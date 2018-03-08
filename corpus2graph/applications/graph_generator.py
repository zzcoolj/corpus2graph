import os
import collections
from .. import util
from .. import multi_processing
from ..word_processor import FileParser, WordPreprocessor, Tokenizer


class GraphGenerator(object):
    def __init__(self, window_size, file_parser='txt', fparser=None,
                 xml_node_path=None, word_tokenizer='WordPunct',  wtokenizer=None,
                 remove_numbers=True, remove_punctuations=True,
                 stem_word=True, lowercase=True, wpreprocessor=None):
        self.window_size = window_size
        self.file_parser = FileParser(file_parser=file_parser, xml_node_path=xml_node_path, fparser=fparser)
        # TODO NOW Ruiqing user defined file_parser yield type check
        self.file_extension = file_parser
        self.word_preprocessor = WordPreprocessor(remove_numbers=remove_numbers,
                                                  remove_punctuations=remove_punctuations,
                                                  stem_word=stem_word, lowercase=lowercase,
                                                  wpreprocessor=wpreprocessor)
        self.tokenizer = Tokenizer(word_tokenizer=word_tokenizer, wtokenizer=wtokenizer)

    def fromsent(self, sent):
        sentence_len = len(sent)
        pairs = []
        for start_index in range(sentence_len - 1):
            if start_index + self.window_size < sentence_len:
                max_range = self.window_size + start_index
            else:
                max_range = sentence_len
            pairs.extend([str(sent[start_index])+' '+str(sent[end_index])
                          for end_index in range(1 + start_index, max_range)])
        return pairs


    def fromfile(self, file_path):
        print('Processing file %s...' % (file_path))
        pairs = []
        words = []
        for sent in self.file_parser(file_path):
            processed_sent = []
            for word in self.tokenizer.apply(sent):
                word = self.word_preprocessor.apply(word)
                if not word:
                    continue
                processed_sent.append(word)
            words.extend(processed_sent)
            pairs.extend(self.fromsent(processed_sent))
        d = collections.Counter(pairs)
        return [(k.split()[0], k.split()[1], d[k]) for k in d], set(words)

    def apply(self, data_folder):
        files = multi_processing.get_files_endswith_in_all_subfolders(
                                data_folder=data_folder,
                                file_extension=self.file_extension)
        for f in files:
            yield self.fromfile(f)

    def __call__(self, data_folder):
        for l in self.apply(data_folder):
            yield l