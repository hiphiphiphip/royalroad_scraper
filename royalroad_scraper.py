#!/usr/bin/env python3
"""
Just Good Enough Royal Road Scraper
===================================

Scrapes fics from royalroad.com and dumps them in a text file.

Install with:
    pip3 install requests BeautifulSoup4 blindspin

Run:
    python3 royalroad_scraper.py <url> <file>


License:
    MIT/WTFPL

Bugs:
    Exist. (Text encoding issues; giant paragraphs)

"""

import sys
import requests
import re

from bs4 import BeautifulSoup as bs
import blindspin


BASE_URL = "https://www.royalroad.com"
URL_CAPTURE_PATTERN = re.compile(r"https://www.royalroad.com/fiction/(\d+)")


def get_match(url):
    return URL_CAPTURE_PATTERN.match(url).group()


def iter_body_paragraphs(tree):
    chapter_contents_node = tree.select_one('.chapter-inner')
    paragraphs = chapter_contents_node.findAll('p')
    return paragraphs


def extract_text(tree):
    return tree.select_one('.chapter-inner').text


def extract_chapter_title(tree):
    return tree.find("meta", {"property": "og:title"})['content']


def extract_next_chapter_or_raise(tree):
    return BASE_URL + tree.find("link", {"rel": "next"})['href']


def make_tree(url):
    response = requests.get(url)
    response.raise_for_status()
    return bs(response.content, features="html.parser")


def main(url, out_file):
    tree = make_tree(url)

    chapters = [x['data-url'] for x in
                tree.select("tr[data-url]")]

    for chapter in chapters:
        tree = make_tree(BASE_URL + chapter)

        title = extract_chapter_title(tree)
        print(title, file=out_file)
        print("=" * len(title), file=out_file, end="\n\n")

        for paragraph in iter_body_paragraphs(tree):
            print(paragraph.text, file=out_file, end="\n\n")


def panic(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        url = get_match(sys.argv[1])
        if url:
            with open(sys.argv[2], 'w') as f:
                with blindspin.spinner():
                    main(url, f)
        else:
            panic("Bad url.\n\nscrape_rr.py <fiction_url> <outfile.txt>")
    else:
        panic("scrape_rr.py <fiction_url> <outfile.txt>")
