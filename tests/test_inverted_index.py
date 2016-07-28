# -*- coding: utf-8 -*-

import unittest

from .context import inverted_index


class InvertedIndexTextSuite(unittest.TestCase):
    def test_create_index(self):
        i = inverted_index.Index()

    def test_add_token(self):
        i = inverted_index.Index()
        i.add_token(1, "test")
        assert len(i.index.get("test", set())) > 0

    def test_add_tokens(self):
        i = inverted_index.Index()
        i.add_tokens(1, ["a", 'b'])
        assert len(i.index) == 2

    def test_add_default(self):
        i = inverted_index.Index()
        i.add(1, "this is the day they give babies away")
        assert len(i.index) == 8

    def test_add_with_tokenizer(self):
        i = inverted_index.Index()
        i.add(1,
              "this is the day they give babies away",
              tokenizer=lambda s: [s])
        assert len(i.index) == 1

    def test_query_simple(self):
        i = inverted_index.Index()
        i.add(1, "i love bess")
        i.add(2, "i love liz")
        i.add(3, "i love mark")
        s, err = i.query('love')
        assert err is None
        assert s == set([1, 2, 3])

    def test_query_simple_parens(self):
        i = inverted_index.Index()
        i.add(1, "i love bess")
        i.add(2, "i love liz")
        i.add(3, "i love mark")
        s, err = i.query('(((love)))')
        assert err is None
        assert s == set([1, 2, 3])

    def test_query_simple_err(self):
        i = inverted_index.Index()
        i.add(1, "i love bess")
        i.add(2, "i love liz")
        i.add(3, "i love mark")
        s, err = i.query('(((love')
        assert err is not None
        assert s == set()

    def test_query_simple_OR(self):
        i = inverted_index.Index()
        i.add(1, "i love bess")
        i.add(2, "i love liz")
        i.add(3, "i love mark")
        s, err = i.query('liz OR mark')
        assert err is None
        assert s == set([2, 3])

    def test_query_simple_AND(self):
        i = inverted_index.Index()
        i.add(1, "i love bess")
        i.add(2, "i love liz")
        i.add(3, "i love mark")
        s, err = i.query('liz AND mark')
        assert err is None
        assert s == set()
        s, err = i.query('i AND love')
        assert err is None
        assert s == set([1, 2, 3])

    def test_query_fancy(self):
        i = inverted_index.Index()
        i.add(1, "i love bess")
        i.add(2, "i love liz")
        i.add(3, "i love mark")
        i.add(4, 'you hate hitler')
        s, err = i.query("((love AND i) AND bess) OR ((((hitler))))")
        assert err is None
        assert s == set([1, 4])

    def test_query_and_or_lower(self):
        i = inverted_index.Index()
        i.add(1, "i love a good or")
        i.add(2, "and i love a good and")
        s, err = i.query('or')
        assert err is None
        assert s == set([1])
        s, err = i.query('and')
        assert err is None
        assert s == set([2])
        s, err = i.query('or OR and')
        assert err is None
        assert s == set([1, 2])
        s, err = i.query('or AND and')
        assert err is None
        assert s == set([])

    def test_hashable(self):
        i = inverted_index.Index()
        i.add("document_1", "i love bess")
        i.add("document_2", "i love liz")
        i.add("document_3", "i love mark")
        s, err = i.query('bess')
        assert err is None
        assert s == set(["document_1"])


if __name__ == '__main__':
    unittest.main()
