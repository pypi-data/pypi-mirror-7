Numbers-Extractor
=================

Extract numbers from a string and return a list of int.

Install
-------

pip install numbers_extractor 

or

easy_install numbers_extractor 


Usage
-----

numbers_extractor(string[, multiple=True])

*string* must be a text that contains zero, one or # numbers.   
If *multiple* is set to True (default) return a list of # numbers 
that can be empty if no numbers are found. If False, return the first number found, or None.

Example:

    >>> from numbers_extractor import numbers_extractor
    >>> numbers_extractor("20 is 10 plus 10")
    [20, 10, 10]
    >>> numbers_extractor("20 is 10 plus 10", multiple=False)
    20
    >>> numbers_extractor("no numbers here")
    []
    >>> numbers_extractor("no numbers here", multiple=False)
    >>>
