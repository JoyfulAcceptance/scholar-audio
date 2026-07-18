# Scholar Audio Project Plan

## Goal

Build a local Mac tool that converts PDFs/articles into listenable audio packets using macOS native voices.

## MVP

- Local web page with drag-and-drop upload.
- Voice and rate controls.
- PDF/text extraction.
- Basic listening-text cleanup.
- Section splitting.
- `say` rendering.
- `.m4a` output per section.
- Chaptered `.m4b` assembly.
- Two final downloads: audio-only `.m4b`, or a ZIP containing the source, audiobook, and listening-packet README.

## Demo Script

1. Show a dense research paper.
2. Drop it into Scholar Audio.
3. Choose voice and rate.
4. Watch pipeline progress.
5. Optionally play the prepared listening sample on the Mac.
6. Download the complete generated audiobook.
7. Show the PDF-and-audio listening packet.

## Build Priorities

1. Working PDF-to-audio path.
2. Drag-and-drop local interface.
3. Reliable progress display.
4. Listening-text cleanup.
5. Chaptered output.
6. `.m4b` single-file audiobook.
7. Submission verification, documentation, and demo recording.

## Non-Goals For MVP

- Cloud TTS.
- Native Mac App Store package.
- Perfect citation cleanup.
- OCR for scanned PDFs.
- Public hosting of copyrighted source papers.
