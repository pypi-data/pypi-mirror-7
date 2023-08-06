==============
tokenizertools
==============

Tokenizertools implements tokenizing iterators that support
``__iter__`` and ``__next__`` for lexing text files.

Classes provided:

* Tokenizer -- Base class.
* RegexTokenizer -- Python re-based tokenizer.
* FlexTokenizer -- Interface to flex-based tokenizer.
* TokenizeAhead -- A look-ahead iterator that can wrap any tokenizer.

Overview
--------

The class ``RegexTokenizer`` implements a tokenizer using the ``re`` 
module to recognize tokens in the input stream.
Tokens and actions are defined by rules.
The tokenizer calls user action functions associated with each rule.
In most cases, the user action function can simply be a ``@classmethod``
constructor of a user-provided token class.

A simple example here will clarify many points:

Example 1
.........

A simple tokenizer for identifiers, keywords, integers, and floats.

Step 1
++++++

Derive a tokenizer class from ``RegexTokenizer``::

  import tokenizertools as tt
  class MyTokenizer(tt.RegexTokenizer):

Step 2
++++++

Create a specification by defining rules to recognize tokens.
Each rule is specified as a tuple.
The first element of the tuple is a regular expression that will
be compiled by ``re`` and used to match a token.
The second element of the tuple is a user-provided callable that 
will be passed
the recognized text, along with the current lexical position.

In this example, the user class ``Token`` implements constructors
as ``@classmethod`` functions, and these serve as the callables in
each lexical rule.

Rules are specified in the class variable ``spec``, which is a
list of rules.
Order is significant.
Rules will be tested in the order provided::

  import tokenizertools as tt
  class MyTokenizer(tt.RegexTokenizer):
      spec = [
          (r'[a-zA-Z][a-zA-Z0-9_]*',Token.typeIdent), # idents and keywords
          (r'[0-9]+\.[0-9]+',Token.typeFloat), # floats
          (r'[0-9]+', Token.typeInt), # ints
          (r'\s*',None), # ignore white space
      ]

Nothing else needs to be defined.  All methods are inherited.

Step 3
++++++

Instantiate a lexer and commence parsing.
The specification rules are compiled and cached on creation
of the first instance.::

  tokenizer = MyTokenizer()
  with open('foo.bar') as f:
      tokenStream = Lookahead(tokenizer.lex(f, f.name))
      compiledStuff = myParser.parse(tokenStream)

Commentary
++++++++++

Let's go back and examine Step 2 for a further explanation of the
rules.

Each rule is a tuple of the form (regular-expression, callable).
In three cases, the callables are ``@classmethods`` of the user-provided
class ``Token``. 
Since white space is simply consumed, for the white space rule the
action is set to ``None``, which causes the generated lexer to simply 
consume the recognized string, however the lexer will keep up lexical position
accounting.
It should probably be noted that the above lexer is incomplete, in that
punctuation characters, etc, are not recognized -- this is to keep the
example simple for the moment.
A practical lexer will want to recognize any possible input.

The callable in each rule is passed the recognized string and lexical
position information.
The user-defined token class might be something like this: ::

  class Token(object):
      _keywords = {'if':'IF','while':'WHILE','else':'ELSE'}
      def __init__(self, tokenType, value, lexpos):
          self.type = tokenType
          self.value = value
          self.lexpos = lexpos
      @classmethod
      def typeInt(cls, s, lexpos):
          return cls('INT', int(s), lexpos)
      @classmethod
      def typeFloat(cls, s, lexpos):
          return cls('FLOAT', float(s), lexpos)
      @classmethod
      def typeIdent(cls, s, lexpos):
          try:
              return cls(cls._keywords[s], s, lexpos)
          except KeyError:
              return cls('ID', s, lexpos)

The user-defined Token can be anything that is convenient for the
application.
The example shown here is simple and generic -- a token consists
simply of a type key, some kind of type-appropriate value, and the
lexical position captured by the lexer.

The constructors for ints and floats are simple and obvious.
The token type is set to the appropriate key, and the string
matched  by the lexer is cast to a numeric value of the appropriate type.

The ``typeIdent`` constructor is more interesting.
Creating a lexer rule to recognize each keyword individually leads to a
large, slow, inefficient lexer. 
It is much more efficient and the code far easier to maintain if 
instead we use a single
rule that captures both keywords and identifiers, and then filter those
at token-creation time.
The code shown above is one simple way of providing keyword filtering,
and returning the appropriate token type.

(Some aside remarks: Recognizing individual keywords in a lex/flex lexer
leads to bloated, inefficient lexers as well -- despite nearly every example
showing keyword matching rules.
Keyword filtering of some nature is a win in your flex-based lexers, too.)
     
Lexer Specification
-------------------

The lexer is specified by the class variable ``spec``.

Order is significant -- token matching attempts are made in the order
that the rules are presented.
In Example 1, it would be an error to put the rule for matching
integers before the rule for matching floating point numbers, because
the integer match would succeed at the decimal point, leaving the
decimal point and fraction in the input stream.
Note that this behavior is slightly different from lex/flex.  
A flex lexer will prefer the longest possible match, and break ties
by taking the earlier rule.
The ``RegexTokenizer`` class follows the Python ``re`` module behavior --
it is always greedy.  
It will take the first match it finds while
scanning the rules in the specified order.

Rules are tuples of one of two forms: ::

 (regular-expression, callable, optional-start-state-list).
 (regular-expression, (callable,start-state), optional-start-state-list).

The regular expression string is compiled by the ``re`` module without any
modification, so all ``re`` syntax applies.  

The second field of the tuple has two forms.
In the first form it is any callable that takes a string and a lexical 
position tuple, and returns a token.
In the second form, it consists of a callable and a start state 
identifier.  
The lexer will transition to the start state after the
token is recognized.

In many cases, it is sufficient to transition to a fixed start state after
recognition of a particular token. 
Some lexers, however, may need to examine the recognized string
in order to compute a start state.
In this case, the start-state should be set to the reserved start state
identifier ``'?'``.
This changes the definition of the callable -- the callable now instead
of simply returning a token, must return a tuple of the form: ::

  (token, start-state)

in which case the lexer will transition to the computed start-state and
return the token.

The third field of the rule tuple is an optional list of start states
in which the rule applies.  All start states are exclusive -- a rule will
only be used if the lexer is in one of the listed start states.
The default list, as well as the default start state, is ``[0]``.  
Start states can be any hashable, although using descriptive strings
is simple and makes the parser more readable.
The start state name ``'?'`` is reserved for computed start states.

Lexer Methods
-------------

The user-define lexer inherits from ``RegexLexer`` the following methods:

* __init__()
* __iter__()
* next()
* __next__()
* begin()
* discard()
* consume()

``__init__()`` looks for a cached copy of the compiled lexer.
If none is found, it compiles one.  
In any case, it returns a new instance of the lexer.

``__iter__()`` supports the standard iterator protocol.

``next()`` provides backward compatibility to the 2.6/2.7 iterator
protocol, and simply delegates to ``__next__()``. 

``__next__()`` supports the standard iterator protocol. 
Each call returns a token.

``begin()`` allows setting the lexer to an arbitrary start state from
outside of normal rule processing.
Explicitly calling ``begin()`` should rarely be needed.
Outside of error recover and specialized cases of initialization,
start states should probably be set by the rule or an action callable.
It is worth noting that if the lexer instance is wrapped by a
``lookaheadtools.Lookahead`` iterator, ``begin()`` will have limited
utility since the ``Lookahead`` iterator may have lex'ed ahead and 
buffered an arbitrary number of tokens.

``discard()`` is called whenever a character is discarded from the input.
The lexer will automatically discard a character any time ``__next__()`` fails to
find a match on any rule.

``consume()`` is a guarded form of ``next()``.  ``consume(guardFunction)`` asserts
``guardFunction(<currentToken>)`` before returning the current token.
The guard function can be any callable taking a single parameter, and
returning a boolean.
It will be passed the current token, and should return ``True`` if the
token passes the screen.  For example, suppose the predicate ``isNumber``
is defined for the class Token: ::
  
  class Token(object):
  ...
  @classmethod
  def isNumber(cls, aToken):
      return aToken.type in frozenset(['INT','FLOAT'])
  ...

Then a parser might use ``consume()`` as shown here: ::

  tkn = myLexer.consume(Token.isNumber)

which will raise ``AssertionError`` if the next token is not a numeric
literal. 
This is a useful idiom for detecting internal logic errors in the parser.

Lookahead Lexers
----------------

Since instances of ``Tokenizer()`` support the standard iterator protocol,
a lookahead lexer could be constructed by simply instantiating
``lookahedatools.Lookahead()`` on an instance of ``Tokenizer()``. 

A more convenient lookahead lexer is provided by the class ``TokenizeAhead``,
which is a specialization of the ``lookaheadtools.Lookahead`` class. 
``TokenizeAhead`` provides to additional methods:

* consume(require=None)
* accept(require)

``consume()`` is a guarded form of ``next()``.  
The definition is identical to ``Tokenizer.consume()``, but accounts
for look-ahead buffering.

``accept(guardFunction)`` is a guarded form of ``next()`` that will
return the next token if ``guardFunction(<next token>)`` is ``True``,
otherwise it will return ``None``.
This is convenient in situations where parsing decisions are made
by looking ahead at the next token, and either consuming it as part
of the parse, or leaving it in the token stream for some other 
parsing function to consume.

Hints and Useful Idioms
-----------------------

A few usage hints in no particular order.


Processing Included Files
.........................

Behavior similar to the C preprocessor ``#include`` directive is
simple to implement.
Since an instance of Tokenizer contains all the state necessary to 
keep track of current file position, handling an include is a simple
matter of creating a new lexer instance and directing the parser
to use the new lexer. ::

  lexerStack = []
  curLexer = MyLexer(aFile,aFile.name)
  while True:
      try:
          ....
          tkn = next(curLexer)
          if tkn.type == 'INCLUDE':
              lexerStack.append(curLexer)
              curLexer = MyLexer(anotherFile, anotherFile.name)
          ...
      except StopIteration:
          try:
              curLexer = lexerStack.pop()
          except ????:
              break

Practical Recursive-Decent Parsing
..................................

Here is one possible approach to recursive decent parsing. ::

  # Make a look-ahead tokenizer.
  tokenSource = la.Lookahead(MyLexer(someFile))

  # Make classes for abstract syntax tree nodes.
  # Each class is self-parsing, via the classmethod parse().
  class SyntaxTreeElement(object):
      pass
  
  class STFoo(SyntaxTreeElement):
      first = frozenset([...token types...])
      def __init__(self, particulars):
          pass
      @classmethod
      def parse(cls, tokenSource):
          if tokenSource[0].type in cls.first:
              t = next(tokenSource)
              ... continue parsing...
              return cls(stuffFoundWhileParsing)

Essential elements:

* The token source is a lookahead tokenizer.
* Each element of the syntax tree is defined by a class.
* Syntax tree classes are self-parsing, via the ``@classmethod parse()``.
* The ``parse()`` method is a constructor for the class.
* The ``parse()`` methods of the various syntax tree classes are 
  mutually recursive.
 
Using accept()
..............

Here the Practical Recursive-Decent example above is re-written using
``accept()``.  ::

  class SyntaxTreeElement(Object):
      @classmethod
      inFirst(cls, aToken):
          return aToken.type in cls.first

  class STFoo(...
      @classmethod
      def parse(cls, tokenSource):
          tkn = tokenSource.accept(cls.inFirst)
          if tkn == None:
              return None
          ... parse some more ...
          return cls(stuff)

Future: FlexLexer
-----------------

The class ``FlexTokenizer(Tokenizer)`` is currently in development.
Eventually, a ``FlexTokenizer`` will be a drop-in replacement for 
a ``RegexTokenizer``, but will provide a Python interface to a flex lexer
implemented as a C extension.

