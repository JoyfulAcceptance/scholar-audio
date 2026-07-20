# Scholar Audio: To Do and Would Like to Do

Keep the working loop small: prepare one scholarly document locally, create one complete chaptered audiobook, and download it clearly within a three-minute demonstration.

## To do

### Product verification

- [ ] Run a complete interface test with a real, text-based scholarly PDF.
- [ ] Confirm the downloaded audio-only `.m4b` contains the entire article and working chapter markers.
- [ ] Confirm the PDF-and-audio packet contains the citation-named source PDF, matching `.m4b`, and `README_listening_packet.md`.
- [ ] Test Markdown and plain-text input through the complete interface.
- [ ] Confirm scanned PDFs fail with a clear explanation that OCR is not supported.
- [ ] Test generation with Evan Enhanced at the default 130 WPM.
- [ ] Check that section openings, dense passages, new terms, and repeated complex results receive the intended adaptive pacing.
- [ ] Confirm every prepared section begins with `[[slnc 700]]`.

### Voice-command experiments

- [ ] Test `[[emph +]] ... [[emph -]]` with Evan Enhanced.
- [ ] Confirm unsupported embedded commands are ignored silently and are never spoken aloud.
- [ ] Compare emphasis support across the favorite voices.
- [ ] Decide whether emphasis should enter the preparation pipeline or remain experimental.

### Personal Voice experiment

- [ ] Create Gen's Personal Voice in **System Settings → Accessibility → Personal Voice**.
- [ ] Test the completed voice with macOS Live Speech.
- [ ] Check whether the Personal Voice appears in the voices returned by the current Scholar Audio interface.
- [ ] Check whether `/usr/bin/say` can select and render the Personal Voice.
- [ ] If `say` cannot use it, test access through Apple's current `AVSpeechSynthesizer` authorization flow.
- [ ] Determine whether an authorized local app can save Personal Voice output to an audio file.
- [ ] Record the privacy and licensing boundary: the user's own voice, personal use, locally processed, and only shared with explicitly authorized apps.
- [ ] Decide whether Scholar Audio should mention Personal Voice in its About section without presenting it as an MVP dependency.

### Submission materials

- [ ] Choose a public-domain or original sample paper for the repository and demo.
- [ ] Capture clear interface and output-packet screenshots.
- [ ] Tighten setup instructions by testing them from a clean terminal session.
- [ ] Add sample input and representative output information to the README without committing oversized audio unnecessarily.
- [x] Write the thirty-second self-narrating demo and capture plan.
- [ ] Record the public YouTube demo.
- [ ] Explain plainly how Codex and GPT-5.6 helped turn the manual workflow into the local tool.
- [x] Capture the required `/feedback` session ID for the Devpost form: `019f73b7-b84a-73f3-92c9-5577269ebc7c`.
- [ ] Perform a final repository audit for setup, sample data, licensing, privacy language, and reproducibility.
- [x] Push the first working version and `v0.1.0` tag to GitHub.
- [ ] Verify the public repository from a clean browser session.

## Would like to do

These are valuable only after the complete local listening loop and submission materials work reliably.

### Listening preparation

- [ ] Add a conservative pronunciation pass for acronyms, names, scholarly terms, and symbols.
- [ ] Add a user-editable pronunciation dictionary.
- [ ] Explore emphasis for newly introduced terms when the selected voice supports it.
- [ ] Improve detection of conceptual lists outside Results sections.
- [ ] Explore a brief pause between a complex sentence subject and its main predicate.
- [ ] Add clearer treatment for tables, equations, figures, citations, and footnotes.
- [ ] Let users inspect and lightly edit the prepared listening text before rendering.

#### Advanced feature concept: heavy-subject pause

This is a later listening-preparation experiment, not current MVP scope. A sentence with a long or embedded subject can benefit from a small cognitive boundary before its main verb:

```text
A pond that remains wet after rainfall has stopped — carries a kind of ecological memory.
```

Preferred first experiment:

- Add an em dash only to the prepared reading copy; never alter the source document.
- Compare the dash with an explicit short cue such as `[[slnc 100]]` and keep whichever sounds more natural across supported voices.
- Scale an explicit pause from the 130 WPM baseline if the silence cue proves preferable.
- Apply the rule only to a long or structurally complex initial subject, not every long opening phrase.
- Skip insertion when punctuation already creates a useful boundary.
- Collect positive and negative examples before automating the rule.
- If simple heuristics prove brittle, consider a local dependency parser such as spaCy to locate the complete subject and the sentence's main verb.
- Treat any new parser as an optional later dependency; Scholar Audio's current pipeline deliberately remains small.

#### Advanced feature concept: pronunciation dictionary

This is explicitly outside the current MVP. The preferred first version is a local, user-audited “sounds like” dictionary rather than automatic phoneme extraction or a required online lookup.

Proposed interaction:

```text
Pronunciation Dictionary

Term as written:       __________________
Say it like this:      __________________

[ Hear original ]  [ Hear correction ]

Apply to:
(o) This article
( ) Every article

[ Save pronunciation ]
```

Design rules:

- Preserve the source document; apply substitutions only to prepared listening text.
- Let the user enter an ordinary readable respelling, such as `boor-dee-YEU`.
- Preview both the original and corrected versions with the currently selected voice and rate.
- Treat the version that sounds correct through that voice as authoritative.
- Store corrections locally with the written term, spoken form, language, and article/global scope.
- Match complete terms carefully so a correction does not alter text inside unrelated words.
- Keep an optional recording only as a private reference; do not promise automatic phoneme extraction.
- Consider IPA entry later for advanced users and speech engines that reliably support it.
- Consider optional lookups from sources such as Wiktionary or the CMU Pronouncing Dictionary later, with a visible warning that the searched term leaves the Mac.
- Do not require an online pronunciation service or upload the paper.

### Interface

- [ ] Add an About section explaining local processing, privacy, native voices, and optional Personal Voice use.
- [ ] Show which embedded controls each installed voice appears to support.
- [ ] Add a small voice-comparison or capability-testing tool.
- [ ] Improve progress reporting for long papers without adding an in-app audiobook player.
- [ ] Add a friendly output-folder reveal after generation.

### Format and input support

- [ ] Accept TeX source files and common arXiv source bundles.
- [ ] Improve structural extraction from difficult multi-column PDFs.
- [ ] Consider OCR as a later, explicitly optional local component.
- [ ] Add EPUB or HTML article input if it improves real scholarly-reading workflows.

### Future speech engines

- [ ] Follow the staged cross-platform design in [`FUTURE_CROSS_PLATFORM.md`](FUTURE_CROSS_PLATFORM.md).
- [ ] Investigate a local neural TTS adapter while preserving offline document privacy.
- [ ] Keep the macOS native voice path as the free, private default.
- [ ] Consider optional cloud TTS adapters only with explicit user consent, clear document-upload warnings, and suitable audio licensing.
- [ ] Separate the listening-preparation engine from speech rendering so additional engines do not require rewriting document preparation.

## Not for the MVP

- Native Mac App Store packaging
- Audible integration
- A full in-app audiobook player
- Cloud document storage
- Perfect citation parsing
- Support for copyrighted sample papers in the public repository
