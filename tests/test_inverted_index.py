# -*- coding: utf-8 -*-

import unittest

from .context import inverted_index


def sett(*args):
    return set(args)


class InvertedIndexTextSuite(unittest.TestCase):
    def test_create_index(self):
        i = inverted_index.Index()

    def test_reduce_by_intersection_empty(self):
        s = inverted_index.reduce_by_intersection([])
        assert s == set()

    def test_reduce_by_intersection_1(self):
        s = inverted_index.reduce_by_intersection([sett(1, 2, 3)])
        assert s == sett(1, 2, 3)

    def test_reduce_by_intersection_2(self):
        s = inverted_index.reduce_by_intersection([sett(1, 2, 3), sett(2, 3)])
        assert s == sett(2, 3)

    def test_reduce_by_intersection_many(self):
        s = inverted_index.reduce_by_intersection(
            [sett(1, 2, 3, 4, 5), sett(3, 4, 5), sett(3, 4), sett(3)])
        assert s == sett(3)

    def test_index_token(self):
        i = inverted_index.Index()
        i.index_token(1, "test")
        assert len(i.inverted_index.get("test", set())) > 0

    def test_index_tokens(self):
        i = inverted_index.Index()
        i.index_tokens(1, ["a", 'b'])
        assert len(i.inverted_index) == 2

    def test_index_default(self):
        i = inverted_index.Index()
        i.index(1, "this is the day they give babies away")
        assert len(i.inverted_index) == 8

    def test_index_with_tokenizer(self):
        i = inverted_index.Index()
        i.index(
            1,
            "this is the day they give babies away",
            tokenizer=lambda s: [s])
        assert len(i.inverted_index) == 1

    def test_query_simple(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        s, err = i.query('love')
        assert err is None
        assert s == set([1, 2, 3])

    def test_query_simple_parens(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        s, err = i.query('(((love)))')
        assert err is None
        assert s == set([1, 2, 3])

    def test_query_simple_err(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        s, err = i.query('(((love')
        assert err is not None
        assert s == set()

    def test_query_simple_OR(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        s, err = i.query('liz OR mark')
        assert err is None
        assert s == set([2, 3])

    def test_query_simple_AND(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        s, err = i.query('liz AND mark')
        assert err is None
        assert s == set()
        s, err = i.query('i AND love')
        assert err is None
        assert s == set([1, 2, 3])

    def test_query_simple_NOT(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        s, err = i.query('NOT bess')
        print(s)
        a, err = i.query("bess")
        v = i.document_ids().difference(a)
        assert err is None
        assert s == set([2, 3])
        s, err = i.query('NOT i')
        assert err is None
        assert s == set()

    def test_query_fancy(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        i.index(4, 'you hate hitler')
        s, err = i.query(
            "((love AND i) AND bess AND NOT mark) OR ((((hitler))))")
        assert err is None
        assert s == set([1, 4])

    def test_query_and_or_lower(self):
        i = inverted_index.Index()
        i.index(1, "i love a good or")
        i.index(2, "and i love a good and")
        s, err = i.query('or')
        assert err is None
        assert s == set([1])
        s, err = i.query('and')
        assert err is None
        assert s == set([2])
        s, err = i.query('or OR and')
        print(err)
        assert err is None
        assert s == set([1, 2])
        s, err = i.query('or AND and')
        assert err is None
        assert s == set([])

    def test_hashable(self):
        i = inverted_index.Index()
        i.index("document_1", "i love bess")
        i.index("document_2", "i love liz")
        i.index("document_3", "i love mark")
        s, err = i.query('bess')
        assert err is None
        assert s == set(["document_1"])

    def test_unindex(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.unindex(1)
        assert len(i.inverted_index) == 0
        assert len(i.token_counts) == 0
        assert len(i.document_counts) == 0

    def test_unindex_2(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        i.index(4, 'you hate hitler')
        i.unindex(1)
        assert len(i.document_ids()) == 3
        s, err = i.query("love")
        assert err is None
        assert s == set([2, 3])

    def test_index_non_existant(self):
        i = inverted_index.Index()
        i.index(1, "i love bess")
        i.index(2, "i love liz")
        i.index(3, "i love mark")
        i.index(4, 'you hate hitler')
        i.unindex(11111111)
        assert len(i.document_ids()) == 4

    def test_index_document_text(self):
        i = inverted_index.Index()
        i.index_document(1, {'identifier': 'document_1',
                             'title': 'I love bess'})
        s, err = i.query("bess")
        assert err is None
        assert s == set([1])

    def test_index_document_field(self):
        i = inverted_index.Index()
        i.index_document(1, {'identifier': 'document_1',
                             'title': 'I love bess'})
        s, err = i.query("identifier:document_1")
        assert err is None
        assert s == set([1])

    def test_unindex_document(self):
        i = inverted_index.Index()
        i.index_document(1, {'identifier': 'document_1',
                             'title': 'I love bess'})
        assert len(i.document_ids()) == 1
        i.unindex_document(1)
        assert len(i.document_ids()) == 0
        assert len(i.inverted_index) == 0

    def test_index_unindex_field_values(self):
        i = inverted_index.Index()
        i.index_document(1, {'identifier': 'document_1',
                             'title': 'I love bess'})
        s, err = i.query("title:bess")
        assert err is None
        assert s == set([1])
        i.unindex_field(1, 'title')
        s, err = i.query("title:bess")
        assert err is None
        assert s == set()
        i.index_field(1, 'title', 'I like ike')
        s, err = i.query("title:ike")
        assert err is None
        assert s == set([1])

    def test_doc_not_found(self):
        i = inverted_index.Index()
        d, err = i.document('notfound')
        assert err is not None


if __name__ == '__main__':
    unittest.main()
