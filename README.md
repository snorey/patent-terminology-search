# Bilingual Patent Terminology Search

While multilingual patent data is increasingly readily available online, the tools that exist to access it are generally written for the needs of patent owners and their attorneys.  Translators and others needing to conduct on-the-fly research on patent language and terminology, or to harness the vast body of patent translation work already in the public domain, will find the otherwise amazing interfaces offered by today's patent websites quite unsatisfactory. This project seeks to bridge that gap by providing a robust query interface for a corpus of paired patent filings in two different languages.

While this project currently supports only US and Korean (KR) patents and the English and Korean languages, it can readily be extended to encompass an arbitrary number of countries and languages.  

## Implementation and installation

### Manual setup

To run this project, you must have:
1. A machine running Python 2.7, with enough disk space to handle the files you want to process (the source files for the example corpus of 6975 patent pairs weighed in at approximately 10 gigabytes).
2. A recent version of metapy.
3. If you will be converting PDFs, version 20140328 of PDFMiner.

With those requirements in place, simply follow these steps:
1. Clone or download the project from Github to the desired directory on your machine.
2. Populate the "KR" and "US" directories, as well as "mappings.tsv", either from the sample corpus or your own files.  If using the sample corpus, simply unpack the GZIP file directly into the project directory.

Please note that this has only been tested on systems running Ubuntu 16.04 and 18.04, although I am not aware of any reason why it would not -- in principle -- work on other systems.

### Using Vagrant

If you have Vagrant and VirtualBox installed, and at least 5 G of available disk space, you can install a fully-functioning version of this project on a local virtual server very easily:

1. Create new folder or directory on your local machine.
2. Download the Vagrantfile and place it in the new folder.
3. In a terminal or command shell, move to the new folder and then type "Vagrant up".

That's it! This will automatically set up and provision an Ubuntu 18.04 server instance running Apache and Python 2.7, with this project and the example corpus pre-loaded. Once installation is complete, you can access the query interface at http://localhost:8080/cgi-bin/search.py. 

### Querying the example corpus

The example corpus, which is automatically installed on the Vagrant machine, consists of 6975 paired US and KR patent filings.

If you are using the Vagrant machine, once it has completed installation you should be able to access the query interface at http://localhost:8080/cgi-bin/search.py

If you are installing the project manually, you have two choices.  If you are a running a CGI-equipped local server, you can set up the internal web interface by (1) moving the contents of the "cgi-bin" directory to the appropriate location, and (2) adding the project directory to your system's PATH or PYTHONPATH variable so that the CGI scripts can access them.  

Alternatively, you can simply enter queries from the command line, using query.py:

> python query.py user_file=foo.txt include_kr=" " include_kr_type=exact 

(As with the web interface, all arguments are optional, although the result won't be very useful if none of them are filled in.)

### Adding new documents or corpora

## Usage

As above, ordinarily this project would be interacted with via either a web browser or the command-line interface.  However, it can also be interacted with programmatically within Python, using query.py and the Query class.

[EXAMPLE]

### Evaluating performance

Currently performance evaluation is limited to the Mean Average Precision metric.  For evaluation purposes, a "relevant" document is considered to be one that shares at least one IPC subgroup with the document it is being compared to.  

Initial testing shows that the MAP obtained based on this definition is quite low, typically around 0.22 (regardless of whether the first 5 documents are evaluated or only the first one).  As there are more than 70,000 groups and subgroups in the current IPC, an exact subgroup match may be an unrealistic metric for performance on the relatively small corpus of 6,975 patents used as an example in this project.  Alternatively, some of this low performance may be due to flaws in how the patent texts have been prepared (i.e. PDF artifacts like word fragments or missing spaces giving rise to seemingly "important" low-frequency words that lead to incorrect similarity judgments), or to unexpected stemming or tokenization behavior.

By default, the provided evaluation function will run 100 tests and look at the first 5 ranked results.

[EXAMPLE]


## Overview of functions

The functions in this module are distributed across several files:

### Query.py

This is the basic query handling library.  It defines the Query class and provides a command-line interface.

[FUNCTIONS]


### Similarity.py

[FUNCTIONS]

### Corpus_setup.py

This library contains utility functions for cleaning and setting up a corpus.  

[FUNCTIONS]

### Kosimple.py (and koverbs.txt)

This library implements a simple set of utilities for processing Korean-language text. Although the available tools for NLP in Korean have multiplied considerably, I have not been able to find an adequately lightweight and efficient stemmer that is also open-source.  Accordingly, I have used a simple homemade stemmer for this project.

Internally, the Kosimple library models Hangul text through a verbose but unambiguous ASCII romanization.

[FUNCTIONS]


### Search.py

[FUNCTIONS]

### Patents.py

This is a set of utility scripts for cleaning up text extracted from PDF patents.  (Using PDFMiner to handle PDFs will obviate many of the issues that arise with manually-extracted text, but not all of them (e.g. PDFMiner will not address sentence and word breaks between pages).)

[FUNCTIONS]
