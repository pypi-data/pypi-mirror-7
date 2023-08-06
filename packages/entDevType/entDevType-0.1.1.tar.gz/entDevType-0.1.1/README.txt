====================
EntropyDeviationType
====================

EntropyDeviationType is an extension that is intended for finding
data hidden within other data with no knowledge of the data itself.
Specifically, the intended use case is to identify executable files
(Portable Executables specifically) embedded in non-executable files.
For example, malware hidden within a Microsoft Word or PDF document.
This is a common occurrence within Advanced Persistent Threat (APT)
style attacks which leverage client-side attacks in common business
office file formats and often follow the generic pattern that within 
the exploit is a XOR encrypted executable that is dropped to the 
compromised system and then the host document is cleaned to remove the 
exploit.

The module contains two classes, ``entropyDeviationType`` and 
``xorTableSearchType``. Both classes are intended as proof of concepts
and not immediately exportable to production. This package also 
contains an example utility, ``edfind.py``, which serves as both an
immediately usable utility and as a rough primer on how to use the
extension to quickly analyze and locate rogue data hidden within
benign information streams.

DISCLAIMER
==========

**YOUR MILEAGE MAY VARY. AS WITH EVERYTHING TEST THOROUGHLY YOURSELF
BEFORE UTILIZING IN PRODUCTION CODE. THIS MODULE HAS NOT RECEIVED
EXTENSIVE TESTING AND MAY CONTAIN BUGS NO WARRANTY, EXPLICIT OR
IMPLICIT IS PROVIDED. ITS THE INTERNET. TRUST BUT VERIFY**

BUILDING
========
 - Requires: 
	- C++ compiler that supports C++11
	- Python >2.3 & <3.0 (tested only on 2.7)
	- The boost::python library

$ ./setup.py build
# ./setup.py install

The C++ classes can be extracted and utilized with only a C++ compiler 
that supports C++11. 

MORE INFORMATION
================
Included with this distribution is a PDF file in the ./doc/ directory 
that contains fairly verbose documentation that outlined both the 
Python and C++ API, structure and intended usage. It further outlines 
usage of the included example utility, edfind.py, and does so by 
explaining its usage on example document files. 

In short, I really tried to type this all up in reST format, but that
is just nuts. I instead elected to have a text file that provides a
very basic description, that will play friendly with 80x60 terminals 
and a PDF document that describes everything in detail that doesn't 
have to overly worry a whole lot about your particular environment for 
viewing the data. Cheers.
 
