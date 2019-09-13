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

        """
        A generator that yields a simple OR of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        answers = []
        el1 = next(p1, None)
        el2 = next(p2, None)
        # merge small list first than we do not have to check for each member of the large list.
        # We can just add them to the list since they all are larger.
        while el1 is not None and el2 is not None:
            while el1.document_id < el2.document_id:
                answers.append(el1)
                el1 = next(p1, None)
            answers.append(el2)
            el2 = next(p2, None)
        while el1 is not None:
            answers.append(el1)
            el1 = next(p1, None)
        while el2 is not None:
            answers.append(el2)
            el2 = next(p2, None)

        return iter(answers)

