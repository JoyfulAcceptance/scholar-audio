# macOS `say` Command Reference

The macOS `say` system has two control layers:

1. Terminal options such as voice, rate, and output format.
2. Commands embedded inside the text, such as `[[slnc 700]]`.

Apple still documents the speech-command delimiter as `[[ ... ]]`, but the underlying `NSSpeechSynthesizer` system is deprecated. Some legacy commands may behave differently—or be ignored—by modern Enhanced voices.

Sources: [NSSpeechSynthesizer documentation](https://developer.apple.com/documentation/appkit/nsspeechsynthesizer), [embedded-command delimiter](https://developer.apple.com/documentation/appkit/nsspeechsynthesizer/speechpropertykey/commanddelimiter), and the [archived Apple Sound documentation](https://developer.apple.com/library/archive/documentation/mac/pdf/Sound/Sound_TOC.pdf).

## Quick reference: voice-dependent controls

These embedded commands are promising but may be honored differently by different macOS voices. In particular, `[[emph +]] ... [[emph -]]` is worth testing as an optional Scholar Audio enhancement: leaving it in the prepared text is harmless when a voice ignores it, provided testing confirms that the command itself is not spoken aloud.

| Command | Brief gloss |
|---|---|
| `[[volm VALUE]]` | Set speaking volume from this point forward. |
| `[[pbas VALUE]]` | Set the voice's baseline pitch. |
| `[[pmod VALUE]]` | Set the amount of pitch variation or expressiveness. |
| `[[emph +]]` | Begin emphasizing the following word or passage. |
| `[[emph -]]` | End emphasis and return to ordinary delivery. |
| `[[char LTRL]]` | Read characters literally or individually. |
| `[[char NORM]]` | Return to normal character interpretation. |
| `[[nmbr LTRL]]` | Read a number digit by digit: `12` becomes “one two.” |
| `[[nmbr NORM]]` | Read digits as a number: `12` becomes “twelve.” |

Example emphasis pair:

```text
This study introduces [[emph +]] ecological latency [[emph -]], a measure of delayed habitat response.
```

## Current `say` terminal commands

These options are documented in the `say` manual installed on macOS.

### Basic use

```bash
say "Text to speak"
say -v "Evan (Enhanced)" -r 130 "Text to speak"
```

| Option | Meaning |
|---|---|
| `say "text"` | Speak supplied text |
| `-f FILE` | Read text from a file |
| `--input-file=FILE` | Long form of `-f` |
| `-f -` | Read text from standard input |
| `-v VOICE` | Select a voice |
| `--voice=VOICE` | Long form of `-v` |
| `-v '?'` | List installed voices |
| `-r RATE` | Speaking rate in words per minute |
| `--rate=RATE` | Long form of `-r` |
| `-o FILE` | Write speech to an audio file |
| `--output-file=FILE` | Long form of `-o` |
| `--progress` | Show synthesis progress |
| `-i` | Interactive highlighting while speaking |
| `--interactive` | Long form of `-i` |

Apple notes that supported rate ranges depend on the particular synthesizer and voice. See [Apple's speech-rate documentation](https://developer.apple.com/documentation/appkit/nsspeechsynthesizer/speechpropertykey/rate).

### Audio destination

```bash
say -a '?'
say -a "MacBook Pro Speakers" "Testing"
```

| Option | Meaning |
|---|---|
| `-a ID` | Use an audio device by numerical ID |
| `-a NAME` | Use an audio device by name |
| `--audio-device=DEVICE` | Long form |
| `-a '?'` | List available audio devices |

### Network speech

| Option | Meaning |
|---|---|
| `-n NAME` | Send speech over the network |
| `-n NAME:PORT` | Send to a named destination and port |
| `-n :PORT` | Send using the specified port |
| `-n :` | Use default network settings |
| `--network-send=...` | Long form |

This is an older macOS capability and is not relevant to Scholar Audio.

### Output format controls

```bash
say -o sample.aiff "Testing"
say -o sample.m4a --file-format=m4af --data-format=aac "Testing"
```

| Option | Meaning |
|---|---|
| `--file-format=FORMAT` | Choose the output container |
| `--file-format=?` | List supported file containers |
| `--data-format=FORMAT` | Select codec or PCM format |
| `--data-format=?` | List supported data formats |
| `--channels=NUMBER` | Select output channel count |
| `--bit-rate=RATE` | Select compressed-audio bitrate |
| `--bit-rate=?` | List supported bitrates |
| `--quality=0-127` | Set conversion quality |

Recognized compressed data-format identifiers include:

```text
aac
alac
```

PCM identifiers can combine:

```text
BE or LE       byte order
F              floating point
I              signed integer
UI             unsigned integer
8/16/24/32/64  sample size
@RATE          sample rate
/FLAGS         hexadecimal flags
```

Examples:

```text
LEI16@44100
BEF32@48000
```

### Interactive highlighting

```bash
say --interactive "Text to speak"
say --interactive=green "Text to speak"
say --interactive=green/black "Text to speak"
```

The markup value can be a terminal capability such as `smso`, a foreground color, or a foreground/background pair such as `green/black`.

## Embedded text commands

Commands are inserted directly into the source document:

```text
This is ordinary speech. [[slnc 700]] This follows a pause.
```

### Silence

```text
[[slnc 700]]
```

Adds silence in milliseconds.

```text
[[slnc 250]]   short pause
[[slnc 500]]   medium pause
[[slnc 700]]   section opening
[[slnc 1000]]  strong transition
```

This is the most dependable pacing command for Scholar Audio and is explicitly demonstrated in the current `say` manual.

### Speaking rate

```text
[[rate 105]]
Dense passage spoken more slowly.
[[rate 130]]
Return to the base rate.
```

The older command system also describes relative adjustments:

```text
[[rate -15]]
[[rate +15]]
```

For Scholar Audio, absolute calculated rates are safer because they make returning to the base rate unambiguous.

### Volume

```text
[[volm 0.7]]
Quieter speech.
[[volm 1.0]]
Normal volume.
```

Changes synthesis volume. Actual behavior and acceptable values may vary by voice.

### Baseline pitch

```text
[[pbas 45]]
[[pbas +5]]
[[pbas -5]]
```

Changes the baseline pitch. Modern Enhanced voices may limit or disregard this control.

### Pitch modulation

```text
[[pmod 30]]
[[pmod +5]]
[[pmod -5]]
```

Controls how much the pitch rises and falls during speech. Lower modulation tends toward flatter speech; higher modulation permits more pitch variation.

### Emphasis

```text
[[emph +]]
Important term.
[[emph -]]
```

Turns emphasis on and off. Support is strongly voice-dependent.

### Input mode

```text
[[inpt TEXT]]
```

Uses normal written-text processing.

```text
[[inpt PHON]]
```

Treats subsequent input as phonemic notation. The exact phoneme inventory depends upon the synthesizer and voice.

### Character interpretation

```text
[[char NORM]]
[[char LTRL]]
```

`NORM` uses normal character interpretation. `LTRL` uses literal interpretation, useful when individual symbols or letters should be spoken.

### Number interpretation

```text
[[nmbr NORM]]
[[nmbr LTRL]]
```

`NORM` reads digits as an assembled number: `12` becomes “twelve.” `LTRL` reads digits individually: `12` becomes “one two.” See [Apple's number-mode documentation](https://developer.apple.com/documentation/appkit/nsspeechsynthesizer/speechpropertykey/numbermode).

### Comment

```text
[[cmnt This is an internal annotation]]
```

Marks command-stream commentary that should not be spoken. This is a legacy command and should be tested before relying on it.

### Change delimiters

```text
[[dlim ...]]
```

Changes the characters that mark embedded commands. The standard delimiters are `[[` and `]]`. Apple’s API also allows embedded processing to be disabled by assigning empty delimiters. Scholar Audio should retain the standard delimiters because they are easier to inspect and debug.

### Synchronization marker

```text
[[sync VALUE]]
```

Inserts a synchronization message into the speech stream. Applications using `NSSpeechSynthesizer` can receive a callback when the marker is encountered. It does not create an audible pause. See [Apple's synchronization callback documentation](https://developer.apple.com/documentation/appkit/nsspeechsynthesizerdelegate/speechsynthesizer(_:didencountersyncmessage:)).

### Version marker

```text
[[vers VALUE]]
```

Identifies the embedded-command format version. This is legacy framework machinery, not a useful audiobook control.

### Synthesizer-specific extension

```text
[[xtnd ...]]
```

Passes proprietary information to a particular synthesizer. It is nonportable and should not be used in Scholar Audio.

## Multiple commands together

Legacy syntax permits multiple commands inside one delimiter pair:

```text
[[rate 110; volm 0.85; pmod 25]]
```

For Scholar Audio, one command per marker is clearer:

```text
[[slnc 700]]
[[rate 110]]
This is a dense passage.
[[slnc 500]]
[[rate 130]]
```

## Non-command pacing controls

Ordinary writing also affects the voice:

- Comma: slight separation
- Semicolon: stronger separation
- Colon: anticipatory separation
- Period: sentence boundary
- Paragraph break: sometimes a larger boundary
- Em dash: voice-dependent
- Ellipsis: highly voice-dependent
- Spelling such as `A.I.`: influences pronunciation
- Short sentences: create clearer cognitive units

These are linguistic cues, not precisely timed commands.

## Recommended Scholar Audio subset

For dependable listening preparation, limit production use to:

```text
[[slnc MILLISECONDS]]
[[rate WPM]]
```

Potentially useful after voice-by-voice testing:

```text
[[volm VALUE]]
[[pbas VALUE]]
[[pmod VALUE]]
[[emph +]]
[[emph -]]
[[char LTRL]]
[[char NORM]]
[[nmbr LTRL]]
[[nmbr NORM]]
```

The remaining commands—`cmnt`, `dlim`, `inpt PHON`, `sync`, `vers`, and `xtnd`—are framework or specialized controls, not audiobook-pacing tools.
