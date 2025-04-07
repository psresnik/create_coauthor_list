#!/usr/bin/env python3
#######################################################################################################################
# python refs2bibtex.py  < refs.txt > out.bib
#
# Reads text references one per line, searches on Google Scholar to find a bibtex entry for each.
# Written with Claude 3.7 Sonnet.
#
#######################################################################################################################
import argparse
import os
import re
import sys
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

def create_references_dir():
    """Create the references directory if it doesn't exist."""
    if not os.path.exists('./references'):
        os.makedirs('./references')

def url_encode_reference(reference):
    """URL encode a reference for use in a Google Scholar search."""
    return urllib.parse.quote_plus(reference)

def get_google_scholar_search_url(reference):
    """Create a Google Scholar search URL for the given reference."""
    encoded_reference = url_encode_reference(reference)
    return f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C21&q={encoded_reference}&btnG="

def extract_scisig(html_content):
    """Extract the scisig value from the HTML content using multiple techniques."""
    # Pattern 1: Look for scisig in data-sval attribute
    pattern1 = r'data-sval="[^"]*scisig=([A-Za-z0-9_-]+)'
    match = re.search(pattern1, html_content)
    if match:
        return match.group(1)
    
    # Pattern 2: Look for scisig as a parameter in various attributes
    pattern2 = r'scisig=([A-Za-z0-9_-]+)'
    matches = re.findall(pattern2, html_content)
    if matches:
        # Exclude very short matches which might be incomplete
        valid_matches = [m for m in matches if len(m) > 8]
        if valid_matches:
            return max(valid_matches, key=len)
    
    # Pattern 3: Try to find any citation link which might contain the info
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for cite button or links
    cite_links = soup.select('a.gs_or_cit')
    if cite_links:
        for link in cite_links:
            onclick = link.get('onclick', '')
            if 'gs_ocit' in onclick:
                # Extract the citation data
                match = re.search(r'gs_ocit\(event,\'([^\']+)', onclick)
                if match:
                    citation_data = match.group(1)
                    # This data typically has the paper ID which can be used to construct the URL
                    return f"citation_data:{citation_data}"
    
    # Pattern 4: Look for the first search result and extract its ID
    results = soup.select('.gs_r')
    if results:
        first_result = results[0]
        result_id = first_result.get('data-cid') or first_result.get('id')
        if result_id:
            return f"result_id:{result_id}"
    
    return None

def construct_bibtex_url(scisig_or_id, reference):
    """Construct the URL to retrieve the BibTeX entry based on extracted information."""
    if scisig_or_id.startswith("citation_data:"):
        # Use citation data to construct URL
        citation_data = scisig_or_id.split(':', 1)[1]
        return f"https://scholar.google.com/scholar?q=info:{citation_data}:scholar.google.com/&output=cite&scirp=0&hl=en"
    
    elif scisig_or_id.startswith("result_id:"):
        # Use result ID to construct URL
        result_id = scisig_or_id.split(':', 1)[1]
        return f"https://scholar.google.com/scholar?q=info:{result_id}:scholar.google.com/&output=cite&scirp=0&hl=en"
    
    else:
        # Use scisig directly
        return f"https://scholar.googleusercontent.com/scholar.bib?q=info:info:scholar.google.com/&output=citation&scisdr=&scisig={scisig_or_id}&scisf=4&ct=citation&cd=-1&hl=en"

def get_cite_page_and_extract_bibtex_link(bibtex_page_url, headers, debug=False):
    """Get the citation page and extract the BibTeX link."""
    try:
        response = requests.get(bibtex_page_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for BibTeX link in the citation dialog
        bibtex_link = None
        for link in soup.find_all('a'):
            if link.text and 'BibTeX' in link.text:
                bibtex_link = link.get('href')
                if bibtex_link:
                    # If it's a relative URL, make it absolute
                    if bibtex_link.startswith('/'):
                        bibtex_link = f"https://scholar.google.com{bibtex_link}"
                    break
        
        return bibtex_link
        
    except Exception as e:
        if debug:
            print(f"Error getting citation page: {e}", file=sys.stderr)
        return None

def get_bibtex_entry(reference, sleep_seconds=10, debug=False):
    """Get BibTeX entry for a reference."""
    search_url = get_google_scholar_search_url(reference)
    
    # Create sequential filename
    reference_count = len([name for name in os.listdir('./references') if name.endswith('.html')]) + 1
    html_file_path = f"./references/{reference_count}.html"
    
    if debug:
        print(f"Search URL: {search_url}", file=sys.stderr)
        print(f"Saving search results to: {html_file_path}", file=sys.stderr)
    
    # Download search results
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Save the search results
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Extract information needed for citation
        scisig_or_id = extract_scisig(response.text)
        if not scisig_or_id:
            if debug:
                print(f"Could not find citation information for reference: {reference}", file=sys.stderr)
                print("Dumping a portion of the HTML for debugging:", file=sys.stderr)
                print(response.text[:1000], file=sys.stderr)
            return None
        
        if debug:
            print(f"Found citation info: {scisig_or_id}", file=sys.stderr)
        
        # Construct URL for citation page
        citation_url = construct_bibtex_url(scisig_or_id, reference)
        if debug:
            print(f"Citation URL: {citation_url}", file=sys.stderr)
        
        # Sleep before making the next request to avoid rate limiting
        time.sleep(sleep_seconds)
        
        # If we got a citation page URL rather than direct BibTeX URL
        bibtex_url = citation_url
        if "output=cite" in citation_url:
            # We need to first get the citation page and then extract the BibTeX link from it
            bibtex_link = get_cite_page_and_extract_bibtex_link(citation_url, headers, debug)
            if not bibtex_link:
                if debug:
                    print(f"Could not find BibTeX link on citation page", file=sys.stderr)
                return None
                
            bibtex_url = bibtex_link
            if debug:
                print(f"BibTeX URL: {bibtex_url}", file=sys.stderr)
            
            # Sleep again before fetching the actual BibTeX
            time.sleep(sleep_seconds)
        
        # Now get the actual BibTeX content
        bibtex_response = requests.get(bibtex_url, headers=headers)
        bibtex_response.raise_for_status()
        
        # Parse the BibTeX content
        soup = BeautifulSoup(bibtex_response.text, 'html.parser')
        
        # Try to get pre-formatted text first (most common for BibTeX)
        pre_tag = soup.find('pre')
        if pre_tag:
            bibtex_content = pre_tag.get_text().strip()
        else:
            # Fallback to regular text
            bibtex_content = soup.get_text().strip()
        
        # Check if we got a valid BibTeX entry
        if bibtex_content and '@' in bibtex_content:
            return bibtex_content
        else:
            if debug:
                print(f"No valid BibTeX entry found for reference: {reference}", file=sys.stderr)
                print(f"Response content: {bibtex_response.text[:500]}", file=sys.stderr)
            return None
            
    except Exception as e:
        if debug:
            print(f"Error processing reference: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Retrieve BibTeX entries from Google Scholar.')
    parser.add_argument('--sleep', type=int, default=10, help='Sleep time in seconds between Google Scholar accesses')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    create_references_dir()
    
    # Process references from stdin
    for line in sys.stdin:
        reference = line.strip()
        if not reference:
            continue
            
        # Print the reference as a comment
        print(f"% {reference}")
        
        # Get BibTeX entry
        bibtex_entry = get_bibtex_entry(reference, args.sleep, args.debug)
        
        # Print the BibTeX entry or a blank line if none was found
        if bibtex_entry:
            print(bibtex_entry)
        print()
        
        # Flush stdout to ensure output is not buffered
        sys.stdout.flush()

if __name__ == "__main__":
    main()

    
