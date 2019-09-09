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


token_seg = ["hei", 'hadet','123', '1234']
list1 = []
list1[0]
list1.append([])
list1.append([])
list1.append([])
print(list1)
i = 0
for token in token_seg[i:len(token_seg)-1]:
    j = i + 1

for i in range(token_seg):
    print(token_seg[i])