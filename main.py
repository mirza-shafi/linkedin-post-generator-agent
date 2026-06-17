"""Command-line interface for the LinkedIn post generator agent.

Usage examples:
    python main.py
    python main.py --topic "AI in Healthcare" --language English
    python main.py -t "Remote Work Productivity" -l Bengali --tone inspirational
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from linkedin_agent import LinkedInPostAgent, PostRequest


def _prompt(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{label}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(130)
    return value or (default or "")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a professional LinkedIn post with a LangChain AI agent.",
    )
    parser.add_argument("-t", "--topic", help="Topic of the post.")
    parser.add_argument(
        "-l",
        "--language",
        default=None,
        help="Language of the post (e.g., English, Bengali, Spanish).",
    )
    parser.add_argument("--tone", help="Optional tone (e.g., inspirational, technical).")
    parser.add_argument("--audience", help="Optional target audience.")
    parser.add_argument("--model", help="Override the LLM model name.")
    parser.add_argument(
        "--temperature", type=float, help="Override the sampling temperature (0.0-1.0)."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = parse_args(argv)

    topic = args.topic or _prompt("Topic")
    if not topic.strip():
        print("Error: a topic is required.", file=sys.stderr)
        return 2

    language = args.language or _prompt("Language", default="English")

    try:
        agent = LinkedInPostAgent(model=args.model, temperature=args.temperature)
        request = PostRequest(
            topic=topic,
            language=language,
            tone=args.tone,
            audience=args.audience,
        )
        print("\nGenerating your LinkedIn post...\n", file=sys.stderr)
        post = agent.generate(request)
    except EnvironmentError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - surface any runtime/API error cleanly
        print(f"Failed to generate post: {exc}", file=sys.stderr)
        return 1

    divider = "=" * 60
    print(divider)
    print(post)
    print(divider)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
