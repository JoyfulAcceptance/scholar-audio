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

Pre-alpha. This repo is being prepared for OpenAI Build Week / Devpost.

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

