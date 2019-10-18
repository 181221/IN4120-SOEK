#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import Counter
from utilities import Sieve
from ranking import Ranker
from corpus import Corpus
from invertedindex import InvertedIndex, Posting
from typing import Callable, Any, Iterator
from traversal import PostingsMerger


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
        counter_terms = Counter(terms)
        hit = options.get('hit_count')
        sieve = Sieve(hit)
        m = len(terms)
        n = max(1, min(m, int(threshhold * m)))

        class Aktiv(object):
            def __init__(self, invertedindex, term, multiplicity):
                self.term = term
                self.iterator = invertedindex.get_postings_iterator(term)
                self.posting = next(self.iterator, None)
                self.multiplicity = multiplicity
                self.hasBeenRanked = False

            @property
            def document_id(self):
                return self.posting.document_id

            def neste_posting(self):
                self.posting = next(self.iterator, None)

        aktive = []  # liste av posting liste-iteratorer

        for term in terms:
            aktiv = Aktiv(self._inverted_index, term, counter_terms[term])
            if aktiv.posting is not None:
                aktive.append(aktiv)
        forrige_minste = None
        while len(aktive) > 0:
            (minste, index) = min((v.document_id, i) for i, v in enumerate(aktive))
            current = aktive[index]
            if minste != forrige_minste:
                aktive_docids = [a for a in aktive if a.document_id == minste]
                ranker.reset(current.document_id)
                evaluated_terms = []
                # må gå gjennom aktive_docids for å sjekke term og frequency
                for a in aktive_docids:
                    if a.term not in evaluated_terms:
                        ranker.update(a.term, a.multiplicity, a.posting)
                        evaluated_terms.append(a.term)
                score = ranker.evaluate()
                if threshhold == 1:
                    if not len(aktive_docids) < n and score >= n:
                        sieve.sift(score, minste)
                else:
                    if score >= n and len(aktive_docids) >= n:
                        sieve.sift(score, minste)
            forrige_minste = minste
            current.neste_posting()
            post = current.posting
            if post is None:
                aktive.pop(index)

        for win in sieve.winners(): # append the winners
            doc = self._corpus.get_document(win[1])
            callback({'score': win[0], 'document': doc})