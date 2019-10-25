#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from corpus import Corpus
from invertedindex import Posting, InvertedIndex
from math import log


class Ranker(ABC):
    """
    Abstract base class for rankers used together with document-at-a-time traversal.
    """

    @abstractmethod
    def reset(self, document_id: int) -> None:
        """
        Resets the ranker, i.e., prepares it for evaluating another document.
        """
        pass

    @abstractmethod
    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        """
        Tells the ranker to update its internals based on information from one
        query term and the associated posting. This method might be invoked multiple
        times if the query contains multiple unique terms. Since a query term might
        occur multiple times in a query, the query term's multiplicity or occurrence
        count in the query is also provided.
        """
        pass

    @abstractmethod
    def evaluate(self) -> float:
        """
        Returns the current document's relevancy score. I.e., evaluates how relevant
        the current document is, given all the previous update invocations.
        """
        pass


class BrainDeadRanker(Ranker):
    """
    A dead simple ranker.
    """

    def __init__(self):
        self._score = 0.0

    def reset(self, document_id: int) -> None:
        self._score = 0.0

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        self._score += multiplicity * posting.term_frequency

    def evaluate(self) -> float:
        return self._score


class BetterRanker(Ranker):
    """
    A ranker that does traditional TF-IDF ranking, possibly combining it with
    a static document score (if present).

    The static document score is assumed accessible in a document field named
    "static_quality_score". If the field is missing or doesn't have a value, a
    default value of 0.0 is assumed for the static document score.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self._score = 0.0
        self._document_id = None
        self._corpus = corpus
        self._inverted_index = inverted_index
        self._dynamic_score_weight = 1.0  # TODO: Make this configurable.
        self._static_score_weight = 1.0  # TODO: Make this configurable. #gd
        self._static_score_field_name = "static_quality_score"  # TODO: Make this configurable.

    def reset(self, document_id: int) -> None:
        self._score = 0.0
        self._document_id = document_id

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        df = self._inverted_index.get_document_frequency(term)
        """
        A word occurring in a large proportion of documents is not a good discriminator, that is why we use 
        inverse document frequency. The idea is to scale down the terms with high collection frequency, thus the idf 
        of a rare term is high, whereas the idf of a frequent term is likely to be low 
        """
        idf_score = self.idf(df)
        """
        Term Frequency - how many times does the term occour in a document.
        If a word is occourring multiple teams in a documents it is more relevant. 
        Term frequency x Inverse document frequency tend to filter out common terms
        """
        tf_idf_score = multiplicity * posting.term_frequency * idf_score
        self._score += tf_idf_score

    def idf(self, df):
        return log((self._corpus.size()/df), 10)

    def evaluate(self) -> float:
        document = self._corpus[self._document_id]
        static_quality_score = float(document[self._static_score_field_name] or 0.0)
        return static_quality_score + self._score

