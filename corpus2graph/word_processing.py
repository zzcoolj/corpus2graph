import os
from . import util
from . import multi_processing
from .word_processor import FileParser, WordPreprocessor, Tokenizer


class WordProcessing(object):
    def __init__(self, output_folder, file_parser='txt', fparser=None,
                 xml_node_path=None, word_tokenizer='WordPunct', wtokenizer=None,
                 remove_numbers=True, remove_punctuations=True,
                 stem_word=True, lowercase=True, wpreprocessor=None):
        self.output_folder = output_folder
        # TODO create relevant folder inside output_folder
        self.file_parser = FileParser(file_parser=file_parser, xml_node_path=xml_node_path, fparser=fparser)
        # TODO NOW Ruiqing user defined file_parser yield type check
        self.file_extension = file_parser
        self.word_preprocessor = WordPreprocessor(remove_numbers=remove_numbers,
                                                  remove_punctuations=remove_punctuations,
                                                  stem_word=stem_word, lowercase=lowercase,
                                                  wpreprocessor=wpreprocessor)
        self.tokenizer = Tokenizer(word_tokenizer=word_tokenizer, wtokenizer=wtokenizer)

    def fromfile(self, file_path):
        print('Processing file %s (%s)...' % (file_path, multi_processing.get_pid()))

        word2id = dict()  # key: word <-> value: index
        id2word = dict()
        encoded_text = []
        for sent in self.file_parser(file_path):
            encoded_sent = []
            for word in self.tokenizer.apply(sent):
                word = self.word_preprocessor.apply(word)
                if not word:
                    continue
                if word not in word2id:
                    id = len(word2id)
                    word2id[word] = id
                    id2word[id] = word
                encoded_sent.append(word2id[word])
            encoded_text.append(encoded_sent)

        file_basename = multi_processing.get_file_name(file_path)
        # names like "AA", "AB", ...
        parent_folder_name = multi_processing.get_file_folder(file_path).split('/')[-1]
        # Write the encoded_text
        if not self.output_folder.endswith('/'):
            self.output_folder += '/'
        util.write_to_pickle(encoded_text,
                             self.output_folder + "encoded_text_" + parent_folder_name + "_" + file_basename + ".pickle")
        # Write the dictionary
        util.write_dict(self.output_folder + "dict_" + parent_folder_name + "_" + file_basename + ".dicloc", word2id)

    def merge_local_dict(self):
        def read_first_column_file_to_build_set(file):
            d = set()
            with open(file, encoding='utf-8') as f:
                for line in f:
                    (key, val) = line.rstrip('\n').split("\t")
                    d.add(key)
            return d

        # Take all files in the folder starting with "dict_"
        files = [os.path.join(self.output_folder, name) for name in os.listdir(self.output_folder)
                 if (os.path.isfile(os.path.join(self.output_folder, name))
                     and name.startswith("dict_") and (name != 'dict_merged.txt'))]
        all_keys = set()
        for file in files:
            all_keys |= read_first_column_file_to_build_set(file)

        result = dict(zip(all_keys, range(len(all_keys))))
        util.write_dict(self.output_folder + 'dict_merged.txt', result)
        return result

    def apply(self, data_folder, process_num):
        multi_processing.master(files_getter=multi_processing.get_files_endswith_in_all_subfolders,
                                data_folder=data_folder,
                                file_extension=self.file_extension,
                                worker=self.fromfile,
                                process_num=process_num)
        self.merge_local_dict()

    def __call__(self, data_folder, process_num):
        self.apply(data_folder, process_num)
