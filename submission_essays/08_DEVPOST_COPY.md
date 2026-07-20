# Scholar Audio — Devpost Submission Copy

## Project name

Scholar Audio

## Tagline

Turn dense scholarly papers into private, chaptered audiobooks on your Mac.

## Track

Education

## Repository

https://github.com/JoyfulAcceptance/scholar-audio

## Demo video

https://youtu.be/1JbygVl-S9c

## Primary Codex `/feedback` session ID

019f73b7-b84a-73f3-92c9-5577269ebc7c

## Inspiration

Heavy-duty reading can be difficult when several articles and unfamiliar concepts must be absorbed at once. Sometimes my eyes simply need a rest, so I began looking for a way to listen to scholarly papers without paying for another service or uploading private documents to the cloud.

Before Build Week, I tested a manual workflow using tools already available on my Mac. I extracted text, divided papers into meaningful sections, added pacing cues, rendered audio, and assembled chaptered audiobooks. The experiments worked, but producing each audiobook required many separate steps. Scholar Audio grew from the idea that this process could become one simple, repeatable local tool.

## What it does

Scholar Audio turns a text-based PDF, Markdown file, or plain-text article into a complete, chaptered `.m4b` audiobook. The reader drops in a document, chooses an installed Mac voice and speaking pace, and can prepare a short sample from the document before starting the full render.

Scholar Audio cleans common extraction artifacts, recovers scholarly sections, and prepares the text for listening. It adds breathing room around structural transitions, new terms, dense sentences, acronyms, numerical findings, and clusters of complex Results statements. Sections such as Abstract, Introduction, Methods, Results, Discussion, and Conclusion become named audiobook chapters.

The reader can download the audiobook alone or a listening packet containing the audiobook, the citation-named original document, and a short README. Everything runs locally on the Mac; the paper is not sent to a cloud text-to-speech service.

## How it works

For PDFs, Scholar Audio extracts text locally with `pdftotext`; it reads Markdown and plain text directly. A Python pipeline removes repeated headers, broken line endings, citation noise, contact information, and other obvious artifacts while preserving the author's argument. It identifies common scholarly headings and inserts available title, author, and publication-year context before the abstract.

The adaptive pacing pass changes pauses and speech rates relative to the reader's chosen baseline. Newly introduced terms are read at 90 percent of the baseline, dense sentences at 85 percent, and very dense sentences at 77 percent. Acronyms and quantitative expressions receive their own listening treatment, and repeated complex findings gain extra separation.

Each prepared section is rendered with the selected macOS `say` voice. FFmpeg converts the recordings into named `.m4a` tracks and assembles them into a single `.m4b` audiobook with embedded chapter markers. The output receives a short citation-style name based on the paper's author, year, and title.

## How I used Codex and GPT-5.6

I entered Build Week with the reader's problem and a tested manual workflow, then used Codex and GPT-5.6 to turn that workflow into a working product. My starting prompt defined the privacy goal, the tired-reader use case, the MVP boundary, and a three-minute demo standard. My Codex setup included durable memory, interaction guidance, and separate Generator and Auditor roles.

I served as product owner, workflow designer, listener, and final decision-maker. Codex and GPT-5.6 served as implementation, research, drafting, and auditing partners. They helped build the Python command-line pipeline and local browser interface, research macOS `say`, implement packet downloads and voice discovery, create regression tests, document the project, and keep advanced ideas outside the MVP.

The pacing system shows the collaboration most clearly. Codex generated prepared text and audio; I listened and described where sections collided, voices produced artifacts, or dense Results passages became exhausting. GPT-5.6 helped reason about those listening problems, and Codex converted our decisions into repeatable pacing rules and tests. We rendered, listened, revised, and kept the changes that made the paper easier to follow.

Bruce Stephenson provided human code review and scope advice throughout the project.

## What changed during Build Week

Before Build Week, Scholar Audio existed as a manual, multi-step experiment. During the submission period, that workflow became the working software in the repository: a repeatable Python pipeline, support for PDF/Markdown/text input, structure recovery, adaptive pacing, local voice rendering, chaptered `.m4b` assembly, citation-style packet naming, a local drag-and-drop interface, document-specific previews, two simple download options, automated tests, sample data, and complete setup documentation.

The Git history and primary Codex session document this development period.

## Challenges and learning

The hardest problem was not producing speech; it was preparing scholarly prose for the ear. PDF extraction preserves words more readily than structure, and a natural-sounding voice can still rush through unfamiliar terms, acronyms, numerical results, or several complex findings in succession. Listening tests proved more useful than theoretical polishing. Each audible failure became a small rule, and important fixes became regression tests.

The second challenge was scope. A pronunciation dictionary, deeper grammatical parsing, cross-platform neural voices, OCR, and richer playback would all be valuable. Keeping them outside the MVP made it possible to ship a working private tool instead of a polished theory.

## Accomplishments

- A complete local document-to-audiobook loop
- Named chapters in one portable `.m4b` file
- Adaptive pacing designed for dense scholarly prose
- Document-specific voice and speed previews
- Private processing with no cloud TTS dependency
- A focused interface that can be demonstrated clearly in under three minutes
- 23 passing automated tests

## What comes next

Near-term work will refine compatibility across different installed Mac voices and improve handling of difficult PDFs, names, equations, tables, figures, and citations. Later possibilities include a user-editable local pronunciation dictionary, optional local grammatical analysis, TeX and arXiv source-bundle input, careful Personal Voice testing, and a cross-platform local speech backend that preserves the project's privacy promise.

## Built with

Python, macOS `say`, FFmpeg, `pdftotext`, HTML, CSS, JavaScript, Codex, and GPT-5.6.

## Final pre-submit checklist

- [ ] Commit and push the demonstrated code and sample paper
- [ ] Confirm the GitHub repository is public
- [x] Upload `ScholarAudioDemo.mov` to YouTube
- [x] Set the YouTube video to **Public**
- [x] Confirm the YouTube runtime is under three minutes and audio is clear
- [x] Replace the demo placeholder above with the public YouTube URL
- [ ] Confirm the `/feedback` session ID above is the primary build session
- [ ] Paste the relevant sections into Devpost
- [ ] Select the **Education** track
- [ ] Preview the Devpost entry and test every link while logged out
- [ ] Submit before Tuesday, July 21, 2026 at 5:00 PM PT
