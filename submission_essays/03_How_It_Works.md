# How Scholar Audio Works

## Writing prompt

Describe the working pipeline plainly enough that a judge can understand the technical accomplishment without reading the code.

## Ideas to consider

1. Extract text locally with `pdftotext`, or read Markdown/plain text directly.
2. Clean PDF artifacts conservatively.
3. Recover common scholarly sections.
4. Insert title and author context before the abstract when available.
5. Detect new terms, dense sentences, very dense sentences, and clusters of complex Results findings.
6. Adjust rate and pauses relative to the user’s selected baseline.
7. Render each section with macOS `say`.
8. Convert and assemble audio with FFmpeg into named tracks and a chaptered audiobook.
9. Package the result using a shortened scholarly citation filename.

## Draft

Scholar Audio uses a local pipeline to turn a document into material prepared specifically for listening. For a text-based PDF, it begins by extracting the text with `pdftotext`. It can also read Markdown and plain-text files directly. The extracted text is cleaned conservatively to remove repeated headers, broken line endings, citation noise, and other common document artifacts without attempting to rewrite the author's argument.

The program then identifies common scholarly sections such as Abstract, Introduction, Methods, Results, Discussion, and Conclusion. When the document provides enough information, Scholar Audio places the title and author context before the abstract. These sections later become named chapters, rather than anonymous pieces of audio.

The central listening-preparation step examines the text for newly introduced terms, dense sentences, very dense sentences, and clusters of complex findings. Scholar Audio adds pauses around structural transitions and difficult material. It also temporarily slows demanding passages relative to the reader's selected baseline: new terms are read at 90 percent of the chosen speed, dense sentences at 85 percent, and very dense sentences at 77 percent. The pauses scale gently with the selected speed, and the reading rate returns to the user's choice after each adjusted passage.

Each prepared section is saved as a reading copy and rendered locally with the selected macOS `say` voice. FFmpeg converts the recordings into named chapter tracks and joins them into one `.m4b` audiobook with embedded chapter markers. Finally, Scholar Audio gives the result a shortened citation name based on the paper's author, year, and title. The reader can download either the complete audiobook alone or a listening packet containing the audiobook, original document, and a short README.

The entire document-processing and speech-rendering workflow takes place on the reader's Mac. The paper does not need to be uploaded to a cloud text-to-speech service.
