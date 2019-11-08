#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import operator
from collections import Counter
from dictionary import InMemoryDictionary
from normalization import Normalizer
from tokenization import Tokenizer
from corpus import Corpus
from typing import Callable, Any, Dict, Iterable


class NaiveBayesClassifier:
    """
    Defines a multinomial naive Bayes text classifier.
    Constructor. Trains the classifier from the named fields in the documents in
    the given training set.
    """
    def __init__(self, training_set: Dict[str, Corpus], fields: Iterable[str],
                 normalizer: Normalizer, tokenizer: Tokenizer):

        # Used for breaking the text up into discrete classification features.
        self._normalizer = normalizer
        self._tokenizer = tokenizer

        # The vocabulary we've seen during training.
        self._vocabulary = InMemoryDictionary()
        self.training_set = training_set
        self.fields = fields
        self.prior = {}
        self.condprob = {}
        self._train()

    def _train(self):
        self._extractVocabulary()
        N = 0
        for _class in self.training_set:
            N += self.training_set.get(_class).size()
        for _class in self.training_set:
            docs_in_class = self.training_set.get(_class).size()
            self.prior[_class] = docs_in_class / N
            text_of_docs_in_class = self._get_text_in_class(_class)
            norm = self._get_terms(text_of_docs_in_class)
            counter = Counter(norm)
            for term in self._vocabulary:
                top = counter[term[0]] + 1
                bottom = len(norm) + self._vocabulary.size()
                result = top / bottom
                self.condprob[(term[0], _class)] = result

    def _get_text_in_class(self, _class):
        text_in_doc =""
        for doc in self.training_set.get(_class):
            for field in self.fields:
                text_in_doc += " " + doc[field]
        return text_in_doc

    def _extractVocabulary(self):
        content = ""
        for key in self.training_set:
            for doc in self.training_set.get(key):
                for field in self.fields:
                    content += " " + doc[field]
        for term in self._get_terms(content):
            self._vocabulary.add_if_absent(term)

    def _get_terms(self, buffer):
        """
        Processes the given text buffer and returns the sequence of normalized
        terms as they appear. Both the documents in the training set and the buffers
        we classify need to be identically processed.
        """
        return [self._normalizer.normalize(s) for s in self._tokenizer.strings(self._normalizer.canonicalize(buffer))]

    def classify(self, buffer: str, callback: Callable[[dict], Any]) -> None:
        """
        Classifies the given buffer according to the multinomial naive Bayes rule. The computed (score, category) pairs
        are emitted back to the client via the supplied callback sorted according to the scores. The reported scores
        are log-probabilities, to minimize numerical underflow issues. Logarithms are base e.

        The callback function supplied by the client will receive a dictionary having the keys "score" (float) and
        "category" (str).
        """
        terms = self._get_terms(buffer)
        W = []
        score = []
        for term in terms:
            if term in self._vocabulary:
                W.append(term)
        for _class in self.training_set:
            score_class = math.log(self.prior[_class])
            for term in W:
                score_class += math.log(self.condprob[(term, _class)])
            score.append((score_class, _class))
        score.sort(key= lambda t: math.fabs(t[0]))
        for score in score:
            callback({"score": score[0], "category": score[1] })

