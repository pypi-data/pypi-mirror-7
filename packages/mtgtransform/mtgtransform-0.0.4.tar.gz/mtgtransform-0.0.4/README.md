mtgtransform
============

Magic the Gathering deck transformator. Used for import/export of decks between
different websites.

So far it only supports moving decks from http://mtgtop8.com to
http://tappedout.net.

# Usage

For usage help, type `./mtgtransform.py -h`.

# Examples

Transforming from one file to another:
```
./mtgtransform.py inputfile > outputfile
./mtgtransform.py --sideboard inputfile > outputfile_sb
```

Note that sideboard transformation is performed in a separate step.

It can also take input from stdin so on OSX the content from the source site
can be copied into clipboard and transformed with
```
pbpaste | ./mtgtransform.py | pbcopy
```

This will add the transformed deck to the clipboard so it can be pasted
directly into the destination website.


# Testing

Running the tests requires pytest. Install dependencies with
```
pip install -r requirements.txt
```
and then run tests with
```
py.test
```

# TODO

Add setup.py for install.
