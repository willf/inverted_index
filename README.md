Inverted Index
==============

A simple in-memory inverted index system, with a modest query language.


    i = inverted_index.Index()
    i.add(1, "this is the day they give babies away with half a pound of tea")
    i.add(1, "if you know any ladies who need any babies just send them round to ")
    i.add(2, "babies are born in the circle of the sun")
    results, err = i.query("babies")
    print(results)
    {1,2}
    results, err = i.query("babies AND ladies")
    print(results)
    {1}
    i.add(3, "WHERE ARE THE BABIES", tokenizer=lambda s:s.lower().split())
    results, err = i.query("babies")
    print(results)
    {1,2,3}

Any hashable object can be the "document", and a tokenizer can be specified to tokenize the
text to index. There are also `add_token` and `add_tokens` methods to directly index on individual
tokens.

The query language is very simple: it understands AND and OR, NOT, and parentheses. For example:

    term OR term
    term AND term OR term
    (term AND term) OR term
    NOT term
    NOT term AND (term OR term)
    
`AND`, `OR`, and `NOT` have equal precedence, so use parentheses to disambiguate.

I'm pretty sure you don't want to use this in production code :)
