#!/usr/bin/python
# -*- coding: utf-8 -*-

# import itertools
from collections import Counter
from utilities import Sieve, apply
import re
from corpus import Corpus
from normalization import Normalizer
from tokenization import Tokenizer
from typing import Callable, Any, Iterable



class SuffixArray:
    """
    A simple suffix array implementation. Allows us to conduct efficient substring searches.
    The prefix of a suffix is an infix!

    In a serious application we'd make use of least common prefixes (LCPs), pay more attention
    to memory usage, and add more lookup/evaluation features.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        self._corpus = corpus
        self._normalizer = normalizer
        self._tokenizer = tokenizer
        self._suffixes = []
        self._haystack = []
        self.matches = []
        self._counter = Counter()
        self._build_suffix_array(fields)

    def _build_suffix_array(self, fields: Iterable[str]) -> None:
        """
        Builds a simple suffix array from the set of named fields in the document collection.
        The suffix array allows us to search across all named fields in one go.
        """
        for doc in self._corpus:
            text_in_fields = ""
            for field in fields:
                text_in_fields += self._normalize(doc[field])
            self._haystack.append(text_in_fields)
            for i in self._tokenizer.ranges(text_in_fields):
                self._suffixes.append((doc.document_id, i[0]))
        self._suffixes.sort(key=self.sorted_by)
        suffix = self.getSuffixes()
        suffix

    def getSuffixes(self):
        suffixes = []
        for b in self._suffixes:
            doc_string = self._haystack[b[0]]
            suffix = doc_string[b[1]:]
            suffixes.append(suffix)
        return suffixes

    def sorted_by(self, suff):
        return self.getSuffix(suff)

    def getSuffix(self, suff):
        return self._haystack[suff[0]][suff[1]:]

    def _normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to succeed.
        """

        # Tokenize and join to be robust to nuances in whitespace and punctuation.
        return self._normalizer.normalize(" ".join(self._tokenizer.strings(self._normalizer.canonicalize(buffer))))

    def evaluate(self, query: str, options: dict, callback: Callable[[dict], Any]) -> None:
        """
        Evaluates the given query, doing a "phrase prefix search".  E.g., for a supplied query phrase like
        "to the be", we return documents that contain phrases like "to the bearnaise", "to the best",
        "to the behemoth", and so on. I.e., we require that the query phrase starts on a token boundary in the
        document, but it doesn't necessarily have to end on one.

        The matching documents are ranked according to how many times the query substring occurs in the document,
        and only the "best" matches are returned to the client via the supplied callback function. Ties are
        resolved arbitrarily.

        The client can supply a dictionary of options that controls this query evaluation process: The maximum
        number of documents to return to the client is controlled via the "hit_count" (int) option.

        The callback function supplied by the client will receive a dictionary having the keys "score" (int) and
        "document" (Document).
        """

        hit = options.get('hit_count')
        sieve = Sieve(hit)
        matches = []
        counter = []
        skip_indexes = []
        self.binarySearch(self._suffixes, 0, len(self._suffixes), query)
       # for i in range(100):
        #    string, doc_id = self.binarySearch(self._suffixes, 0, len(self._suffixes), query)



        test = "hei"

    def binarySearch(self, arr, start, length, search_term):
        if length >= start:
            mid = int(start + (length - start) / 2)
            suff = arr[mid]
            string = self.getSuffix(suff)
            match = re.match("^" + search_term + "\w*", string)
            #match = re.search(search_term + "\w*", string)
            if match:
                self.matches.append(string)
                self.search(search_term, mid, start, length)
                self._counter[match[0],suff[0]] += 1
                return (match[0],suff[0])
            elif string > search_term:
                return self.binarySearch(arr, start, mid - 1, search_term)
            else:
                return self.binarySearch(arr, mid + 1, length, search_term)
        else:
            # Element is not present in the array
            return -1

    def search(self,pattern,mid,start, length):
        r = mid + 1
        l = mid - 1
        suffix = self.getSuffixes()
        suffix
        while r < length:
            suff = self._suffixes[r]
            string = self.getSuffix(suff)
            match = re.match("^" + pattern + "\w*", string)
            if match:
                self.matches.append(string)
                self._counter[match[0], suff[0]] += 1
                r += 1
            else:
                break
        while l > start:
            suff = self._suffixes[l]
            string = self.getSuffix(suff)
            match = re.match("^" + pattern + "\w*", string)
            if match:
                self.matches.append(string)
                self._counter[match[0], suff[0]] += 1
                l -= 1
            else:
                break

