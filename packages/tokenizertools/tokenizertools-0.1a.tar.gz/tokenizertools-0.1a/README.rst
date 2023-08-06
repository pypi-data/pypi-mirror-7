==============
tokenizertools
==============

Text file tokenizers that support multiple start states
and lexical tracking implemented as standard Python iterators.

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
list of rules. ::

  import tokenizertools as tt
  class MyTokenizer(tt.RegexTokenizer):
      spec = [
          (r'[a-zA-Z][a-zA-Z0-9_]*',Token.typeIdent), # idents and keywords
          (r'[0-9]+\.[0-9]+',Token.typeFloat), # floats
          (r'[0-9]+', Token.typeInt), # ints
          (r'\s*',None), # ignore white space
      ]

Nothing else needs to be defined.  All methods are inherited.
Instantiate a lexer and commence parsing.
The specification rules are compiled and cached on creation
of the first instance.::

  tokenizer = MyTokenizer()
  with open('foo.bar') as f:
      tokenStream = Lookahead(tokenizer.lex(f, f.name))
      compiledStuff = myParser.parse(tokenStream)
