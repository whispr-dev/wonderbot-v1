<!-- repo-convergence:readme-header:start -->
<!-- repo-convergence:language=FILL_ME -->
# wonderbot-v1

<p align="center">
  <a href="https://github.com/whisprer/wonderbot-v1/releases">
    <img src="https://img.shields.io/github/v/release/whisprer/wonderbot-v1?color=4CAF50&label=release" alt="Release Version">
  </a>
  <a href="https://github.com/whisprer/wonderbot-v1/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-Hybrid-green.svg" alt="License">
  </a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <a href="https://github.com/whisprer/wonderbot-v1/actions">
    <img src="https://img.shields.io/badge/build-workflow%20not%20set-lightgrey.svg" alt="Build Status">
  </a>
</p>

[![GitHub](https://img.shields.io/badge/GitHub-whisprer%2Fwonderbot-v1-blue?logo=github&style=flat-square)](https://github.com/whisprer/wonderbot-v1)
![Commits](https://img.shields.io/github/commit-activity/m/whisprer/wonderbot-v1?label=commits)
![Last Commit](https://img.shields.io/github/last-commit/whisprer/wonderbot-v1)
![Issues](https://img.shields.io/github/issues/whisprer/wonderbot-v1)
[![Version](https://img.shields.io/badge/version-3.1.1-blue.svg)](https://github.com/whisprer/wonderbot-v1)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)](https://www.microsoft.com/windows)
[![Language](https://img.shields.io/badge/language-FILL_ME-blue.svg)](#)
[![Status](https://img.shields.io/badge/Status-Alpha%20Release-orange?style=flat-square)](#)

<p align="center">
  <img src="/assets/wonderbot-v1-banner.png" width="850" alt="wonderbot-v1 Banner">
</p>
<!-- repo-convergence:readme-header:end -->

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
