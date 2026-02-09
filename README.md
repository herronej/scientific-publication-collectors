# scitext-collectors

A collection of tools and methods for downloading full-text scientific publications from various sources.

## Overview

Collecting full-text scientific papers at scale is a common need for NLP research, literature reviews, and training data curation. This repository provides modular, well-documented methods for fetching papers from different sources, each in its own directory with independent dependencies and usage instructions.

## Available Methods

| Method | Source | Output | Status |
|--------|--------|--------|--------|
| [arxiv-downloader](methods/arxiv-downloader/) | ArXiv API | PDF files + metadata (JSONL) | ✅ Ready |

## Repository Structure

```
scitext-collectors/
├── methods/
│   └── arxiv-downloader/       # Fetch and download ArXiv papers
│       ├── fetch_arxiv.py      # Query ArXiv API for paper metadata
│       ├── download_pdfs.py    # Download PDFs with checkpointing
│       ├── requirements.txt
│       └── README.md
├── README.md
└── LICENSE
```

## Usage

### arxiv-downloader

Fetch paper metadata and download full-text PDFs from ArXiv by category and date range.

**Install dependencies:**

```bash
cd methods/arxiv-downloader
pip install -r requirements.txt
```

**Step 1 — Fetch metadata:**

```bash
python fetch_arxiv.py \
    --category cond-mat.mtrl-sci \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    --output papers.jsonl
```

This queries the ArXiv API day-by-day and writes one JSON record per paper (title, authors, abstract, categories, URLs) to a JSONL file.

| Flag | Default | Description |
|------|---------|-------------|
| `--category` | `cond-mat.mtrl-sci` | ArXiv category to query |
| `--start-date` | *(required)* | Start date (`YYYY-MM-DD`) |
| `--end-date` | today | End date (`YYYY-MM-DD`) |
| `--days` | — | Alternative to `--end-date`: number of days from start |
| `--output` | `feed_output.jsonl` | Output JSONL path |
| `--max-results` | `1000` | Max results per day |

**Step 2 — Download PDFs:**

```bash
python download_pdfs.py \
    --input papers.jsonl \
    --output-dir ./pdfs
```

Downloads PDFs for every paper in the JSONL file. Progress is checkpointed automatically, so interrupted runs resume where they left off.

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | *(required)* | Input JSONL file from Step 1 |
| `--output-dir` | `./pdfs` | Directory to save downloaded PDFs |
| `--checkpoint` | `pdf_downloader_checkpoint.json` | Checkpoint file for resuming |
| `--start-index` | — | Override checkpoint; start from this index |

> **Rate limiting:** ArXiv asks that automated requests be spaced at least 3 seconds apart. The fetch script queries one day at a time, which provides natural pacing. See ArXiv's [API terms of use](https://info.arxiv.org/help/api/tou.html).
