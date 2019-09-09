#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Iterator
from invertedindex import Posting


class PostingsMerger:
    """
    Utility class for merging posting lists.
    """

    @staticmethod
    def intersection(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple AND of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        answers = []
        el1 = next(p1, None)
        el2 = next(p2, None)
        while el1 is not None and el2 is not None:
            if el1.document_id == el2.document_id:
                answers.append(el1)
                el1 = next(p1, None)
                el2 = next(p2, None)
            elif el1.document_id < el2.document_id:
                el1 = next(p1, None)
            else:
                el2 = next(p2, None)
        return iter(answers)

    @staticmethod
    def union(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        answers = []
        size1 = p1.__sizeof__()
        size2 = p2.__sizeof__()
        el1 = next(p1, None)
        el2 = next(p2, None)
        listen = list(p1)
        print("\n" * 3)
        for p in listen:
            print(p)
        print("\n"*3)
        while el1 is not None and el2 is not None:
            print(el1)
            print(el2)
            if el1 == el2:
                print("is equal")

            el1 = next(p1, None)
            el2 = next(p2, None)
        print("\n" * 3)
        """
        A generator that yields a simple OR of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """

        # Replace this with your own implementation.
        raise NotImplementedError
