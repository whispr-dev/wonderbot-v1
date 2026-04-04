from __future__ import annotations

import argparse
import json
import time

from .agent import AgentTurn, WonderBot
from .config import WonderBotConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run WonderBot interactive CLI.")
    parser.add_argument("--config", default="configs/default.toml", help="Path to TOML config.")
    parser.add_argument("--backend", default=None, help="Override backend kind (lvtc or hf).")
    parser.add_argument("--hf-model", default=None, help="Override HuggingFace model name.")
    parser.add_argument("--live", action="store_true", help="Enable configured live sensor polling.")
    parser.add_argument("--camera", action="store_true", help="Enable camera adapter for this run.")
    parser.add_argument("--microphone", action="store_true", help="Enable microphone adapter for this run.")
    parser.add_argument("--caption", action="store_true", help="Enable caption enrichment for camera observations.")
    parser.add_argument("--stt", action="store_true", help="Enable speech-to-text enrichment for microphone observations.")
    parser.add_argument("--caption-model", default=None, help="Override image captioning model name.")
    parser.add_argument("--speech-model", default=None, help="Override speech transcription model name.")
    return parser



def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = WonderBotConfig.load(args.config)
    if args.backend is not None:
        cfg.backend.kind = args.backend
    if args.hf_model is not None:
        cfg.backend.hf_model = args.hf_model
    if args.live:
        cfg.live.enabled = True
    if args.camera:
        cfg.live.enabled = True
        cfg.camera.enabled = True
    if args.microphone:
        cfg.live.enabled = True
        cfg.microphone.enabled = True
    if args.caption:
        cfg.live.enabled = True
        cfg.camera.enabled = True
        cfg.caption.enabled = True
    if args.stt:
        cfg.live.enabled = True
        cfg.microphone.enabled = True
        cfg.speech.enabled = True
    if args.caption_model is not None:
        cfg.caption.model = args.caption_model
    if args.speech_model is not None:
        cfg.speech.model = args.speech_model

    bot = WonderBot(cfg)
    print(f"[{cfg.agent.name}] ready. Type text or use /help.")

    try:
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
                _render_turns(turns)
                continue

            if line.startswith("/"):
                if _handle_command(line, bot):
                    continue
                break

            turn = bot.observe(line, source="user", explicit=True)
            _render_turn(turn)
    finally:
        bot.close()
        print("State saved.")
    return 0



def _handle_command(line: str, bot: WonderBot) -> bool:
    command, *rest = line.strip().split(maxsplit=1)
    arg = rest[0] if rest else ""
    if command == "/help":
        print("/tick [n]  /sense  /watch [n]  /sensors  /state  /memory [n]  /search <query>  /save  /quit")
        return True
    if command == "/tick":
        count = int(arg) if arg else 1
        turns = bot.idle_tick(count)
        if not turns:
            print(f"[system] advanced {count} ticks.")
        _render_turns(turns)
        return True
    if command == "/sense":
        turns = bot.poll_sensors()
        if not turns:
            print("[system] no live sensor event crossed the salience threshold.")
        _render_turns(turns)
        return True
    if command == "/watch":
        count = int(arg) if arg else 10
        for i in range(max(1, count)):
            turns = bot.idle_tick(1)
            if not turns:
                print(f"[system] watch tick {i + 1}: no salient sensor event.")
            _render_turns(turns)
            time.sleep(max(0.0, bot.config.live.poll_interval_ms / 1000.0))
        return True
    if command == "/sensors":
        for status in bot.sensor_hub.status():
            state = "available" if status.available else "unavailable"
            enabled = "enabled" if status.enabled else "disabled"
            print(f"- [{status.source}] {enabled}, {state}: {status.detail}")
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



def _render_turns(turns: list[AgentTurn]) -> None:
    for turn in turns:
        _render_turn(turn)



def _render_turn(turn: AgentTurn) -> None:
    if turn.spontaneous:
        if turn.response:
            print(f"[{turn.backend}] {turn.response}")
        return
    if turn.source in {"camera", "microphone"}:
        print(f"[{turn.source}] {turn.stimulus} (salience={turn.salience:.2f})")
        if turn.response:
            print(f"[{turn.backend}] {turn.response}")
        else:
            print("[system] sensed and stored, but stayed grounded.")
        return
    if turn.response:
        print(f"[{turn.backend}] {turn.response}")
    else:
        print("[system] registered, but nothing crossed the reaction threshold.")


if __name__ == "__main__":
    raise SystemExit(main())
