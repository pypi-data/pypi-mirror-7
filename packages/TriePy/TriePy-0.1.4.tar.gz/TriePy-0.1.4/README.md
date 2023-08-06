TriePy
===========

A simple trie implementation in Python

This implementation utilizes a dictionary as its backing
data structure. Essentially, it is creating nested dictionaries.


Example
----------
    >>> from trie import TriePy
    >>> t = TriePy()
    >>> t.addWord("dog")
    >>> t.addWord("doggy")
    >>> t.addWord("dogs")
    >>> t.containsWord("dog")
    True
    >>> t.containsWord("dogg")
    False
    >>> t.root
    {'d': {'o': {'g': {'!THIS_IS_THE_END!': {'word': 'dog'}, 's': {'!THIS_IS_THE_END!': {'word': 'dogs'}}, 'g': {'y': {'!THIS_IS_THE_END!': {'word': 'doggy'}}}}}}}


Unit Testing
----------
nose is used for unit testing and simple unit tests
can be run with the following in the source trie directory:
    `nosetests`


Installation
----------
You can install this as usual with `setup.py`. 
    `python setup.py install`

You can also install this via pip.
    `pip install TriePy`

The usual "use virtualenv to test first" warnings apply.
