# CertForge — Azure Certification Lab Builder

Transform Azure certification cram session videos into complete, deployable hands-on lab environments.

## Workflow

1. **Generate a transcript** — run `yt2md.sh` against a YouTube cram session URL to produce a Markdown transcript
2. **Build the lab prompt** — feed `certforge-prompt.md` and the transcript into an LLM (e.g., a Copilot session) to generate a full lab project with IaC, study guide, exercises, and cost estimates

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Step 1: Generate the transcript

```bash
./yt2md.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

This creates a Markdown file named after the video title (e.g., `AZ-104_Azure_Administrator_Cram.md`).

You can also use the Python script directly for more control:

```bash
# Print to stdout
python yt2md.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Save to a specific file
python yt2md.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.md

# Specify transcript language
python yt2md.py "https://www.youtube.com/watch?v=VIDEO_ID" -l es
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o`, `--output` | Output file path | stdout |
| `-l`, `--language` | Transcript language code | `en` |

### Step 2: Generate the lab

Open a Copilot session (or any LLM) and provide:

1. The contents of `certforge-prompt.md` as the system/meta prompt
2. The generated transcript file
3. The YouTube URL for metadata extraction

The CertForge prompt will guide the LLM through building a complete lab project.

## What gets generated

The transcript Markdown includes:
- Video title and metadata (keywords, runtime)
- Full video description
- Transcript (when available)

The CertForge prompt produces a full lab project with:
- Infrastructure as Code (Terraform, Bicep, or Azure CLI)
- Comprehensive lab study guide with exercises
- Architecture diagrams (Mermaid)
- Cost estimates and cleanup scripts

## Dependencies

- `markitdown` — Microsoft's file-to-Markdown converter
- `youtube-transcript-api` — fetches YouTube captions

No LLM libraries (e.g., litellm) are in the dependency chain.
