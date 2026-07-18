# Scholar Audio

Scholar Audio turns scholarly PDFs and long articles into local, private listening packets using macOS native voices.

The goal is simple: drop in a PDF, choose a voice and pace, and generate a folder containing cleaned listening text, chapter audio tracks, and an audiobook file.

## Why This Exists

Scholarly reading is often dense, time-bound, and physically demanding. Many people need to read while tired, traveling, visually strained, dysregulated, multitasking, or working around attention limits.

Commercial read-aloud services can help, but they often require subscriptions and cloud upload. Scholar Audio explores a lower-friction alternative for Mac users: use the voices already built into macOS and keep source documents local.

## MVP Vision

The hackathon MVP is a local Mac web app:

1. Drop in a PDF or text file.
2. Extract text.
3. Clean line breaks, headers, citation noise, and obvious OCR artifacts.
4. Add title and author information before the abstract when available.
5. Split the text into listenable sections.
6. Render each section using a selected macOS voice and speaking rate.
7. Export chapter tracks and a single audiobook file.
8. Generate a README/listening packet.

## Current Status

The first complete local pipeline and browser interface are working. Scholar Audio accepts text-based PDFs, Markdown, and plain-text files; prepares section text for listening; renders named `.m4a` chapter tracks locally; assembles a chaptered `.m4b`; and offers two clear downloads: the audiobook alone or a ZIP containing the source, audiobook, and listening-packet README.

The underlying workflow has already been tested manually on AI/HCI research papers using:

- PDF and TeX extraction
- listening-text cleanup
- section splitting
- macOS `say`
- Siri Voice 3
- `.m4a` track generation
- `.m4b` audiobook assembly
- metadata tagging
- Google Drive packet organization

This project wraps that working manual pipeline into a repeatable tool.

## Requirements

- macOS
- macOS voices installed in System Settings
- `ffmpeg` for audio conversion and audiobook assembly
- Python 3 for the local app/pipeline

Install the two command-line dependencies with Homebrew:

```bash
brew install poppler ffmpeg
```

## Run the CLI

```bash
python3 app.py paper.pdf --voice "Evan (Enhanced)" --rate 130
```

Scholar Audio uses a shortened citation name such as `EhsanEtAl2026_FutureOfWorkers`. Its primary download is a matching `.zip` listening packet containing the renamed source, a complete chaptered `.m4b` audiobook, and `README_listening_packet.md`. Working section text and audio tracks remain available locally without cluttering the downloadable packet.

Useful options:

```bash
# See the voices installed on this Mac
python3 app.py --list-voices

# Inspect extraction, cleanup, and section splitting without waiting for audio
python3 app.py paper.pdf --skip-audio

# Choose a specific destination
python3 app.py paper.pdf --output /path/to/listening_packet
```

The MVP supports text-based PDFs, Markdown, and plain text. If a PDF is a scan, Scholar Audio explains that OCR is not yet supported. Keep the source paper open while listening for charts, tables, equations, footnotes, and images.

## Listening Pacing

The selected speaking rate is the baseline. Scholar Audio prepares difficult material for the ear by slowing new terms to 90% of that rate, dense sentences to 85%, and very dense sentences to 77%, then explicitly returning to the selected rate. It adds documented macOS `say` silence cues after difficult material and around structural transitions. Pauses scale gently from the 130 WPM baseline using `sqrt(130 / selected_rate)`, constrained to 75–135%.

This pacing system is covered by regression tests in `tests/test_pacing.py`.

Run the complete fast test suite from the repository root:

```bash
python3 -m unittest discover -v
```

The tests do not render real audio.

## Run the Local Interface

```bash
python3 web_app.py
```

Scholar Audio opens at `http://127.0.0.1:8765`. Drop in a PDF, Markdown, or text file, choose a voice and pace, and follow the section-by-section progress. Finished packets stay in the local `output/` folder and are never sent to a cloud service.

## Devpost Framing

Potential tracks:

- Education
- Apps for Your Life
- Work/Productivity
- Developer Tools

Core promise:

> Make scholarly reading portable without sending your documents to a cloud TTS service.

## Attribution

Concept, workflow design, listening experience, and product framing: Genevieve Prentice.

Implementation support: Codex, with technical review/guidance from Bruce Stephenson.
