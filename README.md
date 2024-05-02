# create_coauthor_list
Streamlining creation of a list of co-authors and their institutions from a bibliography of your publications

For NSF proposals it is required to provide a list of collaborators and other affiliations (COA) in an [Excel file](https://www.nsf.gov/bfa/dias/policy/coa/coa_template.xlsx), https://www.nsf.gov/bfa/dias/policy/coa/coa_template.xlsx. And getting a list of all your recent collaborators can be a serious pain in the neck.  Here is some stuff I've written that makes it a lot easier, even if it's a bit kludgy.

_Author: Philip Resnik, University of Maryland (resnik@umd.edu)_

## Have a .bib file containing your publications

If you don't use BibTex, our friend ChatGPT will make it easy for you
to take whatever format you have your citations in (e.g. copy/paste
from your c.v.) and create the .bib file. Just use chat.openai.com
(ChatGPT 3.5 is fine) with the following prompt:

```
Create bibtex entries for the following papers:
<copy/paste your references here>
```

Depending how many refs you've got you may need to do this in multiple
batches since ChatGPT has limits on the size of any single prompt.


## Get all co-authors from your .bib file

Make a copy of `authorindex.tex` and follow the instructions in
the header. If you need to sort your .bib file chronologically so you
can easily copy/paste just the entries from the last five years into a
fresh .bib file to use as input, go [here](https://flamingtempura.github.io/bibtex-tidy/index.html?opt=%7B%22modify%22%3Atrue%2C%22curly%22%3Atrue%2C%22numeric%22%3Atrue%2C%22months%22%3Afalse%2C%22space%22%3A2%2C%22tab%22%3Atrue%2C%22align%22%3A13%2C%22blankLines%22%3Atrue%2C%22sort%22%3A%5B%22year%22%2C%22month%22%2C%22author%22%2C%22key%22%5D%2C%22duplicates%22%3A%5B%22key%22%2C%22doi%22%2C%22citation%22%5D%2C%22merge%22%3A%22combine%22%2C%22stripEnclosingBraces%22%3Afalse%2C%22dropAllCaps%22%3Afalse%2C%22escape%22%3Afalse%2C%22sortFields%22%3A%5B%22year%22%2C%22month%22%2C%22day%22%2C%22author%22%2C%22title%22%2C%22shorttitle%22%2C%22journal%22%2C%22booktitle%22%2C%22location%22%2C%22on%22%2C%22publisher%22%2C%22address%22%2C%22series%22%2C%22volume%22%2C%22number%22%2C%22pages%22%2C%22doi%22%2C%22isbn%22%2C%22issn%22%2C%22url%22%2C%22urldate%22%2C%22copyright%22%2C%22category%22%2C%22note%22%2C%22metadata%22%5D%2C%22stripComments%22%3Afalse%2C%22trailingCommas%22%3Afalse%2C%22encodeUrls%22%3Afalse%2C%22tidyComments%22%3Atrue%2C%22removeEmptyFields%22%3Afalse%2C%22removeDuplicateFields%22%3Afalse%2C%22lowercase%22%3Atrue%2C%22backup%22%3Atrue%7D
): 

```
https://flamingtempura.github.io/bibtex-tidy/index.html?opt=%7B%22modify%22%3Atrue%2C%22curly%22%3Atrue%2C%22numeric%22%3Atrue%2C%22months%22%3Afalse%2C%22space%22%3A2%2C%22tab%22%3Atrue%2C%22align%22%3A13%2C%22blankLines%22%3Atrue%2C%22sort%22%3A%5B%22year%22%2C%22month%22%2C%22author%22%2C%22key%22%5D%2C%22duplicates%22%3A%5B%22key%22%2C%22doi%22%2C%22citation%22%5D%2C%22merge%22%3A%22combine%22%2C%22stripEnclosingBraces%22%3Afalse%2C%22dropAllCaps%22%3Afalse%2C%22escape%22%3Afalse%2C%22sortFields%22%3A%5B%22year%22%2C%22month%22%2C%22day%22%2C%22author%22%2C%22title%22%2C%22shorttitle%22%2C%22journal%22%2C%22booktitle%22%2C%22location%22%2C%22on%22%2C%22publisher%22%2C%22address%22%2C%22series%22%2C%22volume%22%2C%22number%22%2C%22pages%22%2C%22doi%22%2C%22isbn%22%2C%22issn%22%2C%22url%22%2C%22urldate%22%2C%22copyright%22%2C%22category%22%2C%22note%22%2C%22metadata%22%5D%2C%22stripComments%22%3Afalse%2C%22trailingCommas%22%3Afalse%2C%22encodeUrls%22%3Afalse%2C%22tidyComments%22%3Atrue%2C%22removeEmptyFields%22%3Afalse%2C%22removeDuplicateFields%22%3Afalse%2C%22lowercase%22%3Atrue%2C%22backup%22%3Atrue%7D
```

a handy online tool that lets you paste in a .bib file and do nice
things like de-dupe, normalize entries, and sort by year.  (The
parameters in the url default to settings that should be good for all that, but you can customize on
the page.)

Once you've followed the directions in authorindex.tex, you'll now
have a file with one co-author per line in `authors.txt` in lastname,
firstname format.  Don't forget to delete the line containing
yourself.



## Get the institutions for your co-authors

Institutions are not required in the NSF COA template, but it's a nice
thing to have..

### Get co-author work info from Google Scholar
```
python fetch_scholar_info.py < authors.txt > Collaborator_institutions.txt
```

Yes, that output file is weirdly in 'firstname, lastname' format. I
made a mistake when specifying what I wanted to ChatGPT and decided to
just live with it since this is only an intermediate file anyway.

Note that `fetch_scholar_info.py` uses system calls to `curl`. That's
because the original version using the `request` package led to Google
blocking the IP address; oddly with `curl` this was not a problem.

Note that the script takes an optional `--sleep N` options to sleep N
seconds between hitting Google Scholar to avoid rate limiting or
blocking. Defaults to 10 but 5 seems to work just as well.

### Edit the file that resulted

The Google Scholar profile pages can list multiple matches, especially
for common names. You'll want to manually review/edit so each author
has just one line.


### Combine your author list and the Scholar info

Sometimes the info pulled back from Google Scholar includes both a
position and an institution, e.g. "Professor, Univ of Maryland". To
pull out just the institution and join that info with people's names
as they appear on your co-author list:

```
python join_scholar_info.py authors.txt Collaborator_institutions.txt > coa_info.csv
```

### Manually edit the resulting CSV file

The code isn't perfect, e.g. for institutions you might see the
department and institution together. It's good enough that it's not
worth it (to me) to mess with trying to get the code perfect. I used
CSV rather than XLSX so it would be easy to fix things in a text
editor if that's preferred over editing in Excel.

### Delete the temporary `profiles` directory

The `fetch_scholar_info.py` script created a temporary directory for the HTML author profiles pulled from Google Scholar. Since that can take some time, to be cautious the code doesn't delete that temporary directory. At this point you should be able to go ahead and delete it. 


## Copy info into the COA template

At this point either you've got `authors.txt` (if you didn't add
institutions), or `coa_info.csv` (if you did). Either way, you can
open the file with Excel and then just copy/paste info into the NSF
COA Excel template.

Voila!





