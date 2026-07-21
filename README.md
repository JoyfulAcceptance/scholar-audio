# Scholar Audio

Scholar Audio turns scholarly PDFs and long articles into local, private listening packets using macOS native voices.

The goal is simple: drop in a PDF, choose a voice and pace, and generate a folder containing cleaned listening text, chapter audio tracks, and an audiobook file.

[![Scholar Audio demo](https://img.youtube.com/vi/1JbygVl-S9c/0.jpg)](https://www.youtube.com/watch?v=1JbygVl-S9c)

*Watch the 2-minute, 42-second self-narrated demonstration.*

## Quick Start

Scholar Audio requires macOS, Python 3.9 or newer, Poppler, and FFmpeg.

```bash
brew install poppler ffmpeg
git clone https://github.com/JoyfulAcceptance/scholar-audio.git
cd scholar-audio
python3 web_app.py
```

Then open `http://127.0.0.1:8765` and drop in a file from `sample_data/`.

## Built for OpenAI Build Week

Scholar Audio was created during OpenAI Build Week, July 13–21, 2026. It is the first software application I have built. Before Build Week, I had worked extensively with Codex as a research, writing, and project collaborator, but I was not a programmer and had never translated an idea into working software.

Before Build Week, I had tested a manual, multi-step process for turning scholarly papers into local audiobooks. I approached the build as product owner, workflow designer, listening tester, and final decision-maker. I described problems and desired behavior in ordinary language, evaluated each result, and directed revisions. Codex and GPT-5.6 translated that process into the Python pipeline, adaptive pacing system, local browser interface, audiobook packaging, and automated tests. The repository history documents that development period.

## Why This Exists

Scholarly reading usually means sitting still in front of a page or screen. Scholar Audio lets readers continue through the prose while walking or resting their eyes—then return to the original document for charts, equations, tables, and images.

Unlike many commercial read-aloud services, Scholar Audio uses voices already installed on the Mac and keeps source documents local.

## What Scholar Audio Does

Scholar Audio accepts text-based PDFs, Markdown, and plain-text files. It extracts the document locally, cleans common PDF artifacts, adds available title and author context, and recovers scholarly sections such as Abstract, Introduction, Methods, Results, Discussion, and Conclusion.

The listening-preparation pass adds adaptive pacing around new terms, acronyms, numerical findings, dense sentences, structural transitions, and clusters of complex results. The selected voice and speaking rate remain under the reader's control.

Scholar Audio renders named `.m4a` chapter tracks with macOS `say` and assembles the complete article into a chaptered `.m4b` audiobook. The reader can download either the audiobook alone or a citation-named ZIP containing the source document, audiobook, and listening-packet README. Prepared text and working chapter files remain available locally in the output folder.

## System Requirements and Tested Environment

Scholar Audio runs locally on macOS. Document extraction, listening preparation, speech rendering, and audiobook assembly do not require a cloud text-to-speech service or an ongoing subscription.

### Tested environment

- **Hardware:** Apple M1 MacBook Pro with 16 GB unified memory
- **Operating system:** macOS Tahoe 26.3
- **Speech engine:** Native macOS `/usr/bin/say`
- **Python:** Python 3.9 or newer
- **System dependencies:** Poppler (`pdftotext`) and FFmpeg

Install the command-line dependencies with Homebrew:

```bash
brew install poppler ffmpeg
```

Scholar Audio may work on other Macs capable of running these dependencies, but the current release was developed and tested on the environment listed above.

### Add more Mac voices

Scholar Audio can use additional voices that you download through macOS:

1. Open **System Settings**.
2. Choose **Accessibility**, then **Live Speech**.
3. Click the information button beside the voice setting.
4. Preview and download any voices you would like to use.
5. Return to Scholar Audio and reopen the Voice menu. The app refreshes the installed voice list when its window regains focus.

Only voices that macOS exposes to its local `say` tool can render downloadable Scholar Audio files. **Evan (Enhanced)** is the default when installed, and **Jamie (Premium)** produced strong results during demonstration testing. Downloaded compatible voices remain on the Mac and require no document upload or cloud TTS account.

To see which voices can generate Scholar Audio files, run:

```bash
say -v '?'
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

Scholar Audio supports text-based PDFs, Markdown, and plain-text files. It cannot yet extract words from scanned or image-only PDFs. Because charts, tables, equations, footnotes, and images may not translate well to speech, keep the original document available while listening.

## Listening Pacing

The selected speaking rate is the baseline. Scholar Audio prepares difficult material for the ear by slowing new terms to 90% of that rate, dense sentences to 85%, and very dense sentences to 77%, then explicitly returning to the selected rate. It adds documented macOS `say` silence cues after difficult material and around structural transitions. Pauses scale gently from the 130 WPM baseline using `sqrt(130 / selected_rate)`, constrained to 75–135%.

This pacing system is covered by regression tests in `tests/test_pacing.py`.

Run the complete fast test suite from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests do not render real audio.

## Run the Local Interface

```bash
python3 web_app.py
```

Scholar Audio opens at `http://127.0.0.1:8765`. Drop in a PDF, Markdown, or text file, choose a voice and pace, and follow the section-by-section progress. Finished packets stay in the local `output/` folder and are never sent to a cloud service.

## OpenAI Build Week Submission

**Track:** Education

Core promise:

> Make scholarly reading portable without sending your documents to a cloud TTS service.

## How This Was Built with Codex and GPT-5.6

I began with the reader's problem, a tested manual workflow, and a detailed collaboration prompt defining the privacy goal, MVP boundary, and three-minute demonstration standard. My Codex setup included durable memory, interaction guidance, and separate Generator and Auditor roles.

I served as product owner, workflow designer, listener, and final decision-maker. GPT-5.6 helped reason through the listening experience—most visibly the adaptive pacing rules for new terms, dense sentences, and repeated complex findings. Codex translated those decisions into working Python, tests, documentation, and a local browser interface. I also had the advice, guidance, and code review of my teammate Bruce Stephenson.

The pacing system emerged through an iterative listening process. Codex generated prepared text and audio; I listened, identified where sections collided or difficult passages became exhausting, and described those problems in ordinary language. Codex converted my observations into repeatable rules, and I judged the revised recordings.

Scholar Audio does not call a cloud AI service at runtime. Codex and GPT-5.6 were development collaborators; document extraction, listening preparation, and speech rendering remain local to the reader's Mac.
