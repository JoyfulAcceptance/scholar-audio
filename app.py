#!/usr/bin/env python3
"""Build a local listening packet from a scholarly PDF or text file."""

from __future__ import annotations

import argparse
import html
import math
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple


SECTION_NAMES = {
    "abstract",
    "introduction",
    "background",
    "related work",
    "literature review",
    "methods",
    "method",
    "methodology",
    "materials and methods",
    "results",
    "findings",
    "discussion",
    "limitations",
    "future work",
    "conclusion",
    "conclusions",
    "acknowledgments",
    "acknowledgements",
    "references",
}
HEADING_RE = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?\s+)?(.{2,80})$")
PUNCTUATION_SPACE_RE = re.compile(r"\s+([,.;:!?])")
NUMERIC_CITATION_RE = re.compile(
    r"\s*\[\s*\d+(?:\s*(?:,|[-–])\s*\d+)*\s*\]"
)
AFFILIATION_WORDS = {
    "university", "college", "institute", "laboratory", "lab", "department",
    "school", "center", "centre", "corporation", "inc", "llc", "foundation",
    "research", "press", "journal", "conference", "proceedings",
}
TITLE_SKIP_WORDS = {"a", "an", "and", "the", "toward", "towards"}
PREFERRED_VOICE = "Evan (Enhanced)"
HEADING_MARKER = "[[SCHOLAR_HEADING]] "
MAX_RENDER_WORDS = 1000
TRANSITION_OPENERS = (
    "however", "therefore", "in contrast", "as a result", "for this reason",
    "more importantly", "by comparison", "this means", "the central",
)
TERM_CUES_RE = re.compile(
    r"\b(?:called|known as|defined as|refers to|we call|the term|hereafter)\b",
    re.IGNORECASE,
)
ACRONYM_INTRO_RE = re.compile(r"\b[A-Za-z][A-Za-z -]{3,}\s+\(([A-Z][A-Z0-9-]{1,9})\)")


class ScholarAudioError(RuntimeError):
    """A user-facing pipeline error."""


@dataclass
class Section:
    title: str
    text: str


def run(command: Sequence[str], description: str) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ScholarAudioError(f"Cannot {description}: '{command[0]}' is not installed.") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "unknown error").strip()
        raise ScholarAudioError(f"Could not {description}: {detail}") from exc


def extract_text(source: Path) -> str:
    suffix = source.suffix.lower()
    if suffix in {".txt", ".md"}:
        return source.read_text(encoding="utf-8", errors="replace")
    if suffix != ".pdf":
        raise ScholarAudioError("Input must be a text-based .pdf, .md, or .txt file.")
    if shutil.which("pdftohtml") is None:
        raise ScholarAudioError("PDF extraction requires Poppler. Install it with: brew install poppler")

    with tempfile.TemporaryDirectory(prefix="scholar-audio-") as temp_dir:
        extracted = Path(temp_dir) / "extracted.xml"
        run(
            ["pdftohtml", "-xml", "-hidden", "-nodrm", "-i", str(source), str(extracted)],
            "extract structured PDF text",
        )
        text = structured_pdf_text(extracted)
    if len(re.sub(r"\s", "", text)) < 100:
        raise ScholarAudioError(
            "This PDF contains too little extractable text. It may be scanned; OCR is not in the MVP."
        )
    return text


def structured_pdf_text(xml_path: Path) -> str:
    """Recover PDF reading order and mark standalone bold headings."""
    root = ET.parse(xml_path).getroot()
    pages: List[str] = []
    excluded_headings = {"ccs concepts", "keywords", "acm reference format"}
    shared_fonts: Dict[str, Tuple[float, str]] = {}
    outline_titles = [
        re.sub(r"\s+", " ", "".join(item.itertext())).strip()
        for item in root.findall(".//outline//item")
        if "".join(item.itertext()).strip()
    ]

    def normalized(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip().casefold()

    for page in root.findall("page"):
        page_width = float(page.attrib.get("width", "0") or 0)
        shared_fonts.update({
            item.attrib["id"]: (float(item.attrib.get("size", "0") or 0), item.attrib.get("family", ""))
            for item in page.findall("fontspec")
        })
        fonts = shared_fonts
        nodes = []
        size_weights: Counter[float] = Counter()
        for item in page.findall("text"):
            text = html.unescape("".join(item.itertext())).strip()
            if not text:
                continue
            font_id = item.attrib.get("font", "")
            size, family = fonts.get(font_id, (0.0, ""))
            left = float(item.attrib.get("left", "0") or 0)
            width = float(item.attrib.get("width", "0") or 0)
            top = float(item.attrib.get("top", "0") or 0)
            column = -1 if page_width and left < page_width * 0.45 and left + width > page_width * 0.55 else int(left >= page_width / 2)
            bold = bool(re.search(r"bold|demi|black", family, re.IGNORECASE)) or family.endswith(("TB", "TBI", "TBO"))
            nodes.append((top, column, text, size, bold))
            if size:
                size_weights[size] += len(text)

        body_size = size_weights.most_common(1)[0][0] if size_weights else 0.0
        lines = []
        current = []
        current_top = 0.0
        current_column = -2

        def flush_line() -> None:
            if not current:
                return
            line_text = " ".join(part[0] for part in current).strip()
            total_chars = sum(len(part[0]) for part in current)
            bold_chars = sum(len(part[0]) for part in current if part[2])
            largest_size = max(part[1] for part in current)
            bold_ratio = bold_chars / max(1, total_chars)
            candidate = line_text.rstrip(":")
            numbered = bool(re.match(r"^\d+(?:\.\d+)*\s+\S", candidate))
            heading_shape = (
                1 <= len(candidate.split()) <= 16
                and len(candidate) <= 140
                and not re.search(r"[?!]$", candidate)
                and candidate.lower() not in excluded_headings
            )
            styled_heading = (
                heading_shape
                and bold_ratio >= 0.72
                and (numbered or body_size - 2 <= largest_size <= body_size + 4)
                and (not outline_titles or candidate.lower() in SECTION_NAMES)
            )
            lines.append(f"{HEADING_MARKER}{line_text}" if styled_heading else line_text)
            current.clear()

        for top, column, text, size, bold in nodes:
            if current and (abs(top - current_top) > 4 or column != current_column):
                flush_line()
            if not current:
                current_top = top
                current_column = column
            current.append((text, size, bold))
        flush_line()

        restored_lines: List[str] = []
        index = 0
        while index < len(lines):
            raw_line = lines[index].removeprefix(HEADING_MARKER)
            line_key = normalized(raw_line)
            outline_match = next(
                (title for title in outline_titles if line_key and normalized(title).startswith(line_key)),
                None,
            )
            if outline_match and (re.match(r"^(?:\d|[A-Z]\s)", raw_line) or raw_line.lower() in SECTION_NAMES):
                combined = raw_line
                next_index = index + 1
                while next_index < len(lines):
                    continuation = lines[next_index].removeprefix(HEADING_MARKER)
                    proposed = f"{combined} {continuation}"
                    if not normalized(outline_match).startswith(normalized(proposed)):
                        break
                    combined = proposed
                    next_index += 1
                restored_lines.append(f"{HEADING_MARKER}{outline_match}")
                index = next_index
                continue
            restored_lines.append(lines[index])
            index += 1
        pages.append("\n".join(restored_lines))

    return "\f".join(pages)


def remove_repeated_page_lines(text: str) -> str:
    pages = text.split("\f")
    if len(pages) < 3:
        return text.replace("\f", "\n")
    edge_lines: Counter[str] = Counter()
    page_lines: List[List[str]] = []
    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        page_lines.append(lines)
        for line in lines[:2] + lines[-2:]:
            if 2 < len(line) < 100:
                edge_lines[line] += 1
    threshold = max(3, (len(pages) + 1) // 2)
    repeated = {line for line, count in edge_lines.items() if count >= threshold}
    return "\n\n".join("\n".join(line for line in lines if line not in repeated) for lines in page_lines)


def is_heading(line: str) -> bool:
    candidate = line.strip().rstrip(":")
    if candidate.startswith(HEADING_MARKER):
        return True
    match = HEADING_RE.fullmatch(candidate)
    if not match:
        return False
    name = match.group(1).strip().lower()
    if name in SECTION_NAMES:
        return True
    words = candidate.split()
    letters = sum(char.isalpha() for char in candidate)
    visible = sum(not char.isspace() for char in candidate)
    return (
        1 <= len(words) <= 8
        and candidate.isupper()
        and letters >= 3
        and visible > 0
        and letters / visible >= 0.65
    )


def clean_text(raw: str) -> str:
    text = remove_repeated_page_lines(raw).replace("\u00ad", "")
    text = re.sub(r"(?<=\w)-\n(?=[a-z])", "", text)
    lines = []
    seen_nonempty = False
    for line in text.splitlines():
        markdown_heading = re.match(r"^(#{1,6})\s+(.+)", line.strip())
        cleaned_line = markdown_heading.group(2) if markdown_heading else line
        cleaned_line = re.sub(r"[ \t]+", " ", cleaned_line).strip()
        if markdown_heading and (len(markdown_heading.group(1)) > 1 or seen_nonempty):
            cleaned_line = f"{HEADING_MARKER}{cleaned_line}"
        lines.append(cleaned_line)
        seen_nonempty = seen_nonempty or bool(cleaned_line)
    blocks: List[str] = []
    paragraph: List[str] = []

    def flush() -> None:
        if paragraph:
            joined = " ".join(paragraph)
            joined = NUMERIC_CITATION_RE.sub("", joined)
            blocks.append(PUNCTUATION_SPACE_RE.sub(r"\1", joined))
            paragraph.clear()

    for line in lines:
        if not line:
            flush()
        elif is_heading(line):
            flush()
            blocks.append(line.rstrip(":"))
        elif re.fullmatch(r"\d+", line):
            continue
        else:
            paragraph.append(line)
    flush()
    return "\n\n".join(block for block in blocks if block).strip()


def normalize_title(heading: str) -> str:
    heading = heading.strip().removeprefix(HEADING_MARKER)
    title = re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", heading).rstrip(":")
    return title.title() if title.isupper() else title


def split_sections(text: str) -> List[Section]:
    blocks = text.split("\n\n")
    sections: List[Section] = []
    title = "Opening"
    body: List[str] = []
    for block in blocks:
        if is_heading(block):
            if body:
                sections.append(Section(title, "\n\n".join(body).strip()))
            title = normalize_title(block)
            body = []
        else:
            body.append(block)
    if body:
        sections.append(Section(title, "\n\n".join(body).strip()))
    sections = [section for section in sections if section.text]
    if len(sections) >= 2 and sections[0].title == "Opening" and sections[1].title.lower() == "abstract":
        sections = sections[1:]
    return sections


def safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return name[:60] or "Section"


def pascal_word(word: str) -> str:
    letters = re.sub(r"[^A-Za-z0-9]", "", word)
    if not letters:
        return ""
    if letters.isupper() and len(letters) <= 5:
        return letters
    return letters[0].upper() + letters[1:].lower()


def looks_like_affiliation(line: str) -> bool:
    words = {word.lower().strip(".,") for word in line.split()}
    return bool(words & AFFILIATION_WORDS) or "@" in line


def looks_like_author_line(line: str) -> bool:
    if not 2 <= len(line.split()) <= 20 or len(line) > 180:
        return False
    if any(char in line for char in ":?!") or re.search(r"\b(?:19|20)\d{2}\b", line):
        return False
    if looks_like_affiliation(line):
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", line)
    if len(words) < 2:
        return False
    lowercase = {"and", "de", "del", "der", "di", "la", "van", "von"}
    name_like = sum(word[0].isupper() or word.lower() in lowercase for word in words)
    return name_like / len(words) >= 0.8


def strip_contact_details(line: str) -> str:
    """Remove contact fields that should never be narrated as front matter."""
    cleaned = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "", line)
    cleaned = re.sub(r"\b(?:https?://|www\.)\S+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bORCID\s*:?\s*[\dXx-]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:corresponding\s+author|contact)\s*:?", "", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip(" ,;:-")


def author_label(author_line: str) -> str:
    cleaned = re.sub(r"[\d*†‡]+", "", author_line)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    et_al = re.match(r"^([A-Za-z][A-Za-z'’-]*)\s+et\s+al\.?$", cleaned, re.IGNORECASE)
    if et_al:
        return f"{pascal_word(et_al.group(1))}EtAl"
    parts = [part.strip() for part in re.split(r"\s*(?:;|\band\b|&)\s*|,\s*(?=[A-Z])", cleaned) if part.strip()]
    if not parts:
        return ""
    last_names = []
    for person in parts:
        tokens = re.findall(r"[A-Za-z][A-Za-z'’-]*", person)
        if tokens:
            last_names.append(pascal_word(tokens[-1]))
    if len(last_names) >= 3:
        return f"{last_names[0]}EtAl"
    return "".join(last_names)


def infer_citation_name(source: Path, raw: Optional[str] = None) -> str:
    text = raw if raw is not None else extract_text(source)
    opening = text.split("\f", 1)[0]
    lines = [
        re.sub(r"\s+", " ", re.sub(r"^#{1,6}\s+", "", line)).strip()
        for line in opening.splitlines()
        if line.strip()
    ]
    abstract_index = next((index for index, line in enumerate(lines) if line.rstrip(":").lower() == "abstract"), min(len(lines), 30))
    front = lines[:abstract_index]
    year_match = next((re.search(r"\b((?:19|20)\d{2})\b", line) for line in front if re.search(r"\b(?:19|20)\d{2}\b", line)), None)
    year = year_match.group(1) if year_match else ""

    author_index: Optional[int] = None
    for index in range(len(front) - 1, 0, -1):
        line = front[index]
        if looks_like_affiliation(line) or re.search(r"\b(?:19|20)\d{2}\b", line):
            continue
        if looks_like_author_line(line):
            author_index = index
            break

    if author_index is None or not year:
        return safe_name(source.stem)
    authors = author_label(front[author_index])
    title_text = " ".join(front[:author_index])
    title_words = [
        pascal_word(word)
        for word in re.findall(r"[A-Za-z0-9]+", title_text)
        if word.lower() not in TITLE_SKIP_WORDS
    ][:5]
    short_title = "".join(word for word in title_words if word)
    if not authors or not short_title:
        return safe_name(source.stem)
    return f"{authors}{year}_{short_title}"[:100]


def scaled_pause(base_ms: int, rate: int) -> int:
    factor = max(0.75, min(1.35, math.sqrt(130 / rate)))
    return round(base_ms * factor)


def silence(base_ms: int, rate: int) -> str:
    return f"[[slnc {scaled_pause(base_ms, rate)}]]"


def listening_front_matter(raw: str, rate: int) -> str:
    opening = raw.split("\f", 1)[0]
    lines = [
        re.sub(r"\s+", " ", re.sub(r"^#{1,6}\s+", "", line)).strip()
        for line in opening.splitlines()
        if line.strip()
    ]
    abstract_index = next((index for index, line in enumerate(lines) if line.rstrip(":").lower() == "abstract"), 0)
    front = [strip_contact_details(line) for line in lines[:abstract_index]]
    front = [line for line in front if line]
    if not front:
        return ""
    year_index = next((index for index, line in enumerate(front) if re.search(r"\b(?:19|20)\d{2}\b", line)), None)
    author_index: Optional[int] = None
    for index in range(len(front) - 1, 0, -1):
        if looks_like_affiliation(front[index]) or re.search(r"\b(?:19|20)\d{2}\b", front[index]):
            continue
        if looks_like_author_line(front[index]):
            author_index = index
            break
    if author_index is None:
        return ""
    title = " ".join(front[:author_index]).strip()
    author = front[author_index].strip()
    year = re.search(r"\b((?:19|20)\d{2})\b", front[year_index]) if year_index is not None else None
    pieces = [f"{title}.", silence(400, rate), f"By {author}."]
    if year:
        pieces.extend([silence(300, rate), f"Published in {year.group(1)}."])
    return "\n".join(pieces)


def pace_paragraphs(text: str, rate: int, section_title: str = "") -> str:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    paced: List[str] = []
    seen_acronyms: set[str] = set()
    for index, paragraph in enumerate(paragraphs):
        if index:
            lower = paragraph.lower()
            base = 450 if lower.startswith(TRANSITION_OPENERS) else 300
            if not paced[-1].rstrip().endswith("]]" ):
                paced.append(silence(base, rate))
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", paragraph)
        result_section = section_title.lower() in {"results", "findings"}
        numerical_sentences = sum(bool(re.search(r"\b\d+(?:\.\d+)?%?\b", sentence)) for sentence in sentences)
        result_cluster = result_section and (len(sentences) >= 3 or numerical_sentences >= 2)
        prepared_sentences: List[str] = []
        for sentence_index, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            words = re.findall(r"\b[\w'’-]+\b", sentence)
            introduced = TERM_CUES_RE.search(sentence) is not None
            for acronym in ACRONYM_INTRO_RE.findall(sentence):
                if acronym not in seen_acronyms:
                    introduced = True
                    seen_acronyms.add(acronym)
            very_dense = (
                len(words) >= 50
                or sum(sentence.count(symbol) for symbol in ("•", "=", "⇒", "∑", "→")) >= 2
            )
            dense = very_dense or (
                len(words) >= 36
                or sentence.count(";") >= 2
                or (len(words) >= 25 and sentence.count(",") >= 4)
            )
            relative_rate = 0.77 if very_dense else (0.85 if dense else (0.90 if introduced else 1.0))
            sentence_rate = max(80, round(rate * relative_rate))
            if sentence_rate != rate:
                prepared_sentences.extend([f"[[rate {sentence_rate}]]", sentence, f"[[rate {rate}]]"])
            else:
                prepared_sentences.append(sentence)
            if dense or introduced:
                prepared_sentences.append(silence(550 if very_dense else (500 if dense else 450), rate))
            elif result_cluster:
                prepared_sentences.append(silence(450 if sentence_index == len(sentences) - 1 else 300, rate))
        paced.append("\n".join(prepared_sentences))
    return "\n\n".join(paced)


def prepare_spoken_section(section: Section, rate: int, front_matter: str = "") -> str:
    parts: List[str] = [silence(700, rate)]
    if front_matter and section.title.lower() == "abstract":
        parts.extend([front_matter, silence(700, rate)])
    parts.extend([f"{section.title}.", silence(700, rate), pace_paragraphs(section.text, rate, section.title)])
    return "\n\n".join(parts).strip() + "\n"


def prepare_preview_text(source: Path, rate: int, word_limit: int = 80) -> str:
    raw = extract_text(source)
    sections = split_sections(clean_text(raw))
    if not sections:
        raise ScholarAudioError("No listenable section was found for the sample.")
    section = sections[0]
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", section.text)
    excerpt: List[str] = []
    word_count = 0
    for sentence in sentences:
        words = re.findall(r"\b[\w'’-]+\b", sentence)
        if excerpt and word_count + len(words) > word_limit:
            break
        excerpt.append(sentence.strip())
        word_count += len(words)
        if word_count >= word_limit:
            break
    preview_section = Section(section.title, " ".join(excerpt))
    front_matter = listening_front_matter(raw, rate) if section.title.lower() == "abstract" else ""
    return prepare_spoken_section(preview_section, rate, front_matter)


def available_voices() -> List[str]:
    result = subprocess.run(["say", "-v", "?"], check=True, capture_output=True, text=True)
    voices: List[str] = []
    for line in result.stdout.splitlines():
        match = re.match(r"^(.+?)\s{2,}[a-z]{2}_[A-Z]{2}\s+#", line)
        if match:
            voices.append(match.group(1).strip())
    return voices


def default_voice() -> str:
    voices = available_voices()
    if PREFERRED_VOICE in voices:
        return PREFERRED_VOICE
    if "Samantha" in voices:
        return "Samantha"
    return voices[0] if voices else PREFERRED_VOICE


def render_audio(text_file: Path, audio_file: Path, voice: str, rate: int) -> None:
    if shutil.which("say") is None:
        raise ScholarAudioError("Audio rendering requires macOS and the built-in 'say' command.")
    if shutil.which("ffmpeg") is None:
        raise ScholarAudioError("Audio conversion requires ffmpeg. Install it with: brew install ffmpeg")
    aiff_file = audio_file.with_suffix(".aiff")
    try:
        run(["say", "-v", voice, "-r", str(rate), "-f", str(text_file), "-o", str(aiff_file)], "render speech")
        if not aiff_file.exists() or aiff_file.stat().st_size < 1024:
            raise ScholarAudioError(
                "macOS say did not produce audible output. Check that the selected voice is installed and try again."
            )
        run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(aiff_file), "-c:a", "aac", "-b:a", "128k", str(audio_file)],
            "convert audio to M4A",
        )
        if not audio_file.exists() or audio_file.stat().st_size < 1024:
            raise ScholarAudioError("ffmpeg created an empty audio track.")
    finally:
        aiff_file.unlink(missing_ok=True)


def split_render_chunks(text: str, max_words: int = MAX_RENDER_WORDS) -> List[str]:
    """Split prepared speech at paragraph or sentence boundaries for reliable rendering."""
    if max_words < 1:
        raise ValueError("max_words must be positive")
    units: List[str] = []
    for paragraph in (part.strip() for part in re.split(r"\n\s*\n", text)):
        if not paragraph:
            continue
        if len(paragraph.split()) <= max_words:
            units.append(paragraph)
            continue
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", paragraph) if part.strip()]
        for sentence in sentences:
            words = sentence.split()
            if len(words) <= max_words:
                units.append(sentence)
            else:
                units.extend(" ".join(words[index:index + max_words]) for index in range(0, len(words), max_words))

    chunks: List[str] = []
    current: List[str] = []
    current_words = 0
    for unit in units:
        unit_words = len(unit.split())
        if current and current_words + unit_words > max_words:
            chunks.append("\n\n".join(current))
            current = []
            current_words = 0
        current.append(unit)
        current_words += unit_words
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def render_section_audio(
    text: str,
    text_file: Path,
    audio_file: Path,
    voice: str,
    rate: int,
    progress: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Render bounded internal chunks and expose one final chapter track."""
    chunks = split_render_chunks(text)
    if len(chunks) == 1:
        if progress:
            progress(1, 1)
        render_audio(text_file, audio_file, voice, rate)
        return

    part_texts: List[Path] = []
    part_audio: List[Path] = []
    concat_file = audio_file.with_name(f".{audio_file.stem}_parts.txt")
    try:
        for index, chunk in enumerate(chunks, 1):
            part_text = audio_file.with_name(f".{audio_file.stem}_part_{index:03d}.txt")
            part_track = audio_file.with_name(f".{audio_file.stem}_part_{index:03d}.m4a")
            if index > 1:
                chunk = f"{silence(300, rate)}\n\n{chunk}"
            part_text.write_text(chunk, encoding="utf-8")
            if progress:
                progress(index, len(chunks))
            render_audio(part_text, part_track, voice, rate)
            part_texts.append(part_text)
            part_audio.append(part_track)

        concat_file.write_text(
            "\n".join(f"file '{track.name}'" for track in part_audio) + "\n",
            encoding="utf-8",
        )
        run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", str(concat_file), "-c", "copy", str(audio_file),
            ],
            "join internal chapter chunks",
        )
        if not audio_file.exists() or audio_file.stat().st_size < 1024:
            raise ScholarAudioError("ffmpeg created an empty chapter track.")
    finally:
        concat_file.unlink(missing_ok=True)
        for path in [*part_texts, *part_audio]:
            path.unlink(missing_ok=True)


def audio_duration(audio_file: Path) -> float:
    run_command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]
    try:
        result = subprocess.run(run_command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ScholarAudioError("Could not measure an audio chapter: 'ffprobe' is not installed.") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "unknown ffprobe error").strip()
        raise ScholarAudioError(f"Could not measure audio chapter '{audio_file.name}': {detail}") from exc
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        detail = result.stdout.strip()
        raise ScholarAudioError(
            f"Could not measure audio chapter '{audio_file.name}': "
            f"ffprobe returned an invalid duration{f' ({detail})' if detail else ''}."
        ) from exc


def ffmetadata_escape(value: str) -> str:
    return re.sub(r"([\\;#=])", r"\\\1", value).replace("\n", " ")


def assemble_audiobook(output: Path, source: Path, tracks: List[Tuple[str, Path]]) -> Path:
    if not tracks:
        raise ScholarAudioError("No audio tracks were available for audiobook assembly.")
    concat_file = output / ".audiobook_concat.txt"
    metadata_file = output / ".audiobook_metadata.txt"
    combined_file = output / ".audiobook_audio.m4a"
    citation_name = infer_citation_name(source)
    audiobook = output / f"{citation_name}.m4b"
    try:
        concat_lines = [f"file '{track.name.replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for _, track in tracks]
        concat_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(combined_file)],
            "join audiobook chapters",
        )

        metadata = [";FFMETADATA1", f"title={ffmetadata_escape(citation_name)}", "artist=Scholar Audio"]
        start_ms = 0
        for title, track in tracks:
            duration_ms = max(1, round(audio_duration(track) * 1000))
            end_ms = start_ms + duration_ms
            metadata.extend(
                [
                    "[CHAPTER]",
                    "TIMEBASE=1/1000",
                    f"START={start_ms}",
                    f"END={end_ms}",
                    f"title={ffmetadata_escape(title)}",
                ]
            )
            start_ms = end_ms
        metadata_file.write_text("\n".join(metadata) + "\n", encoding="utf-8")
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(combined_file),
                "-i",
                str(metadata_file),
                "-map_metadata",
                "1",
                "-map_chapters",
                "1",
                "-c",
                "copy",
                str(audiobook),
            ],
            "write audiobook chapters",
        )
        if not audiobook.exists() or audiobook.stat().st_size < 1024:
            raise ScholarAudioError("ffmpeg created an empty audiobook.")
        return audiobook
    finally:
        concat_file.unlink(missing_ok=True)
        metadata_file.unlink(missing_ok=True)
        combined_file.unlink(missing_ok=True)


def write_packet_readme(
    output: Path,
    source: Path,
    voice: str,
    rate: int,
    sections: List[Tuple[str, str]],
    audiobook: Optional[str] = None,
) -> None:
    track_lines = "\n".join(f"{index}. {title} — `{filename}`" for index, (title, filename) in enumerate(sections, 1))
    content = f"""# Scholar Audio Listening Packet

Source: `{source.name}`
Voice: {voice}
Speaking rate: {rate} words per minute

## Complete audiobook

{f'`{audiobook}` — the entire article with embedded chapters.' if audiobook else 'Audio rendering was skipped.'}

## Tracks

{track_lines}

## Listening note

Keep the original paper nearby for charts, tables, equations, footnotes, and images. Automated cleanup is intentionally conservative; check the section text if something sounds unusual.
"""
    (output / "README.md").write_text(content, encoding="utf-8")


def create_packet_archive(output: Path, citation_name: str, files: Sequence[Path]) -> Path:
    archive = output / f"{citation_name}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as packet:
        for file in files:
            packet.write(file, arcname=f"{citation_name}/{file.name}")
    if not archive.exists() or archive.stat().st_size < 1024:
        raise ScholarAudioError("Could not create the downloadable listening packet.")
    return archive


def build_packet(
    source: Path,
    output: Path,
    voice: str,
    rate: int,
    skip_audio: bool,
    progress: Optional[Callable[[int, int, str], None]] = None,
) -> Path:
    if not source.is_file():
        raise ScholarAudioError(f"Input file not found: {source}")
    if output.exists() and any(output.iterdir()):
        raise ScholarAudioError(f"Output folder is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    raw = extract_text(source)
    citation_name = infer_citation_name(source, raw)
    source_copy = output / f"{citation_name}{source.suffix.lower()}"
    if source.resolve() != source_copy.resolve():
        shutil.copy2(source, source_copy)
    cleaned = clean_text(raw)
    if len(cleaned) < 100:
        raise ScholarAudioError("Too little usable text remained after cleanup.")
    sections = split_sections(cleaned)
    if not sections:
        raise ScholarAudioError("No listenable sections were found.")

    (output / "00_full_listening_text.txt").write_text(cleaned + "\n", encoding="utf-8")
    readme_tracks: List[Tuple[str, str]] = []
    audio_tracks: List[Tuple[str, Path]] = []
    front_matter = listening_front_matter(raw, rate)
    width = max(2, len(str(len(sections))))
    for index, section in enumerate(sections, 1):
        stem = f"{index:0{width}d}_{safe_name(section.title)}"
        spoken = prepare_spoken_section(section, rate, front_matter if index == 1 else "")
        text_file = output / f"{stem}.txt"
        text_file.write_text(spoken, encoding="utf-8")
        track_name = f"{stem}.m4a"
        if not skip_audio:
            print(f"Rendering {index}/{len(sections)}: {section.title}")
            if progress:
                progress(index, len(sections), section.title)
            render_section_audio(
                spoken,
                text_file,
                output / track_name,
                voice,
                rate,
                progress=(
                    (lambda part, total, section_title=section.title: progress(
                        index,
                        len(sections),
                        f"{section_title} (part {part} of {total})" if total > 1 else section_title,
                    ))
                    if progress else None
                ),
            )
            readme_tracks.append((section.title, track_name))
            audio_tracks.append((section.title, output / track_name))
        else:
            readme_tracks.append((section.title, text_file.name))
    audiobook = assemble_audiobook(output, source, audio_tracks) if audio_tracks else None
    write_packet_readme(output, source_copy, voice, rate, readme_tracks, audiobook.name if audiobook else None)
    readme = output / "README.md"
    packet_readme = output / "README_listening_packet.md"
    readme.rename(packet_readme)
    if audiobook:
        create_packet_archive(output, citation_name, [source_copy, audiobook, packet_readme])
    if progress:
        progress(len(sections), len(sections), "Complete")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn a scholarly PDF or text file into a local listening packet.")
    parser.add_argument("input", type=Path, nargs="?", help="A text-based PDF, Markdown, or UTF-8 text file")
    chosen_default_voice = default_voice()
    parser.add_argument("--voice", default=chosen_default_voice, help=f"Installed macOS voice (default: {chosen_default_voice})")
    parser.add_argument("--rate", type=int, default=130, help="Speaking rate in words per minute (default: 130)")
    parser.add_argument("--output", type=Path, help="Output folder (default: <input>_listening_packet)")
    parser.add_argument("--skip-audio", action="store_true", help="Create and inspect section text without rendering audio")
    parser.add_argument("--list-voices", action="store_true", help="List installed macOS voices and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.list_voices:
            subprocess.run(["say", "-v", "?"], check=True)
            return 0
        if args.input is None:
            raise ScholarAudioError("Choose an input file, or use --list-voices.")
        if not 80 <= args.rate <= 400:
            raise ScholarAudioError("Speaking rate must be between 80 and 400 words per minute.")
        source = args.input.expanduser().resolve()
        output = (args.output or source.with_name(infer_citation_name(source))).expanduser().resolve()
        packet = build_packet(source, output, args.voice, args.rate, args.skip_audio)
        print(f"Listening packet ready: {packet}")
        return 0
    except (ScholarAudioError, OSError, UnicodeError) as exc:
        print(f"Scholar Audio: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
