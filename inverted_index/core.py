# -*- coding: utf-8 -*-
import collections
import warnings
from functools import reduce


class Index(object):
    def __init__(self):
        self.inverted_index = dict()
        self.reserved = {'AND': 2, 'OR': 2, '(': None, ')': None, 'NOT': 1}
        self.document_counts = collections.Counter()
        self.token_counts = collections.Counter()

    def cardinality(self, operator):
        return self.reserved[operator]

    def documents(self):
        return set(self.document_counts.keys())

    def index_token(self, document_id, token):
        self.document_counts[document_id] += 1
        self.token_counts[token] += 1
        if token not in self.inverted_index:
            self.inverted_index[token] = collections.Counter()
        self.inverted_index[token][document_id] += 1

    def index_tokens(self, document_id, tokens):
        for token in tokens:
            self.index_token(document_id, token)

    def index(self, document_id, sentence, tokenizer=lambda s: s.split()):
        self.index_tokens(document_id, tokenizer(sentence))

    def unindex(self, document_id):
        removes = []
        for token in self.inverted_index:
            if document_id in self.inverted_index[token]:
                # decrease inverted_index count
                token_count = self.inverted_index[token][document_id]
                del self.inverted_index[token][document_id]
                count = self.inverted_index[token][document_id]
                # decrease doc count
                self.document_counts[document_id] -= token_count
                count = self.document_counts[document_id]
                if count == 0:
                    del self.document_counts[document_id]
                self.token_counts[token] -= token_count
                count = self.token_counts[token]

                if count == 0:
                    del self.token_counts[token]
            if len(self.inverted_index[token]) == 0:
                removes.append(token)
        for token in removes:
            del self.inverted_index[token]

    def query_token(self, token):
        return set(
            self.inverted_index.get(token, collections.Counter()).keys())

    def query(self, q):
        try:
            return (self.process_query(
                q.replace('(', ' ( ').replace(')', ' ) ').split()), None)
        except Exception as e:
            return (set(), e)

    def process_query(self, expr):
        def is_term(token):
            return type(token) == str and token not in self.reserved

        def is_or(token):
            return type(token) == str and token == 'OR'

        def is_and(token):
            return type(token) == str and token == 'AND'

        def is_not(token):
            return type(token) == str and token == 'NOT'

        def is_op(token):
            return is_or(token) or is_and(token) or is_not(token)

        def is_lp(token):
            return type(token) == str and token == '('

        def is_rp(token):
            return type(token) == str and token == ')'

        def apply_operator(op, args):
            # print(operator, args)
            if is_or(op):
                v = reduce(lambda s1, s2: s1.union(s2), args, set())
                # print("returning value", v)
                return v
            elif is_and(op):
                v = reduce_by_intersection(args)
                # print("Returning value", v)
                return v
            elif is_not(op):
                v = self.documents().difference(args[0])
                return v
            else:
                warnings.warn("Unknown operator: {0}".format(op))
                return set()

        value_stack = list()
        operator_stack = list()

        def reduce_operators():
            # print("reducing inside")
            op = operator_stack.pop()
            args = [value_stack.pop() for i in range(self.cardinality(op))]
            v = apply_operator(op, args)
            # print("op", op, "s1", s1, "s2", s2, "value", v)
            value_stack.append(v)

        # print("processing tokens")
        for token in expr:
            # print("current token is", token)
            if is_term(token):
                # print("Found a term", token)
                value_stack.append(self.query_token(token))
            elif is_lp(token):
                # print("found a lp", token)
                operator_stack.append(token)
            elif is_rp(token):
                # print("found a rp", token)
                while len(operator_stack) > 0 and not is_lp(operator_stack[
                        -1]):
                    reduce_operators()
                operator_stack.pop()  # pop off '('
            elif is_op(token):
                # print("found AND or OR, indexing to operator_stack")
                operator_stack.append(token)
        # print("operating on operator stack")
        while len(operator_stack) > 0:
            reduce_operators()
        # print("reducing values")
        return reduce_by_intersection(value_stack)


def reduce_by_intersection(sets):
    if len(sets) == 0:
        return set()
    else:
        head = sets[0]
        tail = sets[1:]
        return reduce(lambda s1, s2: s1.intersection(s2), tail, head)
