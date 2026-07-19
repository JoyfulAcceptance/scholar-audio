# Future Direction: Cross-Platform Scholar Audio

## Status

This is a post-competition design note, not part of the current MVP. The release candidate remains a local Mac tool built around macOS `say`.

## Goal

Make Scholar Audio available on macOS, Windows, and Linux without losing its product north star:

> Make scholarly reading listenable without requiring the reader to send documents to a cloud service.

The cross-platform version should preserve the same small working loop: choose a document, select a locally available voice and pace, preview the prepared reading, and download one complete chaptered audiobook.

## What should remain shared

The listening-preparation engine is the core of Scholar Audio and should not depend on an operating system. A shared Python package should continue to handle:

- PDF, Markdown, and plain-text ingestion
- conservative text cleanup
- scholarly section recovery
- title and author context
- named chapter creation
- detection of new terms and dense passages
- adaptive pacing decisions
- shortened citation filenames
- packet structure and listening README generation

Instead of placing macOS `say` commands directly into the prepared text, the shared engine should produce an intermediate listening plan. Each passage would describe its text, relative speaking rate, pause before or after, and chapter membership. A platform-specific renderer would translate that plan into the controls supported by its speech engine.

## Proposed architecture

```text
Document
   ↓
Shared extraction and cleanup
   ↓
Shared listening plan
   ├── chapter title
   ├── spoken text
   ├── relative rate
   └── pause timing
   ↓
Local speech-engine adapter
   ├── macOS: say or AVSpeechSynthesizer
   ├── Windows: installed Windows voices
   └── Linux: selected local speech engine
   ↓
Shared FFmpeg assembly and packet creation
   ↓
Chaptered .m4b and listening packet
```

## Platform adapters

### macOS

Keep the existing `say` renderer as the first supported adapter because it is free, already working, and exposes installed system voices. Later investigation may compare it with `AVSpeechSynthesizer`, particularly for Personal Voice access and newer Apple speech behavior.

### Windows

Add an adapter for voices available through current Windows speech APIs. The first research task is to determine which installed voices can be rendered to an audio file locally, which rate and pause controls they support, and whether those controls behave consistently across Windows versions.

### Linux

Select one well-maintained local engine as the documented default rather than attempting to support every speech system. The adapter must be able to enumerate voices, render to an audio file, and honor enough pacing information to preserve the listening experience. Additional engines could be added later behind the same interface.

## Interface options

The current local browser interface can remain shared if each platform has a small launcher that starts the local server and opens the page. Native application packaging may be considered later, but it should not precede a working cross-platform command-line pipeline.

The interface should show only voices that the active renderer can actually use to create downloadable audio. It should continue to offer:

- voice selection
- baseline speaking rate
- a document-specific preview
- one complete audiobook download
- one source-and-audio packet download

## Privacy boundary

Offline processing remains the default requirement. The application should clearly identify whether an installed engine operates entirely on the device. Optional cloud speech engines may be considered only as separate adapters with explicit consent, clear upload warnings, and no silent fallback from local to cloud processing.

## Main technical risk

Speech engines do not interpret pacing controls uniformly. A literal `[[slnc 700]]` command is specific to the current Mac path, and punctuation may produce different results in different voices. The shared listening plan must therefore express intent—such as a 700-millisecond boundary or a passage at 85 percent of baseline—while each adapter implements and tests the closest supported behavior.

Audio quality should be evaluated by listening, not merely by confirming that a file was produced. Each supported adapter needs a small common test paper containing ordinary prose, new terms, dense sentences, repeated complex findings, acronyms, and section transitions.

## Smallest cross-platform development sequence

1. Separate listening preparation from macOS command generation.
2. Define and test the intermediate listening-plan format.
3. Preserve the existing Mac renderer as the reference implementation.
4. Build one Windows or Linux command-line renderer.
5. Run the common listening paper through both platforms and compare the results.
6. Add platform-aware voice discovery to the local interface.
7. Package launchers only after the command-line loop works reliably.

## Success standard

Cross-platform Scholar Audio succeeds when a reader on each supported operating system can process the same sample paper locally and receive a complete, named, chaptered audiobook with recognizably consistent pacing—without creating an account or uploading the paper.
