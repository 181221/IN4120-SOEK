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
        token_seq = []
        for doc in self._corpus:
            for field in fields:
                terms = self.get_terms(doc[field])
                for term in terms:
                    token_seq.append((doc.document_id, term))

        token_seq.sort(key=lambda el: el[1])
        freq_seq = collections.Counter(token_seq)
        tokens_to_pop = []
        for i in range(len(token_seq)):
            term = token_seq[i][1]
            self._dictionary.add_if_absent(term)
            doc_id = token_seq[i][0]
            for j in range(i + 1, len(token_seq)-1):
                if term == token_seq[j][1] and doc_id == token_seq[j][0]:
                    tokens_to_pop.append(i)
                    term = token_seq[j][1]
                    doc_id = token_seq[j][0]
                else:
                    break
        for index in tokens_to_pop:
            token_seq.pop(index)

        for i in range(len(token_seq)):
            term = token_seq[i][1]
            doc_id = token_seq[i][0]
            term_id = self._dictionary.get_term_id(term)
            lengden = len(self._posting_lists)
            if term_id < lengden:
                posting_list = self._posting_lists[term_id]
                post = Posting(doc_id, freq_seq.get(token_seq[i]))
                posting_list.append(post)
            else:
                posting_list = []
                post = Posting(doc_id, freq_seq.get(token_seq[i]))
                posting_list.append(post)
                self._posting_lists.append(posting_list)



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
