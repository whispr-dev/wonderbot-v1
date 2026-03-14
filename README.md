# wonderbot-v1

A clean consolidation base for the archived LLM/agent experiments.

This repo is deliberately **not** another fragile wrapper around a standard tokenizer pretending to be tokenizerless.
Instead it separates the system into four clear layers:

1. **Event codec** — resonant segmentation + lossless byte encoding + feature signatures.
2. **Memory** — append-only, priority-ranked, searchable, non-destructive.
3. **Ganglion** — a clocked CA bus that gives the agent a continuously evolving internal substrate.
4. **LLM backend** — swappable. The default backend works with no external dependencies; optional HuggingFace support can be enabled later.

That split is the point: the old projects drifted because the “new tokenizer” was treated as if it could be dropped into a pretrained LM without retraining the representational contract. This base stops doing that.

## What was salvaged conceptually

- **`resonant-llm`** → event segmentation, local-agent shell, continuous memory emphasis.
- **`riemann-resonance-llm`** → resonance framing and the wish for cognition to be organized by resonance rather than only next-token prediction.
- **`woflchess` / `claude's-neural-chess`** → ganglion / CA bus / continuously ticking substrate.
- **`wofl-brain`** → coordination / “brain hub” framing.

## What this repo does now

- Runs immediately with **no third-party dependencies**.
- Supports an interactive, always-on-ish CLI agent that forms and searches memory continuously.
- Uses a **replacement tokenizer architecture where it is actually sound**: segmentation, salience, memory, and internal event coding.
- Keeps the LLM backend abstract so you can:
  - stay fully local and lightweight now,
  - plug in a HuggingFace backend later,
  - or replace the backend entirely with a future native event-stream model.

## What this repo does not pretend to do

- It does **not** claim that a pretrained LM has become tokenizerless.
- It does **not** require camera/mic/Whisper/BLIP/TTS just to boot.
- It does **not** destroy memory entries when consolidating.

## Quick start

```bash
python -m wonderbot.cli
```

Or after install:

```bash
pip install -e .
wonderbot
```

Type text normally. Useful commands:

- `/tick 5` — advance internal time and allow spontaneous thoughts
- `/state` — inspect ganglion / memory stats
- `/memory 10` — show top memories
- `/search your query` — semantic-ish memory lookup using the event codec
- `/save` — persist state
- `/quit` — exit cleanly

## Optional HuggingFace backend

```bash
pip install -e .[hf]
python -m wonderbot.cli --backend hf --hf-model distilgpt2
```

Note: the HF backend still uses its own tokenizer internally. That is intentional. The **agent contract** is event-coded text and memory; the backend is only one possible renderer.

## Repo layout

```text
wonderbot/
  agent.py
  cli.py
  config.py
  event_codec.py
  ganglion.py
  llm_backends.py
  memory.py
  resonance.py
  sensors/
configs/
  default.toml
docs/
  ARCHITECTURE.md
  CONSOLIDATION_NOTES.md
  LEGACY_MAP.md
scripts/
  seed_from_legacy.py
tests/
```

## Design choice that keeps this on-course

The event codec is the new center of gravity.

- It segments raw text into resonant events.
- It produces lossless byte IDs when exact reconstruction matters.
- It produces feature signatures for memory, salience, novelty, and internal routing.
- It can later become the input contract for a trained native event model.

That is the bridge from the old “tokenizer replacement” idea to something that actually survives contact with reality.
