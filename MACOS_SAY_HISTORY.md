# The History of macOS `say` and Text-to-Speech

## The short version

Apple's built-in speech lineage is about **42 years old** in 2026. The Macintosh spoke at its January 1984 unveiling.

The precise birthday of the terminal command `/usr/bin/say` is less certain. Surviving documentation confirms it existed by the Mac OS X Panther period, around 2003–2004, making the command itself at least **22 years old**.

But `say` is not one frozen 1980s synthesizer. It is better understood as an old, durable doorway into a collection of speech engines and voice technologies from several different generations.

## Who are the voices?

There are several fundamentally different kinds.

### Synthetic characters

Classic voices such as these were primarily synthesized personalities—not actors recording every word:

- Fred
- Ralph
- Zarvox
- Whisper
- Bells
- Bad News
- Good News
- Bubbles
- Cellos
- Trinoids

Their pitch, formants, timing, excitation, and sound effects were manipulated to create characters. Asking “Who played Zarvox?” is therefore a little like asking who performed a synthesizer preset.

They may contain distant human source material, but the recognizable character is mostly the transformation.

### Recorded-fragment voices

Higher-quality voices such as Agnes, Bruce, and Victoria were created from recorded human speech fragments.

The speaker recorded carefully designed material covering the sound transitions needed by the synthesizer. The computer could then join those fragments into sentences the person had never actually said.

A common building block was the **diphone**: a recording extending from the middle of one speech sound to the middle of the next.

Instead of recording every English word, the system recorded reusable transitions:

```text
text
  → pronunciation
  → phonemes
  → matching recorded fragments
  → joined waveform
```

Apple apparently did not publicly credit most of these performers.

### Evan, Samantha, Alex, and today's voices

These should be treated as product voice identities.

No credible published source was found identifying Evan's performer. The same caution applies to Samantha.

Susan Bennett is credibly identified as the original American Siri voice, but that does **not** prove that she performed the separate macOS voice called Samantha. That connection is repeated online without adequate evidence.

The responsible description is:

> Modern system voices are built from human performances plus substantial synthesis and modeling work; Apple generally does not disclose the performers.

## A short history

### 1984: MacinTalk

At the original Macintosh unveiling, the Mac introduced itself and delivered the line:

> “Never trust a computer you can't lift.”

MacinTalk was developed for Apple by Joseph Katz and Mark Barton, who later founded SoftVoice.

The computer did not contain recordings of all the words it spoke. It converted spelling into phonemes, then produced those phonemes through compact acoustic rules and parameters.

That was necessary because the original Mac had only 128 KB of memory.

The speech was robotic, but the remarkable achievement was that a mass-market personal computer could pronounce arbitrary, previously unseen text in software.

### Early 1990s: Speech Manager

Apple developed several speech engines:

- **MacinTalk 2:** small enough for slower machines
- **MacinTalk 3:** parametric synthesis with many characters and effects
- **MacinTalk Pro:** recorded fragments assembled into more natural speech

The Speech Manager already supported:

- Pronunciation dictionaries
- Phoneme conversion
- Speaking rate
- Pitch
- Pitch modulation
- Volume
- Embedded commands
- Word and phoneme callbacks
- Synchronization markers

Many of the `[[...]]` controls explored by Scholar Audio come from this era. See [Apple's archived Speech Manager contents](https://developer.apple.com/library/archive/documentation/mac/pdf/Sound/Sound_TOC.pdf).

Apple was already warning developers that the original MacinTalk was obsolete by 1990. The technical note was literally titled **“MacinTalk—The Final Chapter.”** See [Archived Apple Technical Note PT22](https://leopard-adc.pepas.com/technotes/pt/pt_22.html).

Apple has therefore been declaring pieces of this system obsolete while preserving its essential idea for decades.

### 2001–2004: Mac OS X and `say`

Mac OS X shipped in 2001. [`say` was documented as a Unix command included with Panther](https://www.macworld.com/article/170907/terminalvoice.html) by 2004.

Apple also provided a separate AppleScript command:

```applescript
say "Hello"
```

See [Apple's archived scripting guide](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/SpeakText.html).

### 2007: Alex

Mac OS X Leopard introduced Alex, designed for natural, intelligible speech at high reading speeds.

Alex included simulated breaths.

The machine obviously did not need to breathe. The breaths helped human listeners perceive phrase boundaries and gave the narration cognitive punctuation. See [Apple's Leopard announcement](https://www.apple.com/newsroom/2007/10/16Apple-to-Ship-Mac-OS-X-Leopard-on-October-26/).

That is particularly relevant to Scholar Audio: something acoustically unnecessary can make dense material cognitively easier to follow.

### 2017: neural assistance in Siri

Apple published a detailed account of using deep learning in Siri's voice. The system was initially hybrid: neural models helped select and smooth recorded speech units instead of replacing the entire pipeline at once. See [Apple Machine Learning Research](https://machinelearning.apple.com/research/siri-voices).

The history is therefore not a neat overnight transition from “spliced recordings” to “AI voices.” Statistical models, human recordings, linguistic rules, unit selection, and neural scoring overlapped.

### Today: Personal Voice and neural generation

Apple's Personal Voice can learn a private synthetic voice from prompted recordings. The voice is produced and stored on-device on supported Apple hardware. See [Apple Personal Voice documentation](https://support.apple.com/en-us/104993).

That is very different from Zarvox or Victoria. Instead of collecting every sound transition manually, a model learns the speaker's acoustic characteristics from examples.

## How did old TTS pronounce unseen words?

The fundamental trick was decomposition.

The computer did not search for a complete recording of “beaver.” It did something resembling:

```text
beaver
  → pronunciation rules
  → phonemes
  → B + EE + V + ER
  → acoustic instructions or reusable speech fragments
  → waveform
```

For an unfamiliar scholarly word, it would:

1. Look for an entry in its pronunciation dictionary.
2. If none existed, apply letter-to-sound rules.
3. Assign phonemes, syllables, and probable stress.
4. Generate or assemble the required speech sounds.
5. Apply pitch, timing, and punctuation rules.

This is why it could pronounce words it had never encountered—and why English could trip it up spectacularly.

Consider:

```text
rough
through
though
thought
```

The spelling patterns are similar, but the pronunciations are not. Hand-built rules need exceptions, and scholarly names, acronyms, Greek terms, and imported words create many more.

## The major generations of text-to-speech

### 1. Formant or rule-based synthesis

```text
text
  → pronunciation rules
  → phonemes
  → pitch/formant/duration instructions
  → waveform
```

It was:

- Tiny
- Fast
- Controllable
- Able to pronounce unlimited new text
- Unmistakably robotic

Many classic Mac character voices came from this world.

### 2. Concatenative synthesis

```text
text
  → linguistic analysis
  → search recorded fragments
  → join and smooth fragments
```

It provided real human timbre but could produce:

- Audible joins
- Awkward changes in tone
- Inappropriate emphasis
- Fragments recorded with incompatible prosody

MacinTalk Pro belonged broadly to this generation.

### 3. Statistical parametric synthesis

The system learned mappings between linguistic features and acoustic parameters:

```text
text features
  → statistical model
  → spectrogram parameters
  → vocoder
```

This was flexible and more compact than enormous recording libraries, but voices could sound smooth, muffled, buzzy, or averaged.

### 4. Neural synthesis

Modern systems learn much more of the conversion from data:

```text
text or phonemes
  → neural language/acoustic model
  → spectrogram or audio representation
  → neural vocoder
  → waveform
```

They can model:

- Speaker identity
- Phoneme duration
- Pitch and energy
- Speaking style
- Emotional tone
- Contextual pronunciation
- Much longer prosodic relationships

WaveNet was a major demonstration that neural waveform generation could surpass leading concatenative and parametric systems in perceived naturalness. See the [WaveNet paper](https://arxiv.org/abs/1609.03499).

FastSpeech explicitly predicts phoneme duration and makes speaking-rate adjustment part of the model. See the [FastSpeech paper](https://arxiv.org/abs/1905.09263).

## Is `say` legacy or modern?

Both.

- `/usr/bin/say` is a legacy-compatible command-line interface.
- The `[[...]]` embedded-command language is legacy.
- `NSSpeechSynthesizer` is deprecated.
- Apple's current developer interface is `AVSpeechSynthesizer`.
- The voice selected through `say` may be old, vendor-produced, Enhanced, Premium, or relatively modern.
- Apple does not publish enough technical detail to say that every Enhanced or Premium voice is fully neural.

The best description is:

> `say` is a legacy-compatible dispatcher into a heterogeneous modern speech system.

That also explains why embedded commands may behave differently across voices. The old grammar remains available, but each voice engine decides what it can actually honor.

## The Scholar Audio connection

The hardest problem is still prosody.

A modern model may produce beautiful audio while misunderstanding:

- Which new term deserves emphasis
- Where a dense thought ends
- When several results form a conceptual list
- Which parenthetical material should recede
- Where the listener needs time to integrate an idea

That is precisely the layer Scholar Audio is building.

Scholar Audio uses a remarkably old, local, accessibility-rooted interface and supplies the document understanding that raw synthesis still does not reliably provide.
