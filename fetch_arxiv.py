import json
import requests
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from tqdm import tqdm
from bs4 import BeautifulSoup

def parse_args():
    parser = argparse.ArgumentParser(description='Fetch ArXiv papers from a specific category and date range')
    parser.add_argument('--category', type=str, default='cond-mat.mtrl-sci',
                        help='ArXiv category (default: cond-mat.mtrl-sci)')
    parser.add_argument('--start-date', type=str, required=True,
                        help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=str, default=None,
                        help='End date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--days', type=int, default=None,
                        help='Number of days to fetch (alternative to --end-date)')
    parser.add_argument('--output', type=str, default='feed_output.jsonl',
                        help='Output JSONL file path (default: feed_output.jsonl)')
    parser.add_argument('--max-results', type=int, default=1000,
                        help='Maximum results per day (default: 1000)')
    return parser.parse_args()

def parse_arxiv_atom(xml_text):
    """Parse ArXiv Atom feed and extract entries"""
    ns = {'atom': 'http://www.w3.org/2005/Atom',
          'arxiv': 'http://arxiv.org/schemas/atom'}

    root = ET.fromstring(xml_text)
    entries = []

    for entry in root.findall('atom:entry', ns):
        item = {}

        # Extract basic fields
        title = entry.find('atom:title', ns)
        if title is not None:
            item['title'] = title.text.strip().replace('\n', ' ')

        summary = entry.find('atom:summary', ns)
        if summary is not None:
            item['content_html'] = summary.text.strip()

        published = entry.find('atom:published', ns)
        if published is not None:
            item['date_published'] = published.text

        # Extract authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None:
                authors.append(name.text)
        if authors:
            item['authors'] = authors

        # Extract ArXiv ID and URL
        id_elem = entry.find('atom:id', ns)
        if id_elem is not None:
            item['id'] = id_elem.text
            item['url'] = id_elem.text

        # Extract PDF link
        for link in entry.findall('atom:link', ns):
            if link.get('title') == 'pdf':
                item['pdf_url'] = link.get('href')

        # Extract categories
        categories = []
        for category in entry.findall('atom:category', ns):
            term = category.get('term')
            if term:
                categories.append(term)
        if categories:
            item['categories'] = categories

        entries.append(item)

    return entries

def main():
    args = parse_args()

    # Parse start date
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    except ValueError:
        print("Error: Invalid start date format. Use YYYY-MM-DD")
        return

    # Determine end date
    if args.end_date is not None:
        # User provided end date
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid end date format. Use YYYY-MM-DD")
            return

        # Calculate number of days
        days = (end_date - start_date).days + 1

        if days <= 0:
            print("Error: End date must be after start date")
            return

    elif args.days is not None:
        # User provided number of days
        days = args.days
        end_date = start_date + timedelta(days=days - 1)
    else:
        # Default to today
        end_date = datetime.now()
        days = (end_date - start_date).days + 1

        if days <= 0:
            print("Error: Start date cannot be in the future")
            return

    # Generate day timestamps
    day_timestamps = [
        (start_date + timedelta(days=i)).strftime('%Y%m%d')
        for i in range(0, days)
    ]

    print(f"Fetching papers from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Total days: {days}")
    print(f"Category: {args.category}")

    BASE_URL = (
        f'http://export.arxiv.org/api/query?'
        f'search_query=cat:{args.category}+AND+'
        f'submittedDate:[{{day}}0000+TO+{{day}}2359]&'
        f'max_results={args.max_results}'
    )

    feeds = [BASE_URL.format(day=date) for date in day_timestamps]

    total_items = 0

    for feed in tqdm(feeds, desc="Fetching feeds"):
        try:
            resp = requests.get(feed, headers={"User-Agent": "arxiv-poll"})
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {feed}: {e}")
            continue

        try:
            items = parse_arxiv_atom(resp.text)
        except Exception as e:
            print(f"Error parsing feed {feed}: {e}")
            continue

        if not items:
            continue

        num_items = len(items)
        total_items += num_items

        # Clean HTML content
        for item in items:
            if 'content_html' in item:
                item['content_text'] = BeautifulSoup(
                    item['content_html'], "html.parser"
                ).get_text()

        # Append to output file
        with open(args.output, "a+", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")

    print(f"\nTotal items fetched: {total_items}")
    print(f"Output saved to: {args.output}")

if __name__ == "__main__":
    main()
