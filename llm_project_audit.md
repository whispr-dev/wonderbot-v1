# LLM Project Audit and Consolidation Recommendation

## Executive summary

You have **six distinct branches** in this archive, but only **three are serious candidates** for consolidation:

1. **`code/resonant-llm`** — best current base for a working local multimodal agent
2. **`code/riemann-resonance-llm`** — best preserved expression of the original resonance model idea
3. **`code/woflchess` + `code/wofl-brain` + `code/claude's-neural-chess`** — best source of the **ganglion / clock / CA brain** ideas

The important surprise:

- The **“tokenizerless / replacement tokenizer” candidate is `code/resonant-llm/code/fren-agent/src/fren_agent/resonant_tokenizer.py`**
- But it is **not actually the active model interface**
- And in its current form it is **not production-ready as the main token interface for a language model**

Right now the overall situation is:

- **Most runnable bot base:** `resonant-llm`
- **Most faithful to the original Riemann idea:** `riemann-resonance-llm`
- **Best source of the brain/ganglion timing idea:** `woflchess`, `wofl-brain`, `claude's-neural-chess`
- **Most junk / least trustworthy as source-of-truth:** `multimodal-agent` zips and `grok's_take` generated fragments

## What looks current vs actually useful

### 1) `code/resonant-llm` — **KEEP / USE AS BASE**
Why:
- Cleanest structure
- Python source compiles
- Real local-agent architecture exists
- Has GUI, memory, audio, vision, TTS, and a resonance-flavored LLM wrapper
- Contains the only real tokenizer-replacement implementation

Key files:
- `code/resonant-llm/code/fren-agent/src/fren_agent/agent.py`
- `code/resonant-llm/code/fren-agent/src/fren_agent/llm/resonant_llm.py`
- `code/resonant-llm/code/fren-agent/src/fren_agent/resonant_tokenizer.py`
- `code/resonant-llm/code/fren-agent/src/fren_agent/memory.py`
- `code/resonant-llm/code/fren-agent/src/fren_agent/guardian.py`
- `code/resonant-llm/code/fren-agent/src/fren_agent/gui/app.py`

### 2) `code/riemann-resonance-llm` — **KEEP / MINE FOR CORE IDEAS**
Why:
- Cleaner “pure concept” repo for resonance-collapse transformer work
- Python source compiles
- Preserves the intended Riemann-resonance framing better than the multimodal branches

Best files:
- `code/riemann-resonance-llm/src/riemann_resonance_llm/model_b.py`
- `code/riemann-resonance-llm/src/riemann_resonance_llm/modules/resonance_collapse_b.py`
- `code/riemann-resonance-llm/src/riemann_resonance_llm/train_b.py`

### 3) `code/woflchess` — **KEEP / SALVAGE**
Why:
- Not a bot foundation, but it contains the strongest concrete implementation of the **ganglion / CA bus / synchronous clocked brain** idea in Python
- This is valuable if you want the “living, ticking, always-on” architecture back

Best files:
- `code/woflchess/engine/ca_bus.py`
- `code/woflchess/engine/ganglion.py`
- `code/woflchess/engine/tri_gan.py`
- `code/woflchess/engine/nets.py`

### 4) `code/wofl-brain` — **KEEP AS SPEC / NOT AS CODEBASE**
Why:
- Mostly design notebook / architectural conversation
- Strong conceptual material for ganglion-mediated multimodal coordination
- Not a real codebase

Most useful file:
- `code/wofl-brain/petey-convo.md`

### 5) `code/claude's-neural-chess` — **KEEP / SALVAGE IDEAS ONLY**
Why:
- Newest hand-authored source by timestamp
- Strong Rust implementation of a **clocking ganglion**
- But it is still chess-specific and not your fastest route to a working wonder-bot

Best file:
- `code/claude's-neural-chess/neural_chess/ganglion.rs`

### 6) `code/multimodal-agent` — **ARCHIVE / SALVAGE SMALL PIECES ONLY**
Why:
- Earliest practical multimodal shell
- But the source tree is inconsistent, duplicated, partly broken, and mixed with generated / pasted fragments
- Multiple zips look newer by timestamp but are **not** more trustworthy

Useful only for:
- early UI / interaction flow ideas
- legacy module comparisons

## The “replacement tokenizer” status

## What it is
The replacement tokenizer is almost certainly:

- `code/resonant-llm/code/fren-agent/src/fren_agent/resonant_tokenizer.py`

It is a:
- character n-gram hashed feature extractor
- phase-shift segmenter
- optional semantic lexicon learned by online k-means
- byte-fallback reversible encoder

So this is **not really “no tokenizer”** in the strict sense. It is closer to:

**segmentation + semantic chunk coding + reversible UTF-8 byte fallback**

That is interesting and salvageable, but it is not yet a complete tokenizerless language interface.

## Why it is not actually active
In:
- `code/resonant-llm/code/fren-agent/src/fren_agent/llm/resonant_llm.py`

the model still does this:

- loads a standard HuggingFace tokenizer
- loads a standard HuggingFace causal LM
- wraps generation with the resonant tokenizer before and after

Critical problem:
- `self.reso = ResoTokenizer(vocab_size=65536)` is created
- but there is **no `fit()`**
- and no saved tokenizer state is loaded
- so the semantic lexicon is empty

That means the current “replacement tokenizer” is usually just doing **byte-level reversible pass-through**, not a learned semantic interface.

## Additional problem: semantic mode is lossy
I smoke-tested the tokenizer implementation directly.

Observed behavior:
- `lossless=True` round-trips correctly
- `lossless=False` often reconstructs the wrong text after fitting a small corpus

Examples observed during testing:
- `"hello world"` decoded semantically as `"helles"`
- `"camera input"` decoded semantically as `"camera input and m"`
- `"real time memory"` decoded semantically as `"realme"`
- `"tokenizerless wonder bot"` decoded semantically as `"heheesher het"`

Conclusion:
- the current semantic-token path is **experimental**, not stable enough to become your main model I/O contract

## So what is the deep architectural truth?
If you really replace the tokenizer, you **cannot** just swap it into a pretrained HF model and expect the model to stay aligned.

You have three real options:

### Option A — Fastest, most practical
Keep a standard pretrained LM tokenizer for the core LM, and use your replacement tokenizer for:
- memory chunking
- event segmentation
- multimodal scene/audio episode formation
- salience ranking
- agent-side cognition

This gives you a **working wonder-bot fastest**, but it is not fully tokenizerless.

### Option B — Best compromise
Keep the replacement tokenizer, but train an **adapter** from its semantic/byte IDs into an existing pretrained embedding space.

This needs:
- a frozen or lightly tuned pretrained model
- a learned embedding bridge / projection layer
- distillation or reconstruction training

This is the best route if you want to **stay close to the new tokenizer idea** without training an entire model from scratch.

### Option C — Most faithful to the vision
Build a real tokenizerless-ish model:
- byte / patch / event stream input
- learned segmenter
- ganglion clock
- resonance gating
- memory prioritization loop
- native multimodal event stream

This is the cleanest conceptually, but it is the slowest path.

## Why the project drifted off course

Your original idea was:
- continuous input
- camera + mic always on
- memory forming continuously
- salience-driven retention
- autonomous reaction without waiting for explicit prompts
- resonance as a deep organizing principle

What happened in the current code:
- the live-agent shell got built
- memory got built
- multimodal pieces got built
- but the cognitive core drifted into “standard pretrained model + wrappers”
- resonance became mostly:
  - logits modulation
  - entropy gating
  - naming / framing
- not the actual primary representational substrate

So yes: **your intuition is correct**. It drifted.

## Concrete keep / archive / salvage decision

### KEEP IN ACTIVE CONSOLIDATION
- `code/resonant-llm`
- `code/riemann-resonance-llm/src/riemann_resonance_llm/model_b.py`
- `code/riemann-resonance-llm/src/riemann_resonance_llm/modules/resonance_collapse_b.py`
- `code/woflchess/engine/ca_bus.py`
- `code/woflchess/engine/ganglion.py`
- `code/wofl-brain/petey-convo.md`
- `code/claude's-neural-chess/neural_chess/ganglion.rs`

### ARCHIVE BUT DO NOT TRUST AS PRIMARY SOURCE
- `code/multimodal-agent`
- `code/multimodal-agent/bakup_zips/*`
- `code/multimodal-agent/grok's_take/*`
- `code/multimodal-agent/multimodal_agent_fixed.zip`
- `code/multimodal-agent/fren-agent.zip`

### PROBABLY JUNK / DERIVED / GENERATED
- most `grok's_take` Python fragments
- zip bundles that contain mixed code + pasted chat text
- duplicate old/new/ol1/ol2/old versions unless manually diffed later

## Specific code issues worth knowing

### `resonant-llm`
1. `agent.py` initializes `self.memory` twice, and the second initialization drops governance protection
2. `main.py` forces Coqui TTS through environment variables even though config still exposes Piper
3. the resonant tokenizer is not trained/loaded before use
4. the LLM core still depends on a normal HF tokenizer

### `riemann-resonance-llm`
1. `config/tokenizer.model` is empty
2. `inference_b.py` still loads a normal HF tokenizer (`sentence-transformers/all-MiniLM-L6-v2`)
3. this repo is conceptually closer to the original vision, but not actually tokenizerless

### `woflchess`
1. `engine/agent.py` imports `.utils`
2. the file present is `engine/utiils.py`
3. that typo will break runtime once dependencies are installed

### `multimodal-agent`
1. top-level `main.py` has a syntax error (`continue` outside loop block)
2. several generated modules do not parse
3. latest zips are not source-of-truth; some contain mixed code + pasted conversation text

## Best consolidation target

If the goal is:

### “Give me a decent working wonder bot soon”
Base it on **`resonant-llm`**

Then merge into it:
- `model_b.py` and `resonance_collapse_b.py` from `riemann-resonance-llm`
- ganglion / CA bus ideas from `woflchess`
- architecture rules from `wofl-brain`
- timing/diagnostic ganglion ideas from `claude's-neural-chess`

## Recommended consolidated architecture

### Layer 1 — Sensor/event loop
From `resonant-llm`:
- camera
- mic
- STT
- TTS
- GUI
- memory persistence

### Layer 2 — Continuous salience/memory engine
Use:
- current semantic memory from `resonant-llm`
- extend it to event/episode memory rather than only dialogue memory
- use replacement tokenizer **here first**, not as LM core input

### Layer 3 — Ganglion clock / scheduler
Merge from:
- `woflchess/engine/ganglion.py`
- `woflchess/engine/ca_bus.py`
- ideas from `claude's-neural-chess/neural_chess/ganglion.rs`

Purpose:
- synchronize vision/audio/LLM/memory ticks
- maintain live state even without explicit prompt
- create periodic self-check / self-reflection windows
- support autonomous reaction

### Layer 4 — Resonance core
Use:
- `model_b.py`
- `resonance_collapse_b.py`

But treat this as:
- experimental cognitive module
- scoring / gating / salience layer first
- only later a full generative backbone

### Layer 5 — Tokenizer replacement path
Do **not** make the current `ResoTokenizer` your only LM tokenizer yet.

Instead:
1. stabilize it
2. train or fit it properly
3. use it for memory segmentation and event chunking first
4. only then build an adapter into the LM

## My blunt recommendation

Do **not** try to merge every cool idea directly into one codebase right now.

That would recreate the mess.

Instead build one deliberate branch:

### `wonderbot-v1`
Base:
- `resonant-llm`

Add only four things:
1. **fixes** to `resonant-llm`
2. **better resonance block** from `riemann-resonance-llm/model_b.py`
3. **ganglion tick loop** from `woflchess`
4. **replacement tokenizer only for memory/event segmentation at first**

That gives you:
- a living always-on multimodal agent
- memory prioritization
- resonance gating
- room to evolve toward true tokenizerless operation
- minimal self-inflicted chaos

## Final verdict

### Best current base
`resonant-llm`

### Best alternate tokenizer candidate
`resonant_tokenizer.py` in `resonant-llm`

### Is that tokenizerless path working as intended?
No.

### Best salvage from the original Riemann path
`model_b.py` + `resonance_collapse_b.py`

### Best salvage from the “brain” path
`ca_bus.py` + `ganglion.py` + `petey-convo.md`

### What to archive
Most of `multimodal-agent` zips and generated fragments

### What to build next
A single **`wonderbot-v1`** branch based on `resonant-llm`, with:
- bug fixes
- event memory
- ganglion scheduler
- resonance block upgrade
- replacement tokenizer used first for segmentation/memory, not yet full LM I/O
