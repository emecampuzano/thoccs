import argparse
import random
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf


class TypingSimulator:
    def __init__(
        self,
        samples_dir: str | Path = "samples",
        output_dir: str | Path = "output",
        delay_ms: int = 150,
        jitter_ms: int = 40,
        pitch_variance: float = 0.04,
        pitch_enabled: bool = True,
        jitter_enabled: bool = True,
    ):
        self.samples_dir = Path(samples_dir)
        self.output_dir = Path(output_dir)
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.pitch_variance = pitch_variance
        self.pitch_enabled = pitch_enabled
        self.jitter_enabled = jitter_enabled

        self.output_dir.mkdir(exist_ok=True)
        self._space_sample, self._sr = self._load_sample(
            self.samples_dir / "space.wav")
        self._key_samples = self._load_key_samples()
        self._channels = self._space_sample.shape[1]

    def _load_sample(self, path: Path) -> tuple[np.ndarray, int]:
        audio, sr = sf.read(path, dtype="float32", always_2d=True)
        return self._normalize(audio), sr

    def _load_key_samples(self) -> list[np.ndarray]:
        files = [f for f in self.samples_dir.glob(
            "*.wav") if f.stem != "space"]
        if not files:
            raise FileNotFoundError(
                f"No key samples found in {self.samples_dir}/")
        samples = []
        for f in files:
            audio, sr = self._load_sample(f)
            if sr != self._sr:
                raise ValueError(
                    f"{f.name} has sample rate {sr}, expected {self._sr}")
            samples.append(audio)
        return samples

    @staticmethod
    def _normalize(audio: np.ndarray) -> np.ndarray:
        peak = np.abs(audio).max()
        return audio / peak if peak > 0 else audio

    def _vary_pitch(self, audio: np.ndarray) -> np.ndarray:
        # factor = 1.0 + random.uniform(-self.pitch_variance, self.pitch_variance)
        # indices = np.arange(0, len(audio), factor)
        # indices = indices[indices < len(audio)].astype(int)
        # return audio[indices]
        return audio

    def _next_trigger_offset(self) -> int:
        """Return the number of samples to wait before triggering the next keystroke."""
        if self.jitter_enabled:
            ms = random.randint(
                max(10, self.delay_ms - self.jitter_ms),
                self.delay_ms + self.jitter_ms,
            )
        else:
            ms = self.delay_ms
        return int(self._sr * ms / 1000)

    def _clip_for_char(self, char: str) -> np.ndarray:
        clip = self._space_sample if char == " " else random.choice(
            self._key_samples)
        if self.pitch_enabled and char != " ":
            clip = self._vary_pitch(clip)
        return clip

    def render(self, text: str) -> np.ndarray:
        text = text.strip()
        if not text:
            return np.zeros((0, self._channels), dtype="float32")

        events: list[tuple[int, np.ndarray]] = []
        cursor = 0
        for i, char in enumerate(text):
            clip = self._clip_for_char(char)
            events.append((cursor, clip))
            if i < len(text) - 1:
                cursor += self._next_trigger_offset()

        last_trigger, last_clip = events[-1]

        total_samples = last_trigger + len(last_clip) + self._sr
        timeline = np.zeros((total_samples, self._channels), dtype="float32")

        for trigger, clip in events:
            end = trigger + len(clip)
            timeline[trigger:end] += clip

        np.clip(timeline, -1.0, 1.0, out=timeline)

        return timeline

    def save(self, text: str, filename: str = None) -> Path:
        if filename is None:
            filename = f"{text}.wav"
        audio = self.render(text)
        output_path = self.output_dir / filename
        sf.write(output_path, audio, self._sr)
        return output_path

    def save_and_open(self, text: str, filename: str = None) -> Path:
        if filename is None:
            filename = f"{text}.wav"
        output_path = self.save(text, filename)
        subprocess.run(["open", str(self.output_dir)])
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Simulate typing audio for a string.")
    parser.add_argument("text",
                        help="The string to simulate typing")
    parser.add_argument("--delay", type=int, default=200,
                        help="Base delay between keystrokes in ms (default: 120)")
    parser.add_argument("--jitter", type=int, default=40,
                        help="Max timing jitter in ms (default: 40)")
    parser.add_argument("--pitch-variance", type=float, default=0.04,
                        help="Pitch shift variance, e.g. 0.04 = ±4%% (default: 0.04)")
    parser.add_argument("--no-pitch", action="store_true",
                        help="Disable pitch variation")
    parser.add_argument("--no-jitter", action="store_true",
                        help="Disable timing jitter")
    parser.add_argument("--output", default=f"typed.wav",
                        help="Output filename (default: typed.wav)")
    args = parser.parse_args()

    sim = TypingSimulator(
        delay_ms=args.delay,
        jitter_ms=args.jitter,
        pitch_variance=args.pitch_variance,
        pitch_enabled=not args.no_pitch,
        jitter_enabled=not args.no_jitter,
    )

    path = sim.save_and_open(args.text)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()
