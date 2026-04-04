# wonderbot-v1

A clean consolidation base for the archived LLM/agent experiments, now with optional **phase 4 multimodal enrichment**.

This repo is deliberately **not** another fragile wrapper around a standard tokenizer pretending to be tokenizerless.
Instead it separates the system into four clear layers:

1. **Event codec** — resonant segmentation + lossless byte encoding + feature signatures.
2. **Memory** — append-only, priority-ranked, searchable, non-destructive.
3. **Ganglion** — a clocked CA bus that gives the agent a continuously evolving internal substrate.
4. **LLM backend** — swappable. The default backend is a no-dependency local LVTC-style backend with a grounded path plus a guarded imagination branch; optional HuggingFace support can be enabled later.

That split is the point: the old projects drifted because the “new tokenizer” was treated as if it could be dropped into a pretrained LM without retraining the representational contract. This base stops doing that.

## What this repo does now

- Runs immediately with **no third-party dependencies**.
- Uses a **local LVTC-style controlled-imagination backend** by default instead of the old echo stub.
- Supports an interactive, always-on-ish CLI agent that forms and searches memory continuously.
- Uses a **replacement tokenizer architecture where it is actually sound**: segmentation, salience, memory, and internal event coding.
- Keeps the LLM backend abstract so you can stay lightweight now, plug in HF later, or replace the backend entirely with a future native event-stream model.
- Supports **optional live camera and microphone sensing**.
- Supports **optional image captioning and speech transcription enrichment** behind the same sensor contract, instead of hard-wiring multimodal logic into the agent core.

## What this repo does not pretend to do

- It does **not** claim that a pretrained LM has become tokenizerless.
- It does **not** require camera/mic/Whisper/BLIP/TTS just to boot.
- It does **not** destroy memory entries when consolidating.
- It does **not** force imagination into every turn.

## Quick start

```bash
py -3.11 -m wonderbot.cli
```

Or after install:

```bash
py -3.11 -m pip install -e .
wonderbot
```

## Live sensing

Sensor-only live mode:

```bash
py -3.11 -m pip install -e .[live]
py -3.11 -m wonderbot.cli --live --camera --microphone
```

Phase 4 live mode with captioning and STT enrichers:

```bash
py -3.11 -m pip install -e .[live-full]
py -3.11 -m wonderbot.cli --live --camera --microphone --caption --stt
```

Useful live commands:

- `/sensors` — show adapter availability
- `/sense` — poll sensors once immediately
- `/watch 20` — run 20 live polling ticks with the configured interval
- `/memory 10` — inspect what actually got stored

## Phase 4 multimodal design

The camera and microphone adapters remain responsible for low-level change detection.
Phase 4 adds **optional enrichers**:

- camera -> image captioner -> richer scene observation
- microphone -> speech transcriber -> transcript-bearing audio observation

The crucial design choice is that the agent still receives plain **event-coded observations**.
That means the multimodal path upgrades the *quality of the observation* without changing the rest of the system contract.

Example camera observation:

```text
camera sees noticeable motion with lighting shift in a bright scene and busy visual texture. Scene impression: desk with a monitor and a keyboard.
```

Example microphone observation:

```text
microphone hears voice-like audio activity and catches speech: "henlo wonderbot".
```

## Optional HuggingFace backend

```bash
py -3.11 -m pip install -e .[hf]
py -3.11 -m wonderbot.cli --backend hf --hf-model distilgpt2
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
  perception.py
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
