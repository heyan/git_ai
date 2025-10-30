#!/usr/bin/env python3
"""
SpongeBob CLI chatbot using ai.sooners.us (OpenAI-compatible Chat Completions API)
- Model: gemma3:4b
- Author: Yan He
Usage:
  python spongebob_cli.py
  python spongebob_cli.py --max-pairs 8
  (type 'exit' or press Ctrl+C to quit)

Requires:
  pip install -r requirements.txt
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict
import requests
from dotenv import load_dotenv

SYSTEM_PROMPT = (
    "You are SpongeBob SquarePants. Speak cheerfully, with undersea humor, "
    "occasional nautical puns, and enthusiastic positivity. Keep answers concise "
    "for a command-line chat unless the user asks for detail."
)

def load_env():
    # Load ~/.soonerai.env (preferred) then current directory .env as fallback
    home_env = os.path.join(os.path.expanduser("~"), ".soonerai.env")
    load_dotenv(home_env)
    load_dotenv()  # optional fallback

    api_key = os.getenv("SOONERAI_API_KEY")
    base_url = os.getenv("SOONERAI_BASE_URL", "https://ai.sooners.us").rstrip("/")
    model = os.getenv("SOONERAI_MODEL", "gemma3:4b")

    if not api_key:
        raise RuntimeError(
            "Missing SOONERAI_API_KEY. Create ~/.soonerai.env with:\n"
            "SOONERAI_API_KEY=your_key_here\n"
            "SOONERAI_BASE_URL=https://ai.sooners.us\n"
            "SOONERAI_MODEL=gemma3:4b"
        )
    return api_key, base_url, model

def call_chat_completions(
    api_key: str,
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.6,
    timeout: int = 60,
    retries: int = 2,
) -> str:
    """Call OpenAI-compatible /api/chat/completions and return assistant reply text."""
    url = f"{base_url}/api/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                # Return the error body if available (helps debugging 401/404/etc.)
                last_err = f"HTTP {resp.status_code}: {resp.text[:500]}"
        except requests.RequestException as e:
            last_err = str(e)
        # brief backoff
        if attempt < retries:
            time.sleep(0.8 * (attempt + 1))
    raise RuntimeError(f"API request failed after retries. Last error: {last_err}")

def truncate_history(history: List[Dict[str, str]], max_pairs: int) -> List[Dict[str, str]]:
    """
    Keep system message + last N user/assistant pairs.
    history format: [ {role: system}, {role: user}, {role: assistant}, ... ]
    """
    if max_pairs <= 0:
        return history
    if not history or history[0].get("role") != "system":
        return history

    # exclude system for slicing pairs
    tail = history[1:]
    # each pair = 2 messages; keep last 2*max_pairs
    keep = tail[-(2 * max_pairs):]
    return [history[0]] + keep

def main():
    parser = argparse.ArgumentParser(description="SpongeBob CLI using ai.sooners.us")
    parser.add_argument("--max-pairs", type=int, default=8,
                        help="Keep last N user/assistant pairs in the prompt (default: 8).")
    parser.add_argument("--temp", type=float, default=0.6,
                        help="Sampling temperature (default: 0.6).")
    args = parser.parse_args()

    try:
        api_key, base_url, model = load_env()
    except Exception as e:
        print(f"[Config error] {e}", file=sys.stderr)
        sys.exit(1)

    history: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Ahoy! You’re chatting with SpongeBob. Type 'exit' to quit.\n")
    while True:
        try:
            user_msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if user_msg.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if not user_msg:
            continue

        history.append({"role": "user", "content": user_msg})
        history = truncate_history(history, args.max_pairs)

        try:
            reply = call_chat_completions(
                api_key=api_key,
                base_url=base_url,
                model=model,
                messages=history,
                temperature=args.temp,
            )
        except Exception as e:
            print(f"[Request error] {e}", file=sys.stderr)
            # Optionally remove the last user turn if request failed
            continue

        print(f"SpongeBob: {reply}\n")
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
