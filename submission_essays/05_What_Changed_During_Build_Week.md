# What Changed During Build Week

## Writing prompt

State clearly what existed before the submission period and what was newly built or meaningfully extended during Build Week.

## Before Build Week

- A tested manual workflow for extraction, cleanup, section splitting, macOS voice rendering, pacing adjustments, audio conversion, audiobook assembly, metadata, and packet organization
- Listening experience and product insight developed through real scholarly-reading practice

## Built or extended during Build Week

### Working product

- Turned the manual sequence into a repeatable Python command-line pipeline
- Added input support for text-based PDFs, Markdown files, and plain-text files
- Added local PDF extraction with `pdftotext` and conservative cleanup of common PDF artifacts
- Recovered common scholarly sections and produced contextually named chapter tracks
- Inserted available title, author, and publication-year context before the abstract
- Rendered each prepared section through the Mac's installed `say` voices
- Converted section recordings to `.m4a` tracks with FFmpeg
- Assembled the entire article into one `.m4b` audiobook with embedded chapter markers
- Created shortened citation-style filenames and listening-packet folder names
- Produced a packet README and copied the citation-named original document into the packet
- Added two clear downloads: the audiobook alone, or a ZIP containing the audiobook, original document, and listening README

### Listening preparation and pacing

- Made 130 words per minute the default baseline for dense scholarly material
- Added a 700-millisecond opening pause to every prepared section
- Added pauses around section headings, new concepts, dense transitions, and difficult sentences
- Added variable speech rates relative to the user's selected baseline
- Set introduced terms to 90 percent, dense sentences to 85 percent, and very dense sentences to 77 percent of the selected rate
- Scaled pauses gently when the user selects a different baseline speed
- Detected clusters of repeated complex findings, especially list-like Results passages, and added extra breathing room between them
- Created and repeatedly rendered a fictional beaver paper containing every major section and varying levels of conceptual density
- Compared prepared reading copies with generated audio and refined the rules through listening rather than text inspection alone

### Local interface

- Built a local browser wrapper around the command-line pipeline without adding a cloud backend
- Replaced the initial utility interface with a simplified Scholar Audio page centered on a scroll-and-quill document drop area
- Added drag-and-drop and file-selection controls
- Added installed-voice selection and a speaking-rate control
- Defaulted the interface to Evan (Enhanced) at 130 words per minute when available
- Made the voice dropdown automatically speak a sample sentence whenever a new voice is selected, using the currently selected speaking pace
- Kept access to all compatible installed voices while making preferred voices easier to explore
- Added a document-specific 30-second listening preview before full audiobook generation
- Added preview playback through the Mac and a clear primary **Create audio** action
- Added progress and completion states for the longer local rendering process
- Refreshed the available voice list so newly downloaded `say`-compatible Mac voices, including Jamie, can appear without stale browser data

### Testing, hardening, and documentation

- Added safeguards for missing tools, unavailable voices, empty audio, invalid rates, and failed rendering
- Audited packet structure, download behavior, voice discovery, citation naming, and failure handling
- Added automated tests for adaptive pacing and downloadable packet contracts
- Performed a safe cleanup pass without changing intended behavior
- Created public sample documents for testing without including copyrighted scholarly papers
- Expanded the README with setup, supported inputs, voice-download guidance, privacy behavior, output structure, and pacing details
- Researched and documented the macOS `say` command, its embedded speech commands, and its limitations
- Researched and documented the history of Mac text-to-speech, modern alternatives, and Personal Voice boundaries
- Created a prioritized TODO and advanced-feature list, including Personal Voice testing and a future pronunciation dictionary
- Documented a short demo-capture plan in which Scholar Audio's generated narration explains the product while it is shown
- Committed, tagged, and pushed the first working version, followed by cleanup and downloaded-voice improvements

## Draft
