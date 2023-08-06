=========
bibupdate
=========

**Usage**: 

usage: bibupdate [-h] [-a] [-c] [-f] [-i IGNORE] [-l LOG] [-m | -M] [-q] [-r]
                 [-w LEN] bibtexfile [outputfile]

This is a command line tool for updating the entries in a BibTeX_ file using
mrlookup_. By default bibupdate_ tries to update the entry for each paper
in the BibTeX_ file unless the entry already has an ``mrnumber`` field (you can
disable future checking of an entry by giving it an empty ``mrnumber`` field).

**Options**::

  -a, --all             update or validate ALL BibTeX entries
  -c, --check_all       check all bibtex entries against a database
  -f, --font_replace    do NOT replace fonts \Bbb, \germ and \scr
  -h, --help            show this help message and exit
  -i IGNORE, --ignored-fields IGNORE
                        a string of bibtex fields to ignore
  -l LOG, --log LOG     log messages to specified file (defaults to stdout)
  -q, --quietness       print fewer messages
  -r  --replace         replace existing bibtex file
  -w {}, --wrap {}      wrap bibtex fields to specified width

  -m, --mrlookup        use mrlookup to update bibtex entries (default)
  -M, --mathscinet      use mathscinet to update bibtex entries (less flexible)

**Note:** 
As described below, you should check the new file for errors before deleting the
original version of your BibTeX_ file.

By default, bibupdate_ does not change your original database file. Instead, it creates a
new file with the name *updated_file.bib*, if your original file was *file.bib*.
It is also possible to have it replace your current file (use carefully!), or to
specify a new file name.

BibTeX_ is widely used by the LaTeX_ community to maintain publication databases.
This script attempts to add missing fields to the papers in a BibTeX_ database
file by querying mrlookup_ and getting the missing information from there. This
is not completely routine because to search on mrlookup_ you need either the
authors or the title of the article and both of these can have non-standard
representations. If the article is already published then it is also possible to
use the publication year and its page numbers. To search on mrlookup_ we:

    - use the authors (can be problematic because of accents and names with von etc)
    - use the page numbers, if they exist
    - use the year only if there are no page numbers and this is NOT a preprint
    - use the title if there are no page numbers (or this is a book)

If there is a unique (good, non-fuzzy) match from mrlookup_ then bibupdate_
replaces all of the current fields with those from mrlookup_, except for the
citation key. The values of any fields that are not specified by mrlookup_, such
as ``eprint`` fields, are retained. By default, a message is printed whenever
existing fields in the database are changed. If the title of the retrieved paper
does not (fuzzily) match that of the original article then the entry is NOT
updated and a warning message is printed.

Although some care is taken to make sure that the new BibTeX_ entries correspond
to the same paper that the original entry referred to there is always a (small?)
chance the new entry corresponds to an entirely different paper. In my
experience this happens rarely, and mostly with unpublished manuscripts. In any
case, before you delete your original BibTeX_ file *you are strongly advised to
check the updated file BibTeX file carefully for errors!*

To help the user to compare the updated fields for each entry in the BibTeX_
file the program prints a detailed list of all changes that are made to existing
BibTeX_ fields (any new fields that are added are not printed). Once bibupdate_
has finished running it is recommended that you compare the old and new versions
of your database using programs like *diff* and *tkdiff*.

As bibupdate_ calls mrlookup_ this program will only be useful if you have
papers in your database that are listed in MathSciNet_. As described below it is
also possible to call MathSciNet_ directly, however, this is less flexible
because the ``mrnumber`` field for each paper is required.

I wrote this script because I wanted to automatically add links to journals, the
arXiv_ and DOIs to the bibliographies of my papers using hyperref_. This script
allowed me to add the missing urls and DOI fields to my BibTeX_ database. As a
bonus the script helped me to correct many minor errors that had crept into my
BibTeX_ file over the years (for example, incorrect page numbers and publication
years). Now I use the program to automatically update the preprint entries in my
database when the papers appear in MathSciNet_ after they are published.

Options and their defaults
--------------------------

-a, --all  Update or validate ALL BibTeX entries

  By default bibupdate_ only checks each BibTeX_ entry with the mrlookup
  database if the entry does *not* have an ``mrnumber`` field. With this switch
  all entries are checked and updated.

-c --check_all  Check/validate all bibtex entries against a database

  Prints a list of entries in the BibTeX file that have fields different from
  those given by the corresponding database. The original BibTeX file is not
  changed.

-f, --font_replace  Do not replace fonts \\germ and \\scr

  The BibTeX_ entries generated by mrlookup_ use \\Bbb, \\germ and \\scr for the
  \\mathbb, \\mathfrak and \\mathscr fonts. By default, in the *title* fields,
  these fonts specifications are automatically changed to the following more
  LaTeX_ friendly fonts:

        - \\Bbb X  --> \\mathbb{X}
        - \\scr X  --> \\mathcal{X}
        - \\germ X --> \\mathfrak{X}

  The -f option *disables* these substitutions.

-i IGNORE, --ignored-fields=IGNORE  A string of BibTeX_ fields to ignore when writing the updated file

  By default bibupdate_ removes the following fields from each BibTeX_ entry:

      - coden
      - mrreviewer
      - fjournal
      - issn

  This list can be changed using the -i command line option::

     bibupdate -i "coden fjournal" file.bib   # ignore coden and fjournal
     bibupdate -i coden -i fjournal file.bib  # ignore coden and fjournal
     bibupdate -i "" file.bib                 # do not ignore any fields

-l LOG, --log LOG  Log output to file (defaults to stdout)

  Specify a log filename to use for the bibupdate_ messages.

-m --mrlookup     Use mrlookup to update bibtex entries (default)

-M --mathscinet   Use mathscinet to update bibtex entries

  By default mrlookup_ is used to update the BibTeX_ entries in the database.
  This has the advantage of being a free service provided by the American
  Mathematical Society. A second advantage is the more flexible searching is
  possible when mrlookup_ is used. It is also possible to update BibTeX_
  entries using MathSciNet_, however, these searches are currently only possible
  using the ``mrnumber`` field (so this option only does something if combined
  with the --all option or the -check-all-option).

-q, --quietness  Print fewer messages

  There are three levels of verbosity in how bibupdate_ describes the changes that
  it is making. These are determined by the q-option as follows::

     bibupdate     bibfile.bib    (Defalt) Report all changes
     bibupdate -q  bibfile.bib    (Warning mode) Only print entries that are changed
     bibupdate -qq bibfile.bib    (Quiet mode) Only printer error messages

  By default all changes are printed (to stdout, although a log file can be
  specified by the -l option). In the default mode bibupdate_ will tell you what
  entries it changes and when it *is not* able to find the paper on the database
  (either because there are no matches or because there are too many). If it is
  not able to find the paper and bibupdate_ thinks that the paper is not a
  preprint then it will mark the missing entry with an exclamation mark, to
  highlight that it thinks that it should have found the entry in mrlookup_ but
  failed. Here is some sample output::

    ------------------------------
    ? did not find Webster:CanonicalBasesHigherRep=Canonical bases and higher representatio
    ++++++++++++++++++++++++++++++
    + updating Weyl=
    + publisher: Princeton University Press
    +         -> Princeton University Press, Princeton, NJ
    ------------------------------
    ? did not find Williamson:JamesLusztig=Schubert calculus and torsion
    ------------------------------
    ! did not find QSAII=On Quantitative Substitutional Analysis

  Each bibtex_ entry is identified by the citation key and the (first 50
  characters of the sanitised) document title, as specified by your database. Of
  the three missed entries above, bibupdate_ thinks that the first and third are
  preprints (they are not marked with an !) and  that the final article should
  already have been published. With the entry that bibupdate_ found, only the
  publisher field was changed to include the city of publication.

  In *warning mode*, with the -q option, you are "warned" whenever changes are
  made to an entry or when the paper is not found in the external datbase. That
  is, when papers are found (with changes) or when they are missed and
  bibupdate_ thinks that they are not preprints. In *quiet mode*, with the -qq
  option, the program only reports when something goes wrong.

-r  --replace  Replace the existing bibtex file with the updated version

  Replace the existing BibTeX_ file with the updated file. A backup version of
  the original BibTeX_ is made with a .bak extension. it is also possible to
  specify the output filename as the last argument to bibupdate.

-w WRAP_LEN --wrap WRAP_LEN    wrap bibtex fields to specified width

  Limits the maximum line length in the output BibTeX_ file. In theory this is
  supposed to make it easier to compare the updated BibTeX_ file with the
  original one, however, in practise this doesn't always work.

Known issues
------------

There are a small number of cases where bibupdate_ fails to correctly identify
papers that are listed in MathSciNet_. These failures occur for the following
reasons:

* Apostrophes: Searching for a title that contains, for example, "James's Conjecture" 
  confuses mrlookup_.
* Ambiguous spelling: Issues arise when there are multiple ways to spell a
  given author's name. This can often happen if the surname involves accents
  (such as Koenig and K\\"onig). Most of the time accents themselves are not a
  problem because the AMS is LaTeX_ aware.
* Pages numbers: electronic journals, in particular, often have strange page
  numbers (for example "Art. ID rnm032, 24"). bibupdate_ assumes that page
  numbers are always given in the format like 4--42.
* Occasionally MathReviews combines two or more closely related articles. This
  makes it difficult to search for them.

All of these problems are due to idiosyncrasies with mrlookup_ so there is not
much that we can do about them.

Installation
============

You need to have Python_ installed. In principle, this program should work on
any system that supports Python_, however, I only promise that it will work
on an up-to-date mac or Linux system. In the event that it does not install I
may not be able to help you as I will not have access to your system.

From the command line type::

      pip install bibupdate

Instead of pip, you should also be able to use easy_install. The program should
run on python 2.7 and 2.8...I haven't tried python3. You can also clone or
download_ the git repository and work directly with the source.

Support
=======

This program is being made available primarily on the basis that it might be
useful to others. I wrote the program in my spare time and I will support it in
my spare time, to the extent that I will fix what I consider to be serious
problems and I may implement feature requests. Ultimately, however, my family,
research, teaching and administrative duties will have priority.

To do
=====

- More intelligent searches using MathSciNet_.
- Interface to the arXiv_? In principle, this is easy to do although,
  ultimately, it would probably not work because the arXiv_ blocks frequent
  requests from the same IP address in order to discourage robots.

AUTHOR
======

`Andrew Mathas`_

bibupdate_ Version 1.2. Copyright (C) 2012-14 

GNU General Public License, Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU_General Public License (GPL_) as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

.. _`Andrew Mathas`: http://www.maths.usyd.edu.au/u/mathas/
.. _arXiv: http://arxiv.org/
.. _BibTeX: http://www.bibtex.org/
.. _bibupdate: https://bitbucket.org/AndrewsBucket/bibupdate
.. _download: http://bitbucket.org/AndrewsBucket/bibupdate/downloads/
.. _GPL: http://www.gnu.org/licenses/gpl.html
.. _hyperref: http://www.ctan.org/pkg/hyperref
.. _LaTeX: http://en.wikipedia.org/wiki/LaTeX
.. _MathSciNet: http://www.ams.org/mathscinet/
.. _mrlookup: http://www.ams.org/mrlookup
.. _Python: https://www.python.org/
