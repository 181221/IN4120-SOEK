#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
from abc import ABC, abstractmethod
from dictionary import InMemoryDictionary
from normalization import Normalizer
from tokenization import Tokenizer
from corpus import Corpus
from collections import Counter
from typing import Iterable, Iterator
import collections

class Posting:
    """
    A very simple posting entry in a non-positional inverted index.
    """

    def __init__(self, document_id: int, term_frequency: int):
        self.document_id = document_id
        self.term_frequency = term_frequency

    def __repr__(self):
        return str({"document_id": self.document_id, "term_frequency": self.term_frequency})


class InvertedIndex(ABC):
    """
    Abstract base class for a simple inverted index.
    """

    def __getitem__(self, term: str) -> Iterator[Posting]:
        return self.get_postings_iterator(term)

    def __contains__(self, term: str) -> bool:
        return self.get_document_frequency(term) > 0

    @abstractmethod
    def get_terms(self, buffer: str) -> Iterator[str]:
        """
        Processes the given text buffer and returns an iterator that yields normalized
        terms as they are indexed. Both query strings and documents need to be
        identically processed.
        """
        pass

    @abstractmethod
    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        """
        Returns an iterator that can be used to iterate over the term's associated
        posting list. For out-of-vocabulary terms we associate empty posting lists.
        """
        pass

    @abstractmethod
    def get_document_frequency(self, term: str) -> int:
        """
        Returns the number of documents in the indexed corpus that contains the given term.
        """
        pass


class InMemoryInvertedIndex(InvertedIndex):
    """
    A simple in-memory implementation of an inverted index, suitable for small corpora.

    In a serious application we'd have configuration to allow for field-specific NLP,
    scale beyond current memory constraints, have a positional index, and so on.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        self._corpus = corpus
        self._normalizer = normalizer
        self._tokenizer = tokenizer
        self._posting_lists = []
        self._posting_lists_size = 0
        self._dictionary = InMemoryDictionary()
        self._build_index(fields)

    def __repr__(self):
        return str({term: self._posting_lists[term_id] for (term, term_id) in self._dictionary})

    def _corpus_freq(self, term_docid_list):
        corpus_doc_freq = {}
        lengden = len(term_docid_list)

        for i in range(lengden):
            term = term_docid_list[i][0]
            if term not in corpus_doc_freq:
                corpus_doc_freq[term] = 1
            if i < lengden:
                j = i + 1
                while j < lengden and term == term_docid_list[j][0]:
                    j = j + 1
                    corpus_doc_freq[term] = corpus_doc_freq[term] + 1

        return corpus_doc_freq

    def _build_index(self, fields: Iterable[str]) -> None:
        print(fields)
        list_col = []
        for doc in self._corpus:
            for field in fields:
                terms = self.get_terms(doc[field])
                for term in terms:
                    self._dictionary.add_if_absent(term)
                list_col.append(collections.Counter(terms))









    """
        def _build_index(self, fields: Iterable[str]) -> None:
        term_docid_list = []
        posting_list = []
        for doc in self._corpus:
            arr = []
            for field in fields:
                terms = self.get_terms(doc[field])
                arr.append(doc[field])
                col = collections.Counter(terms)
                for value in col.values():
                    posting_list.append(Posting(doc.document_id, value))

            terms = []
            for a in arr:
                col = collections.Counter(self.get_terms(a))
                terms.append(self.get_terms(a))
            for term in terms:
                col = collections.Counter(term.split(' '))
                Posting(doc.document_id, col.get(term))

            word_dict = {}
            for term in terms:
                word_dict[term] = doc.document_id
            for key in word_dict:
                term_docid_list.append((key, word_dict[key]))

        term_docid_list.sort(key=lambda el: el[0])
        for term in term_docid_list:
            self._dictionary.add_if_absent(term[0])

        for term in term_docid_list:
            term_id = self._dictionary.get_term_id(term[0])
            if term_id < len(self._posting_lists):
                self._posting_lists[term_id].append(term[1])
            else:
                self._posting_lists.append([term[1]])
    """

    def get_terms(self, buffer: str) -> Iterator[str]:
        return (self._normalizer.normalize(t) for t in self._tokenizer.strings(self._normalizer.canonicalize(buffer)))

    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        # In a serious application a postings list would be stored as a contiguous buffer
        # storing compressed integers, and the iterator would facilitate loading this buffer
        # from somewhere and decompressing the integers.
        term_id = self._dictionary.get_term_id(term)
        return iter([]) if term_id is None else iter(self._posting_lists[term_id])

    def get_document_frequency(self, term: str) -> int:
        # In a serious application we'd store this number explicitly, e.g., as part of the dictionary.
        # That way, we can look up the document frequency without having to access the posting lists
        # themselves. Imagine if the posting lists don't even reside in memory!
        term_id = self._dictionary.get_term_id(term)
        return 0 if term_id is None else len(self._posting_lists[term_id])
