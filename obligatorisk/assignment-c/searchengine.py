#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import Counter
from utilities import Sieve
from ranking import Ranker
from corpus import Corpus
from invertedindex import InvertedIndex
from typing import Callable, Any


class SimpleSearchEngine:
    """
    A simple implementation of a search engine based on an inverted index, suitable for small corpora.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self._corpus = corpus
        self._inverted_index = inverted_index

    def evaluate(self, query: str, options: dict, ranker: Ranker, callback: Callable[[dict], Any]) -> None:
        """
        Evaluates the given query, doing N-out-of-M ranked retrieval. I.e., for a supplied query having M terms,
        a document is considered to be a match if it contains at least N <= M of those terms.

        The matching documents are ranked by the supplied ranker, and only the "best" matches are returned to the
        client via the supplied callback function.

        The client can supply a dictionary of options that controls this query evaluation process: The value of
        N is inferred from the query via the "match_threshold" (float) option, and the maximum number of documents
        to return to the client is controlled via the "hit_count" (int) option.

        The callback function supplied by the client will receive a dictionary having the keys "score" (float) and
        "document" (Document).
        """

        terms = list(self._inverted_index.get_terms(query))

        threshhold = options.get("match_threshold")

        # Print verbose debug information?
        debug = options.get("debug", False)
        counter = Counter()
        hit = options.get('hit_count')
        sieve = Sieve(hit)

        m = len(terms)
        n = max(1, min(m, int(threshhold * m)))

        for term in terms:
            postings = list(self._inverted_index.get_postings_iterator(term))
            for post in postings:
                counter[post.document_id] += 1
                sieve.sift(counter[post.document_id], post.document_id)

        for win in sieve.winners():
            doc = self._corpus.get_document(win[1])
            if win[0] >= n:
                callback({'score': win[0], 'document': doc})
