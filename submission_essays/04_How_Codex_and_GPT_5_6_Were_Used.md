# How Codex and GPT-5.6 Were Used

## Writing prompt

Explain what you contributed, what Codex contributed, and how the collaboration turned a tested manual workflow into a repeatable local product. Be specific about decisions and artifacts rather than saying only that AI “helped with coding.”

## Ideas to consider

- Translating the manual PDF-to-audiobook workflow into a Python pipeline
- Inspecting outputs and listening together before changing pacing rules
- Building the local browser wrapper without a cloud backend
- Developing and testing adaptive pacing for new terms, dense content, and repeated Results complexity
- Turning user observations into regression tests
- Auditing download behavior, voice discovery, packet structure, and failure handling
- Researching Apple `say`, embedded commands, voice history, and Personal Voice boundaries
- Maintaining a practical MVP boundary while recording later ideas in the TODO
- Using Git history and the primary Codex session as evidence of the Build Week process

## Draft

I did not begin Build Week with a blank prompt. Before the competition, I had already developed and tested a manual workflow for turning scholarly papers into locally generated audiobooks. I had used Codex to help extract text, prepare reading copies, divide papers into sections, add pacing cues, render Mac voices, and assemble chaptered audio. That work established both the reader's problem and the central product insight: reading with the ears requires more preparation than sending raw extracted text to a voice.

I began the competition project with a detailed collaboration prompt. It described the tired reader, the existing manual workflow, the privacy goal, the smallest viable product, the three-minute demonstration standard, and the features that should remain outside the MVP. It also told Codex how I wanted to work: start with the problem, show progress through concrete artifacts, explain changes in plain language, and pause when a choice could affect submission quality. During the project I moved Codex between Generator and Auditor roles, asking it either to implement a decision or to step back and evaluate the result.

My Codex setup includes durable memory, interaction guidance, and role separation (Auditor and Generator). It preserves important project decisions and corrections, helps maintain continuity across sessions, and allows me to distinguish between generating work and auditing it. That meant the project's context and lessons did not have to be reconstructed each time. I also installed the Devpost Hackathons plugin so that Build Week requirements, judging guidance, and submission steps were available within the same working environment. I treated the plugin as guidance and verified competition-critical details against the official rules.

Bruce Stephenson served as a human advisor. He reviewed the GitHub, challenged me to control scope, prompted a safe code-cleanup review, and reminded me that a working submission mattered more than chasing every possible improvement. Near the deadline, he asked the decisive question: "Have you written the essays?" He also reminded me that I could submit a working version early, continue improving it until the deadline, and return to longer-term ideas after the competition.

My role throughout was product owner, workflow designer, listener, and final decision-maker. Codex and GPT-5.6 served as implementation, research, drafting, and auditing partners. Codex translated the manual process into a Python command-line pipeline and then a local browser interface. It inspected generated text and audio artifacts, researched the behavior and limits of macOS `say`, built download packaging and voice discovery, added tests, documented later ideas, and maintained the repository. I decided what the product should do and judged whether its output was actually comfortable to hear.

The adaptive pacing system shows the collaboration most clearly. Codex first generated a working reading copy and audio file. I listened closely, identified where sections collided or dense results became exhausting, and described what I heard in ordinary language. Codex translated those observations into repeatable rules for section-opening pauses, new terms, dense sentences, changing speech rates, and clusters of complex findings. We rendered the material again, listened again, and kept the changes that improved the experience. What began as a manual sequence became a tested local product through this cycle of generation, listening, judgment, and revision.
