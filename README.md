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
