################################################################
# Written by ChatGPT 4 with the following prompt, May 1, 2024.
# Needed to fix one thing manually; search on "CORRECTION"
# 
# 
# You are going to write a python script that retrieves information about authors from Google Scholar, providing the university for each author.   For any author, you can get their Author Profile from Google Scholar using the following URL: 'https://scholar.google.com/citations?view_op=search_authors&mauthors=LASTNAME,+FIRSTNAME&hl=en&oi=ao'.  You should use curl to retrieve the author profile page and put it in ./profiles/LASTNAME_FIRSTNAME.html.  Then use BeautifulSoup to extract the university from the line after their name.  For example, if the author is 'Hinton, Geoffrey', the URL would be https://scholar.google.com/citations?view_op=search_authors&mauthors=argyle,+lisa&hl=en&oi=ao, the information at the top of the author profile is 'Geoffrey Hinton
# Emeritus Prof. Computer Science, University of Toronto
# Verified email at cs.toronto.edu', and the desired output would be 'Hinton, Geoffrey\tUniversity of Toronto'.
# 
# The program should take the list of author names from stdin and put the desired output, one author per line, on stdout.  If it is not possible to identify an author's university or institution for any reason, just put their name on the line in stdout in the same format as it appeared in the input.
# 
# If the author's name is ambiguous, then the profile page may contain information for multiple authors with that name. For example, if you ask for author profile for 'Smith, James', there is profile information for 'James Smith
# rand corporation
# Verified email at rand.org', for 'James E. Smith
# University of Wisconsin
# Verified email at ece.wisc.edu', and for 'James L Smith
# Los Alamos National Laboratory
# Verified email at lanl.gov', among others.  If that's the case, provide one output line for each profile in the HTML file.
# 
#  Output should not be buffered, so that if the program halts unexpectedly all the available output has been delivered to stdout.
# 
# The program should take an optional --sleep parameter. If the value is --sleep N, then the program should sleep or pause for N seconds in between accesses to Google Scholar, to avoid triggering rate limits. The default value should be 10.
################################################################

import os
import sys
import time
import argparse
from bs4 import BeautifulSoup

def fetch_author_profile(first_name, last_name, sleep_duration):
    # Creating the author-specific URL
    url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={last_name},+{first_name}&hl=en&oi=ao"
    # Creating directory if it doesn't exist
    directory = "./profiles"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f"{directory}/{last_name}_{first_name}.html"

    # Using curl to fetch the page
    command = f"curl -s '{url}' > '{file_path}'"
    print(f"DEBUG: running {command}")
    os.system(command)
    time.sleep(sleep_duration)  # Sleep to avoid hitting rate limits
    return file_path

def extract_university(file_path, first_name, last_name):
    # CORRECTION: was 'r' but 'rb' is necessary to avoid utf-8 related error
    with open(file_path, 'rb') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Finding all author profile entries
    entries = soup.find_all('div', class_='gsc_1usr')
    results = []
    for entry in entries:
        name_line = entry.find('h3', class_='gs_ai_name')
        if name_line:
            affiliation_line = entry.find('div', class_='gs_ai_aff')
            if affiliation_line:
                affiliation = affiliation_line.text.strip()
                results.append(f"{last_name}, {first_name}\t{affiliation}")
            else:
                results.append(f"{last_name}, {first_name}")
    return results

def main():
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description='Fetch and process Google Scholar author profiles.')
    parser.add_argument('--sleep', type=int, default=10, help='Sleep duration between requests to avoid rate limits')
    args = parser.parse_args()

    sleep_duration = args.sleep

    # Process each author name from standard input
    print("DEBUG: starting")
    for line in sys.stdin:
        if line.strip():
            first_name, last_name = line.strip().split(', ')
            file_path = fetch_author_profile(first_name, last_name, sleep_duration)
            results = extract_university(file_path, first_name, last_name)
            for result in results:
                print(result)
                sys.stdout.flush()

if __name__ == "__main__":
    main()
