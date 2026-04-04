from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .config import WonderBotConfig
from .event_codec import EventCodec, SegmentEvent
from .ganglion import Ganglion
from .llm_backends import create_backend
from .memory import MemoryStore
from .resonance import ResonanceField
from .sensors import SensorHub, SensorObservation, build_sensor_hub


@dataclass(slots=True)
class AgentTurn:
    stimulus: str
    response: Optional[str]
    resonance: float
    tick: int
    recalled: List[str]
    spontaneous: bool
    backend: str
    source: str = "user"
    salience: float = 0.0

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


WonderBotConfigAlias = WonderBotConfig


class WonderBot:
    def __init__(self, config: WonderBotConfig, sensor_hub: SensorHub | None = None) -> None:
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
        self.backend = create_backend(config=config.backend, codec=self.codec)
        self.sensor_hub = sensor_hub if sensor_hub is not None else build_sensor_hub(config)
        self.last_turn: Optional[AgentTurn] = None
        self._idle_counter = 0

    def observe(self, stimulus: str, source: str = "user", explicit: bool = True) -> AgentTurn:
        return self._observe_common(stimulus=stimulus, source=source, explicit=explicit, source_salience=0.0, metadata=None)

    def observe_sensor(self, observation: SensorObservation) -> AgentTurn:
        return self._observe_common(
            stimulus=observation.text,
            source=observation.source,
            explicit=False,
            source_salience=observation.salience,
            metadata={**observation.metadata, "sensor": True, "salience": observation.salience},
        )

    def poll_sensors(self) -> List[AgentTurn]:
        turns: List[AgentTurn] = []
        for observation in self.sensor_hub.poll():
            if observation.salience < self.config.live.sensor_memory_threshold:
                continue
            turn = self.observe_sensor(observation)
            turns.append(turn)
        return turns

    def idle_tick(self, count: int = 1) -> List[AgentTurn]:
        turns: List[AgentTurn] = []
        for _ in range(max(1, count)):
            self.ganglion.tick()
            sensor_turns = self.poll_sensors() if self.config.live.enabled else []
            turns.extend(sensor_turns)
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
                        source="assistant",
                        salience=0.0,
                    )
                    turns.append(turn)
                    self.last_turn = turn
                self._idle_counter = 0
        return turns

    def save(self) -> None:
        self.memory.save()

    def close(self) -> None:
        self.sensor_hub.close()
        self.save()

    def state_summary(self) -> Dict[str, object]:
        return {
            "tick": self.ganglion.t,
            "ganglion": self.ganglion.state_summary().to_dict(),
            "memory": self.memory.stats(),
            "sensors": [asdict(status) for status in self.sensor_hub.status()],
            "last_turn": self.last_turn.to_dict() if self.last_turn else None,
        }

    def _observe_common(
        self,
        stimulus: str,
        source: str,
        explicit: bool,
        source_salience: float,
        metadata: Optional[Dict[str, object]],
    ) -> AgentTurn:
        stimulus = stimulus.strip()
        events = self.codec.analyze_text(stimulus)
        if stimulus:
            self.memory.add(stimulus, source=source, metadata={"explicit": explicit, **(metadata or {})})
        resonance_value = self._ingest_events(events)
        drive = max(resonance_value, min(1.0, source_salience * self.config.live.sensor_reaction_gain))
        recalled_items = (
            self.memory.search(stimulus, k=self.config.agent.max_context_memories)
            if stimulus
            else self.memory.top_memories(self.config.agent.max_context_memories)
        )
        recalled = [item.text for item in recalled_items]
        should_answer = explicit or drive >= self.config.live.sensor_reaction_threshold or self.resonance.should_react(
            drive,
            self.config.agent.reaction_threshold,
            explicit=explicit,
        )
        response = None
        backend_name = self.backend.name if hasattr(self.backend, "name") else type(self.backend).__name__
        if should_answer:
            result = self.backend.generate(
                stimulus=stimulus,
                memories=recalled_items,
                style=self.config.agent.response_style,
                spontaneous=False,
            )
            response = result.text.strip()
            backend_name = result.backend_name
            if response:
                self.memory.add(response, source="assistant", metadata={"stimulus": stimulus, "source": source})
        if source == "user":
            self.ganglion.tick()
            self._idle_counter = 0
        turn = AgentTurn(
            stimulus=stimulus,
            response=response,
            resonance=round(drive, 6),
            tick=self.ganglion.t,
            recalled=recalled,
            spontaneous=False,
            backend=backend_name,
            source=source,
            salience=round(source_salience, 6),
        )
        self.last_turn = turn
        return turn

    def _ingest_events(self, events: List[SegmentEvent]) -> float:
        if not events:
            return 0.0
        for event in events:
            self.ganglion.write_signature(event.signature)
        return self.resonance.score_many([event.signature for event in events], tick=self.ganglion.t)


WonderBotConfig = WonderBotConfigAlias
