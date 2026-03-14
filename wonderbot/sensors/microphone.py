from __future__ import annotations


class MicrophoneUnavailableError(RuntimeError):
    pass


class SoundDeviceMicrophoneSource:
    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        try:
            import sounddevice as sd  # type: ignore
        except ImportError as exc:
            raise MicrophoneUnavailableError(
                "sounddevice is not installed. Install with: pip install -e .[audio]"
            ) from exc
        self._sd = sd
        self.sample_rate = sample_rate
        self.channels = channels

    def record(self, seconds: float = 3.0):
        frames = int(self.sample_rate * seconds)
        recording = self._sd.rec(frames, samplerate=self.sample_rate, channels=self.channels, dtype="float32")
        self._sd.wait()
        return recording
