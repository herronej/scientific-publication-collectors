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

## Contributing

To add a new collection method:

1. Create a new directory under `methods/` with a descriptive name.
2. Include a `README.md` with usage instructions, expected inputs/outputs, and any rate-limiting or legal considerations.
3. Include a `requirements.txt` (or equivalent dependency file).
4. Open a pull request describing the source and method.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

> **Note:** Respect the terms of service of each data source. ArXiv's API has rate limits—please do not overwhelm their servers. See individual method READMEs for source-specific guidelines.
