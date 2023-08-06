Description
===========

A package that uses linguistic analysis in order to determine the author of a document. Currently version 0.0.1.

Installation
------------

1. Install the package from the PyPi homepage (run `setup.py install`) 
2. Import the package in your project (`from authorid import authorid`)
3. You're good to go! You can now run individual functions (i.e. `authorid.run()`) by calling the package name. 

Usage
-----

`authorid` is a package meant to help analyze linguistic features of files and determine their potential author, provided a list of attributes. 
In order to invoke the primary utility, simply run `authorid.run()` and you will be prompted for a file containing the mystery text. After analysis
is complete, the program will print a signature for that file, and prompt for a directory where `.stats` files are stored. 

If this is the first time you are running `authorid`, exit out of the main program now, and copy the signature list to another file, ending with the 
signature `.stats`. A sample .stats file may look like the following: 

``
first last
4.41553119311
0.0563451817574
0.02229943808
16.8869087498
2.54817097682
``

Remember to order the information correctly in order to ensure optimal results. Complete this step for various files, and when you have a directory containing
your made `.stats` files (this process will be automated in `0.0.2`), run `authorid.run()` once more, this time with a mystery file and providing the directory with
your STATS files. The program will compare signatures with those in the list and provide a "best match" author.

Other utility functions are also available, which are listed below (also open sourced on GitHub):

``
def clean_up(s)
def average_word_length(text)
def type_token_ratio(text)
def hapax_legomana_ratio(text)
def split_on_separators(original, separators)
def average_sentence_length(text)
def avg_sentence_complexity(text)
def get_valid_filename(prompt)
def read_directory_name(prompt)
def compare_signatures(sig1, sig2, weight)
def read_signature(filename)
def run()
``

Note that `text` is a list of strings. 