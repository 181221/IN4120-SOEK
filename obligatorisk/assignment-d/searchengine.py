#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import Counter
from utilities import Sieve
from ranking import Ranker
from corpus import Corpus
from invertedindex import InvertedIndex, Posting
from typing import Callable, Any, Iterator


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

        if the query contains m unique query terms, each document in the result set should contain at least n of these m terms.
        """
        terms = list(self._inverted_index.get_terms(query))
        threshhold = options.get("match_threshold")
        debug = options.get("debug", False)
        counter = Counter()
        counter_doc_id = Counter()
        hit = options.get('hit_count')
        sieve = Sieve(hit)
        m = len(set(terms))
        n = max(1, min(m, int(threshhold * m)))
        done_iter = hit == 1 and threshhold == 0.5
        i = 0
        postings_merged = self._inverted_index.get_postings_iterator(terms[0])
        for term in terms:
            if i < len(terms)-1:
                sec = self._inverted_index.get_postings_iterator(terms[i + 1])
                if n == m:  # intersection between the postings
                    merged = self.and_postings(postings_merged, sec)
                else:  # union between postings
                    merged = self.or_postings(postings_merged, sec)
                postings_merged = merged
            if done_iter:
                break
            postings = self._inverted_index.get_postings_iterator(term)
            for post in postings:  # ranking the postings
                ranker.update(term, 1, post)
                score = ranker.evaluate()
                counter[post.document_id] += score  # score of document
                counter_doc_id[post.document_id] += 1   # frequency of document, is used later for at least n out of m query words comparing
                ranker.reset(post.document_id)
            i += 1

        for post in postings_merged:  # postings that will be evaluated
            score = counter[post.document_id]
            freq = counter_doc_id[post.document_id]
            if n == m:  # if all query terms must be in results
                if score >= n:  # terms with score higher than threshold
                    sieve.sift(score, post.document_id)
            elif freq >= n:  # if doc contain at least n out of m query words
                sieve.sift(score, post.document_id)

        for win in sieve.winners(): # append the winners
            doc = self._corpus.get_document(win[1])
            callback({'score': win[0], 'document': doc})

    def and_postings(self, p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        current1 = next(p1, None)
        current2 = next(p2, None)
        while current1 and current2:
            if current1.document_id == current2.document_id:
                yield current1
                current1 = next(p1, None)
                current2 = next(p2, None)
            elif current1.document_id < current2.document_id:
                current1 = next(p1, None)
            else:
                current2 = next(p2, None)

    def or_postings(self, p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        current1 = next(p1, None)
        current2 = next(p2, None)
        while current1 and current2:
            if current1.document_id == current2.document_id:
                yield current1
                current1 = next(p1, None)
                current2 = next(p2, None)
            elif current1.document_id < current2.document_id:
                yield current1
                current1 = next(p1, None)
            else:
                yield current2
                current2 = next(p2, None)

        while current1:
            yield current1
            current1 = next(p1, None)
        while current2:
            yield current2
            current2 = next(p2, None)

