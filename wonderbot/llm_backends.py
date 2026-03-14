from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from .memory import MemoryItem


@dataclass(slots=True)
class BackendResult:
    text: str
    backend_name: str


class TextBackend(Protocol):
    def generate(self, stimulus: str, memories: List[MemoryItem], style: str, spontaneous: bool = False) -> BackendResult:
        ...


class EchoBackend:
    name = "echo"

    def generate(self, stimulus: str, memories: List[MemoryItem], style: str, spontaneous: bool = False) -> BackendResult:
        top_memory = memories[0].text if memories else "nothing anchored strongly enough yet"
        if spontaneous:
            text = (
                f"I'm still running the thread of thought around: {top_memory}. "
                f"The current internal pull says it deserves another pass."
            )
            return BackendResult(text=text, backend_name=self.name)
        if not stimulus.strip():
            return BackendResult(text="I registered the lull, but nothing salient crystallized.", backend_name=self.name)
        text = (
            f"I noticed: {stimulus.strip()}\n"
            f"Most relevant memory: {top_memory}\n"
            f"Current stance: {style}."
        )
        return BackendResult(text=text, backend_name=self.name)


class HFBackend:
    name = "hf"

    def __init__(self, model_name: str = "distilgpt2", max_new_tokens: int = 120, temperature: float = 0.8) -> None:
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError as exc:
            raise RuntimeError(
                "HuggingFace backend requested, but transformers/torch are not installed. "
                "Install with: pip install -e .[hf]"
            ) from exc

        self._torch = torch
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()

    def generate(self, stimulus: str, memories: List[MemoryItem], style: str, spontaneous: bool = False) -> BackendResult:
        prompt = _build_prompt(stimulus=stimulus, memories=memories, style=style, spontaneous=spontaneous)
        encoded = self.tokenizer(prompt, return_tensors="pt")
        with self._torch.inference_mode():
            output = self.model.generate(
                **encoded,
                do_sample=True,
                temperature=max(0.01, self.temperature),
                max_new_tokens=self.max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated_ids = output[0][encoded["input_ids"].shape[1]:]
        text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        if not text:
            text = "I had the shape of a response, but the backend returned silence."
        return BackendResult(text=text, backend_name=self.name)


def create_backend(kind: str, hf_model: str = "distilgpt2", max_new_tokens: int = 120, temperature: float = 0.8) -> TextBackend:
    normalized = kind.strip().lower()
    if normalized == "echo":
        return EchoBackend()
    if normalized == "hf":
        return HFBackend(model_name=hf_model, max_new_tokens=max_new_tokens, temperature=temperature)
    raise ValueError(f"Unsupported backend kind: {kind}")


def _build_prompt(stimulus: str, memories: List[MemoryItem], style: str, spontaneous: bool) -> str:
    memory_block = "\n".join(f"- {memory.text}" for memory in memories[:6]) or "- none"
    mode = "spontaneous reflection" if spontaneous else "response"
    return (
        f"You are WonderBot. Style: {style}. Mode: {mode}.\n"
        f"Relevant memories:\n{memory_block}\n\n"
        f"Current stimulus: {stimulus or '[idle]'}\n"
        f"Answer concisely and coherently.\nAssistant:"
    )
