# thoccs

Turns text into realistic typing sounds.

I made this because I needed typing audio for videos and other projects. It takes keyboard samples and strings them together with some randomness so it actually sounds like someone typing instead of the same click repeated over and over.

## How it works

Put your keystroke samples in `samples/` (WAV files). The script picks random samples for each character and adds timing variations and pitch shifts. Spaces use their own sample. Output goes to `output/`.

## Setup

```bash
pip install numpy soundfile
```

You'll need sample WAV files in the `samples/` directory:
- Individual keystrokes (any name except `space.wav`)
- `space.wav` for spaces

## Usage

Basic:
```bash
python main.py "hello world"
```

With options:
```bash
python main.py "your text here" --delay 150 --jitter 50 --output my_typing.wav
```

Options:
- `--delay` - Base time between keystrokes in milliseconds (default: 50)
- `--jitter` - Random timing variation in ms (default: 40)
- `--pitch-variance` - How much pitch can shift, e.g., 0.04 = ±4% (default: 0.04)
- `--no-pitch` - Turn off pitch variation (Disabled by default)
- `--no-jitter` - Turn off timing variation
- `--output` - Name of the output file (default: typed.wav)

The script will save the audio and open the output folder when it's done.

## Notes

- All samples need the same sample rate (48Khz 24 bit)
- Shorter delays make faster typing
- More jitter sounds more human but less predictable
- Pitch variance is currently disabled in the code (commented out) but the flag is there

## License

MIT
