from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Dict, List, Optional

from .config import WonderBotConfig
from .event_codec import EventCodec, SegmentEvent
from .ganglion import Ganglion
from .llm_backends import BackendResult, create_backend
from .memory import MemoryItem, MemoryStore
from .resonance import ResonanceField


@dataclass(slots=True)
class AgentTurn:
    stimulus: str
    response: Optional[str]
    resonance: float
    tick: int
    recalled: List[str]
    spontaneous: bool
    backend: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class WonderBotConfigBundle:
    raw: WonderBotConfig


WonderBotConfigAlias = WonderBotConfig


class WonderBot:
    def __init__(self, config: WonderBotConfig) -> None:
        self.config = config
        self.codec = EventCodec(
            dim=config.codec.dim,
            ngram=config.codec.ngram,
            window_chars=config.codec.window_chars,
            min_segment_chars=config.codec.min_segment_chars,
            cosine_drop=config.codec.cosine_drop,
            lowercase=config.codec.lowercase,
            nfkc=config.codec.nfkc,
        )
        self.memory = MemoryStore(
            codec=self.codec,
            path=config.memory.path,
            max_active_items=config.memory.max_active_items,
            protect_identity=config.memory.protect_identity,
            importance_threshold=config.memory.importance_threshold,
            min_novelty=config.memory.min_novelty,
        )
        self.ganglion = Ganglion(
            height=config.ganglion.height,
            width=config.ganglion.width,
            channels=config.ganglion.channels,
            bleed=config.ganglion.bleed,
        )
        self.resonance = ResonanceField(
            sigma=config.resonance.sigma,
            tau=config.resonance.tau,
            alpha=config.resonance.alpha,
            prime_count=config.resonance.prime_count,
        )
        self.backend = create_backend(
            kind=config.backend.kind,
            hf_model=config.backend.hf_model,
            max_new_tokens=config.backend.max_new_tokens,
            temperature=config.backend.temperature,
        )
        self.last_turn: Optional[AgentTurn] = None
        self._idle_counter = 0

    def observe(self, stimulus: str, source: str = "user", explicit: bool = True) -> AgentTurn:
        stimulus = stimulus.strip()
        events = self.codec.analyze_text(stimulus)
        if stimulus:
            self.memory.add(stimulus, source=source, metadata={"explicit": explicit})
        resonance_value = self._ingest_events(events)
        recalled_items = self.memory.search(stimulus, k=self.config.agent.max_context_memories) if stimulus else self.memory.top_memories(self.config.agent.max_context_memories)
        recalled = [item.text for item in recalled_items]
        should_answer = self.resonance.should_react(resonance_value, self.config.agent.reaction_threshold, explicit=explicit)
        response = None
        backend_name = self.backend.name if hasattr(self.backend, "name") else type(self.backend).__name__
        if should_answer:
            result = self.backend.generate(stimulus=stimulus, memories=recalled_items, style=self.config.agent.response_style, spontaneous=False)
            response = result.text
            backend_name = result.backend_name
            if response.strip():
                response = response.strip()
                self.memory.add(response, source="assistant", metadata={"stimulus": stimulus})
        self.ganglion.tick()
        self._idle_counter = 0
        turn = AgentTurn(
            stimulus=stimulus,
            response=response,
            resonance=round(resonance_value, 6),
            tick=self.ganglion.t,
            recalled=recalled,
            spontaneous=False,
            backend=backend_name,
        )
        self.last_turn = turn
        return turn

    def idle_tick(self, count: int = 1) -> List[AgentTurn]:
        turns: List[AgentTurn] = []
        for _ in range(max(1, count)):
            self.ganglion.tick()
            self._idle_counter += 1
            if self._idle_counter >= self.config.agent.spontaneous_interval:
                memories = self.memory.top_memories(self.config.agent.max_context_memories)
                result = self.backend.generate(stimulus="", memories=memories, style=self.config.agent.response_style, spontaneous=True)
                if result.text.strip():
                    text = result.text.strip()
                    self.memory.add(text, source="assistant", metadata={"spontaneous": True})
                    turn = AgentTurn(
                        stimulus="",
                        response=text,
                        resonance=0.0,
                        tick=self.ganglion.t,
                        recalled=[memory.text for memory in memories],
                        spontaneous=True,
                        backend=result.backend_name,
                    )
                    turns.append(turn)
                    self.last_turn = turn
                self._idle_counter = 0
        return turns

    def save(self) -> None:
        self.memory.save()

    def state_summary(self) -> Dict[str, object]:
        return {
            "tick": self.ganglion.t,
            "ganglion": self.ganglion.state_summary().to_dict(),
            "memory": self.memory.stats(),
            "last_turn": self.last_turn.to_dict() if self.last_turn else None,
        }

    def _ingest_events(self, events: List[SegmentEvent]) -> float:
        if not events:
            return 0.0
        for event in events:
            self.ganglion.write_signature(event.signature)
        return self.resonance.score_many([event.signature for event in events], tick=self.ganglion.t)


WonderBotConfig = WonderBotConfigAlias
