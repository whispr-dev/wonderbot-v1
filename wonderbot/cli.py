from __future__ import annotations

import argparse
import json

from .agent import WonderBot
from .config import WonderBotConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run WonderBot interactive CLI.")
    parser.add_argument("--config", default="configs/default.toml", help="Path to TOML config.")
    parser.add_argument("--backend", default=None, help="Override backend kind (echo or hf).")
    parser.add_argument("--hf-model", default=None, help="Override HuggingFace model name.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = WonderBotConfig.load(args.config)
    if args.backend is not None:
        cfg.backend.kind = args.backend
    if args.hf_model is not None:
        cfg.backend.hf_model = args.hf_model

    bot = WonderBot(cfg)
    print(f"[{cfg.agent.name}] ready. Type text or use /help.")

    while True:
        try:
            line = input("> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break

        if not line.strip():
            turns = bot.idle_tick(1)
            for turn in turns:
                print(f"[{turn.backend}] {turn.response}")
            continue

        if line.startswith("/"):
            if _handle_command(line, bot):
                continue
            break

        turn = bot.observe(line, source="user", explicit=True)
        if turn.response:
            print(f"[{turn.backend}] {turn.response}")
        else:
            print("[system] registered, but nothing crossed the reaction threshold.")

    bot.save()
    print("State saved.")
    return 0


def _handle_command(line: str, bot: WonderBot) -> bool:
    command, *rest = line.strip().split(maxsplit=1)
    arg = rest[0] if rest else ""
    if command == "/help":
        print("/tick [n]  /state  /memory [n]  /search <query>  /save  /quit")
        return True
    if command == "/tick":
        count = int(arg) if arg else 1
        turns = bot.idle_tick(count)
        if not turns:
            print(f"[system] advanced {count} ticks.")
        for turn in turns:
            print(f"[{turn.backend}] {turn.response}")
        return True
    if command == "/state":
        print(json.dumps(bot.state_summary(), indent=2, ensure_ascii=False))
        return True
    if command == "/memory":
        limit = int(arg) if arg else 10
        for item in bot.memory.top_memories(limit):
            print(f"- ({item.priority:.3f}) [{item.source}] {item.text}")
        return True
    if command == "/search":
        if not arg:
            print("Usage: /search your query")
            return True
        for item in bot.memory.search(arg, k=8):
            print(f"- ({item.priority:.3f}) [{item.source}] {item.text}")
        return True
    if command == "/save":
        bot.save()
        print("[system] state saved.")
        return True
    if command == "/quit":
        return False
    print(f"Unknown command: {command}. Use /help.")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
