# -*- coding: utf-8 -*-
import warnings
from functools import reduce


class Index(object):
    def __init__(self):
        self.index = dict()
        self.reserved = set(['AND', 'OR', '(', ')'])

    def add_token(self, document_id, token):
        if token not in self.index:
            self.index[token] = set()
        self.index[token].add(document_id)

    def add(self, document_id, sentence, tokenizer=lambda s: s.split()):
        # print(sentence)
        self.add_tokens(document_id, tokenizer(sentence))

    def add_tokens(self, document_id, tokens):
        for token in tokens:
            self.add_token(document_id, token)

    def query_token(self, token):
        return self.index.get(token, set())

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

        def is_lp(token):
            return type(token) == str and token == '('

        def is_rp(token):
            return type(token) == str and token == ')'

        def apply_operator(operator, s1, s2):
            # print(operator, s1, s2)
            if is_or(op):
                v = s1.union(s2)
                # print("returning value", v)
                return v
            elif is_and(op):
                v = s1.intersection(s2)
                # print("Returning value", v)
                return v
            else:
                warnings.warn("Unknown operator: {0}".format(op))
                return set()

        value_stack = list()
        operator_stack = list()
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
                    # print("reducing inside")
                    op = operator_stack.pop()
                    s1 = value_stack.pop()
                    s2 = value_stack.pop()
                    v = apply_operator(op, s1, s2)
                    # print("op", op, "s1", s1, "s2", s2, "value", v)
                    value_stack.append(v)
                operator_stack.pop()  # pop off '('
            elif is_or(token) or is_and(token):
                # print("found AND or OR, adding to operator_stack")
                operator_stack.append(token)
        # print("operating on operator stack")
        while len(operator_stack) > 0:
            op = operator_stack.pop()
            s1 = value_stack.pop()
            s2 = value_stack.pop()
            v = apply_operator(op, s1, s2)
            value_stack.append(v)
        # print("reducing values")
        try:  # treat the value stack as ands
            base = value_stack.pop()
            # print("base is", base, "rest is", value_stack)
            return reduce(lambda s1, s2: s1.intersection(s2), value_stack,
                          base)
        except IndexError:
            # print("returning empty set from failure at end")
            return set()
