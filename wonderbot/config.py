from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any, Dict


@dataclass(slots=True)
class CodecConfig:
    dim: int = 192
    ngram: int = 3
    window_chars: int = 16
    min_segment_chars: int = 4
    cosine_drop: float = 0.14
    lowercase: bool = False
    nfkc: bool = True


@dataclass(slots=True)
class MemoryConfig:
    path: str = "state/memory.json"
    max_active_items: int = 2000
    protect_identity: bool = True
    importance_threshold: float = 0.36
    min_novelty: float = 0.08


@dataclass(slots=True)
class GanglionConfig:
    height: int = 8
    width: int = 8
    channels: int = 8
    bleed: float = 0.03


@dataclass(slots=True)
class ResonanceConfig:
    sigma: float = 0.5
    tau: float = 14.134725
    alpha: float = 1.2
    prime_count: int = 32


@dataclass(slots=True)
class BackendConfig:
    kind: str = "lvtc"
    hf_model: str = "distilgpt2"
    max_new_tokens: int = 120
    temperature: float = 0.8
    delta_scale: float = 0.24
    creative_depth: int = 1
    anchor_pullback: float = 0.72
    novelty_threshold: float = 0.10
    drift_threshold: float = 0.58
    repetition_threshold: float = 0.34
    latency_budget_ms: int = 30


@dataclass(slots=True)
class AgentConfig:
    name: str = "wonderbot"
    response_style: str = "warm, concise, reflective, technical when useful"
    reaction_threshold: float = 0.18
    spontaneous_interval: int = 5
    max_context_memories: int = 6


@dataclass(slots=True)
class LiveConfig:
    enabled: bool = False
    poll_interval_ms: int = 350
    sensor_memory_threshold: float = 0.10
    sensor_reaction_threshold: float = 0.18
    sensor_reaction_gain: float = 1.15


@dataclass(slots=True)
class CameraConfig:
    enabled: bool = False
    index: int = 0
    width: int = 320
    height: int = 240
    motion_threshold: float = 0.08
    brightness_threshold: float = 0.05
    min_salience: float = 0.12


@dataclass(slots=True)
class MicrophoneConfig:
    enabled: bool = False
    sample_rate: int = 16000
    channels: int = 1
    window_seconds: float = 0.35
    rms_threshold: float = 0.03
    peak_threshold: float = 0.12
    min_salience: float = 0.10


@dataclass(slots=True)
class CaptionConfig:
    enabled: bool = False
    model: str = "Salesforce/blip-image-captioning-base"
    max_new_tokens: int = 24
    interval_seconds: float = 3.0
    salience_threshold: float = 0.22
    min_chars: int = 12


@dataclass(slots=True)
class SpeechConfig:
    enabled: bool = False
    model: str = "openai/whisper-tiny.en"
    language: str = "en"
    salience_threshold: float = 0.22
    min_chars: int = 4
    cooldown_seconds: float = 0.75


@dataclass(slots=True)
class WonderBotConfig:
    agent: AgentConfig
    codec: CodecConfig
    memory: MemoryConfig
    ganglion: GanglionConfig
    resonance: ResonanceConfig
    backend: BackendConfig
    live: LiveConfig
    camera: CameraConfig
    microphone: MicrophoneConfig
    caption: CaptionConfig
    speech: SpeechConfig

    @classmethod
    def load(cls, path: str | Path) -> "WonderBotConfig":
        data = _read_toml(path)
        return cls(
            agent=AgentConfig(**data.get("agent", {})),
            codec=CodecConfig(**data.get("codec", {})),
            memory=MemoryConfig(**data.get("memory", {})),
            ganglion=GanglionConfig(**data.get("ganglion", {})),
            resonance=ResonanceConfig(**data.get("resonance", {})),
            backend=BackendConfig(**data.get("backend", {})),
            live=LiveConfig(**data.get("live", {})),
            camera=CameraConfig(**data.get("camera", {})),
            microphone=MicrophoneConfig(**data.get("microphone", {})),
            caption=CaptionConfig(**data.get("caption", {})),
            speech=SpeechConfig(**data.get("speech", {})),
        )



def _read_toml(path: str | Path) -> Dict[str, Any]:
    with open(path, "rb") as handle:
        return tomllib.load(handle)
