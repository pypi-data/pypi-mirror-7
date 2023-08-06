mtgtransform
============

Magic the Gathering deck transformator. Used for import/export of decks between
different websites.

So far it only supports moving decks from http://mtgtop8.com to
http://tappedout.net.

# Installation

Install the extension with one of the following commands:

```
$ easy_install mtgtransform
```

or alternatively if you have pip installed:

```
$ pip install mtgtransform
```

# Usage

Type `mtgtransform -h` for usage help.

## Examples

Transforming from one file to another:

```
$ mtgtransform inputfile > outputfile
$ mtgtransform --sideboard inputfile > outputfile_sb
```

Note that sideboard transformation is performed in a separate step.

It can also take input from stdin so on OSX the content from the source site
can be copied into clipboard and transformed with

```
$ pbpaste | mtgtransform | pbcopy
```

This will add the transformed deck to the clipboard so it can be pasted
directly into the destination website.

# Development

## Testing

Running the tests during development requires pytest. Install dependencies with

```
pip install -r requirements.txt
```
and then run tests with
```
py.test
```
