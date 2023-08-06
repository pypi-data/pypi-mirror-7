===========
PyJoke
===========

PyJoke is a package for fetching the perfect joke in a database.
You give a sentence, you get a joke. Isn't that great? Common usage is::

    #!/usr/bin/env python

    from pyjoke.PyJoke import *

    p = PyJoke()
    print p.getTheJoke("keywords listed as such")
