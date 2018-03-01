__author__ = 'Ruiqing YIN'

import os
from .. import util
from .. import multi_processing
from ..word_processor import FileParser, WordPreprocessor, Tokenizer


class WordsGenerator(object):
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
        for start_index in range(sentence_len - 1):
            if start_index + self.window_size < sentence_len:
                max_range = self.window_size + start_index
            else:
                max_range = sentence_len
            for end_index in range(1 + start_index, max_range):
                yield sent[start_index], sent[end_index]

    def fromfile(self, file_path):
        print('Processing file %s...' % (file_path))

        for sent in self.file_parser(file_path):
            processed_sent = []
            for word in self.tokenizer.apply(sent):
                word = self.word_preprocessor.apply(word)
                if not word:
                    continue
                processed_sent.append(word)
            for pair in self.fromsent(processed_sent):
                yield pair

    def apply(self, data_folder):
        files = multi_processing.get_files_endswith_in_all_subfolders(
                                data_folder=data_folder,
                                file_extension=self.file_extension)
        for f in files:
            for pair in self.fromfile(f):
                yield pair

    def __call__(self, data_folder):
        for pair in self.apply(data_folder):
            yield pair
