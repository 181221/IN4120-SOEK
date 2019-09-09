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

post = Posting(1,1)
c = collections.Counter(["hei","hei", "test"])
c.get()
print(c)
print("hei sann hadet".split(' '))