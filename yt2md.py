#!/usr/bin/env python3
"""Convert a YouTube video transcript to Markdown using Microsoft's markitdown."""

import argparse
import re
import sys

from markitdown import MarkItDown

YOUTUBE_URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w\-]+"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert YouTube video transcript to Markdown."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-o", "--output", default=None, help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "-l",
        "--language",
        default="en",
        help="Transcript language code (default: en)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not YOUTUBE_URL_PATTERN.match(args.url):
        print(f"Error: '{args.url}' does not look like a YouTube URL.", file=sys.stderr)
        sys.exit(1)

    try:
        md = MarkItDown()
        result = md.convert(
            args.url,
            enableYoutubeTranscript=True,
            youtubeTranscriptLanguage=args.language,
        )
    except Exception as exc:
        print(f"Error converting video: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result.text_content or not result.text_content.strip():
        print("Warning: No content was returned. The video may lack a transcript.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.text_content)
        print(f"Markdown written to {args.output}", file=sys.stderr)
    else:
        print(result.text_content)


if __name__ == "__main__":
    main()
