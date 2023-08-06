==============
lookaheadtools
==============

The lookaheadtools module extends generic iterators to support look-ahead,
and also provides some convenient look-ahead iterators that are useful for
processing text files.

Lookahead is implemented by extending iterators with support for __getitem__().
For example: ::

  import lookaheadtools as la
  looker = la.lookahead(iter([0,1,2,3,4]))
  assert looker[3] == 3
  assert looker[0] == 0
  assert looker[1000] == None
  assert looker[0:9:2] == [1,2,4]
  assert next(looker) == 0
  assert looker[0] == 1

As seen in the example,
``myLookaheadIter[0]`` returns the value that will be returned by
``next(myLookaheadIter)`` but without consuming it.
Arbitrary lookahead distance is supported.  
Attempts to lookahead past the end of the iterator will return None. 
The look-ahead index can be any slice with positive indices.

Classes Provided
----------------

Lookahead(object)
.................

Convert any iterator into a look-ahead iterator.
Use ``Lookahead()`` by instantiating it on any iterator: ::

  import lookaheadtools as la
  looker = la.Lookahead(iter([0,1,2,3,4]))
  
Now ``looker`` is an iterator that supports the normal iterator protocol, and
in addition implements ``__getitem__`` so that indexing for positive integers
is supported.
``looker[0]`` peeks at the value that will be yielded by a call
to ``next()``, but without consuming it.  
``looker[n]`` looks ``n`` positions further ahead.
If ``n`` is beyond the end of the underlying iterator, ``None`` is returned.

``Lookahead()`` implements the methods ``__iter__()`` 
and ``__next__()`` to satisfy
the iterator protocol, and also implements ``next()`` by simply delegating
to ``__next__()`` for backwards compatibility with Python 2.6 and 2.7.

LinesOf(object)
...............

Iterate over a string line-by-line, emulating text file iteration.
If string ``s`` and find ``f`` contain the same text, then the following
code fragments are equivalent: ::

  for ln in f:
      print ln

  for ln in LinesOf(s):
      print ln

The ``FileLookahead`` and ``LexAhead`` objects described below 
expect a line-structured iterator, commonly an open file.
The ``LinesOf`` iterator allows the same lexical processing to 
be used on strings. For example: ::

  with LinesOf(s) if useString else open(f) as f:
      fla = FileLookahead(f)
      ...

Lexpos, a named tuple
.....................

``Lexpos`` is a convenience class for capturing lexical tracking information.
The named fields of the tuple are: ``lineno``, ``colno``, ``charpos``, 
and ``cookie``.
The lookaheadtools module sets ``lineno`` to the line number of the next
character that ``next()`` will yield, ``colno`` to the column number,
and ``charpos``
to the absolute file offset so that a ``seek()`` to that file position will
find the character.

The ``cookie`` field is set to a value provided by the user. 
The common idiom is to set ``cookie`` to be the file name, but it can be
any arbitrary object.
``cookie`` is simply handed back in instances of Lexpos(), without processing.

FileLookahead(Lookahead)
........................

``FileLookahead(anOpenFile, cookie=None)`` is a 
specialization of the ``Lookahead()`` class that
iterates over an open file that is assumed to be a text file structured
into lines by newline characters.
``FileLookahead()`` yields characters, and look-ahead indices select
characters from the file.
``FileLookahead()`` provides lexical tracking of line number, column number,
and absolute file offset, and in addition can provide the entire line
containing the current iterator position. 

In this example, ``fla`` will iterate over ``someOpenFile``, and the tracking
cookie is set to the file's name. ::

  fla = FileLookahead(someOpenFile, someOpenFile.name)

Property ``lexpos`` returns a ``Lexpos`` instance corresponding to the
lexical position of the character that will be yielded by ``next()``.
Property ``curln`` returns the entire line that contains the character
that will be yielded by ``next()``.  Together, the ``lexpos`` and ``curln`` 
properties greatly simplify error reporting.

LexAhead(FileLookahead)
.......................

``LexAhead(anOpenFile, cookie=None)`` is a 
specialization of ``FileLookahead`` that include some
simple lexical processing utilities that can be used to extract 
token strings. 
``LexAhead`` stops short of being a full tokenizer.
See tokenizertools for a module that builds a tokenizer on top of
``LexAhead``.

The predicate ``eol()`` returns ``True`` if the next character is a newline.

The ``consume()`` method without parameters removes and 
returns the next character 
from the file.  This is identical functionality to ``next()``.
Optionally, ``consume(require)`` can take a ``str`` or ``set`` parameter
``require``,
and will assert that the next character in the file is in ``require``. 
This creates a guarded form of next that can be used to protect
against internal logic errors in lexing and parsing code.

The ``accept()`` method conditionally takes characters from the iterator.
``myIter.accept(someTest)`` examines the next character, and if it passes
the test consumes and returns it.  ``myIter.accept(someTest, n)`` will consume
a string of up to ``n`` characters.  If ``n`` is ``None``, ``accept``
will consume as many characters as pass the test.
The test may be a string, a set, or a callable taking a single character
and returning a boolean.
If the test fails, ``accept()`` returns the empty string without consuming
any characters from the iterator.

The ``accept_not()`` method is nearly the logical negation of ``accept()``, 
in that it accepts characters that do NOT pass the test. 
There is an important difference, however, in that ``accept_not()`` will not
accept a newline in any case, so it always stops at line boundaries.
A useful idiom is ``someIter.accept_not('',None)``, which will consume the
balance of a line up to but not including the terminating newline.

Regular expression matching is provided by ``accept_re(aMatcher)``.  
The parameter ``aMatcher`` is presumably a compiled regular expression, 
but could be any instance implementing ``match()`` and ``group(0)``. 
All characters at the start of the buffer that match the regular 
expression are consumed and returned. 

A second optional parameter can be used to supply a compiled regular
expression that determines how far ahead the look-ahead buffer is
constructed.  
The default is to extend the look-head buffer through at 
least one newline, and then further through at least one non-white-space 
character, if possible.  
Most interesting tokens should be found in the
lookahead buffer without running off the end, but if the default is
not sufficient then the user may provide a different look-ahead rule
in the form of a compiled regular expression.
If the entire look-ahead buffer is consumed without matching the
expression being sought, ``accept_re()`` will silently return the empty
string, so it is important that the look-ahead buffer construction
expression extends the buffer sufficiently long to contain the token
being sought.



