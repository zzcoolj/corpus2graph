import warnings


class WordPairsExtractor(object):
    def __init__(self, max_window_size, type='position'):
        self.max_window_size = max_window_size
        self.type = type

    def position_based(self, encoded_text):
        edges = {}

        # Construct edges
        for i in range(2, self.max_window_size + 1):
            edges[i] = []
        for encoded_sent in encoded_text:
            sentence_len = len(encoded_sent)
            for start_index in range(sentence_len - 1):
                if start_index + self.max_window_size < sentence_len:
                    max_range = self.max_window_size + start_index
                else:
                    max_range = sentence_len

                for end_index in range(1 + start_index, max_range):
                    current_window_size = end_index - start_index + 1
                    # encoded_edge = [encoded_sent[start_index], encoded_sent[end_index]]
                    encoded_edge = (encoded_sent[start_index], encoded_sent[end_index])
                    edges[current_window_size].append(encoded_edge)
        return edges

    def apply(self, encoded_text, distance):
        if self.type == 'position':
            return self.position_based(encoded_text)
        else:
            return {}

    def __call__(self, encoded_text, distance):
        return self.apply(encoded_text, distance)