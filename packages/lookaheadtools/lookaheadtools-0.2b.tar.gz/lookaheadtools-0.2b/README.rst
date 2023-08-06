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

As seen in the example, myLookaheadIter[0] returns the value that will 
be returned by next(myLookaheadIter) but without consuming it.
Arbitrary lookahead distance is supported.  Attempts to lookahead 
past the end of the iterator will return None.  The look-ahead index 
can be any slice with positive indices.

Classes Provided
----------------

Lookahead(object) -- Convert any iterator into a look-ahead iterator.

LinesOf(object) -- Iterate line-by-line over a string, emulating text file
iteration.

Lexpos (a named tuple) -- Convenience class for capturing lexical 
tracking information.

FileLookahead(Lookahead) -- FileLookahead() is a specialization of the
Lookahead() class that iterates by characters over a text file with 
full lexical position tracking.

LexAhead(FileLookahead) -- LexAhead() is a specialization of 
FileLookahead() that includes some simple tokenizing utilities, 
stopping short of being a full tokenizer.  See tokenizertools 
for a module that builds a tokenizer on top of LexAhead().

