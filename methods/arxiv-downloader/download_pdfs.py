import json
import os
import argparse
from subprocess import call

def parse_args():
    parser = argparse.ArgumentParser(description='Download ArXiv PDFs from a JSONL file')
    parser.add_argument('--input', type=str, required=True,
                        help='Input JSONL file containing URLs')
    parser.add_argument('--output-dir', type=str, default='./pdfs',
                        help='Directory to save PDFs (default: ./pdfs)')
    parser.add_argument('--checkpoint', type=str, default='pdf_downloader_checkpoint.json',
                        help='Checkpoint file path (default: pdf_downloader_checkpoint.json)')
    parser.add_argument('--start-index', type=int, default=None,
                        help='Start from specific index (overrides checkpoint)')
    return parser.parse_args()

def load_checkpoint(checkpoint_path):
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)
        return checkpoint['batch_idx']
    else:
        return 0

def save_checkpoint(batch_idx, checkpoint_path):
    checkpoint = {'batch_idx': batch_idx}
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f)

def read_urls_from_jsonl(file_path):
    urls = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if "url" in record:
                    urls.append(record["url"].replace("abs", "pdf") + ".pdf")
            except json.JSONDecodeError:
                # skip malformed lines
                continue
    return urls

def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Read URLs
    urls = read_urls_from_jsonl(args.input)
    print(f"Found {len(urls)} URLs in {args.input}")

    # Determine start index
    if args.start_index is not None:
        start_index = args.start_index
        print(f"Starting from index {start_index} (user-specified)")
    else:
        start_index = load_checkpoint(args.checkpoint)
        print(f"Starting from index {start_index} (from checkpoint)")

    # Download PDFs
    for index, url in enumerate(urls):
        if index < start_index:
            continue

        print(f"\n[{index + 1}/{len(urls)}] Downloading: {url}")

        try:
            url = url.replace("abs", "pdf")
            ret_code = os.system(f"arxiv-downloader {url} -d {args.output_dir}")
            if ret_code != 0:
                print(f"Warning: Download returned non-zero exit code: {ret_code}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            save_checkpoint(index, args.checkpoint)
            return

        save_checkpoint(index + 1, args.checkpoint)

    print(f"\nDownload complete! PDFs saved to: {args.output_dir}")

if __name__ == "__main__":
    main()
