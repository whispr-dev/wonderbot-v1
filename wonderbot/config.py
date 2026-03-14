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
    kind: str = "echo"
    hf_model: str = "distilgpt2"
    max_new_tokens: int = 120
    temperature: float = 0.8


@dataclass(slots=True)
class AgentConfig:
    name: str = "wonderbot"
    response_style: str = "warm, concise, reflective, technical when useful"
    reaction_threshold: float = 0.18
    spontaneous_interval: int = 5
    max_context_memories: int = 6


@dataclass(slots=True)
class WonderBotConfig:
    agent: AgentConfig
    codec: CodecConfig
    memory: MemoryConfig
    ganglion: GanglionConfig
    resonance: ResonanceConfig
    backend: BackendConfig

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
        )


def _read_toml(path: str | Path) -> Dict[str, Any]:
    with open(path, "rb") as handle:
        return tomllib.load(handle)
