import os
from multiprocessing import Pool
from . import util
from . import multi_processing
from .word_processor import FileParser, WordPreprocessor, Tokenizer
import spacy


class WordProcessing(object):
    def __init__(self, output_folder, language='en', file_parser='txt', fparser=None,
                 xml_node_path=None, word_tokenizer='WordPunct', wtokenizer=None,
                 remove_stop_words=True, remove_numbers=True, remove_punctuations=True, replace_digits_to_zeros=True,
                 stem_word=True, lowercase=True, wpreprocessor=None):
        self.output_folder = output_folder
        self.file_parser = FileParser(file_parser=file_parser, xml_node_path=xml_node_path, fparser=fparser)
        # TODO NOW Ruiqing user defined file_parser yield type check
        self.file_extension = file_parser
        self.word_preprocessor = WordPreprocessor(remove_numbers=remove_numbers,
                                                  remove_stop_words=remove_stop_words,
                                                  replace_digits_to_zeros=replace_digits_to_zeros,
                                                  remove_punctuations=remove_punctuations,
                                                  stem_word=stem_word, lowercase=lowercase,
                                                  wpreprocessor=wpreprocessor)
        self.language = language
        self.word_tokenizer = word_tokenizer
        self.remove_stop_words = remove_stop_words
        self.tokenizer = Tokenizer(word_tokenizer=word_tokenizer, wtokenizer=wtokenizer)

    def fromfile(self, file_path):
        """
        master sends jobs to processors, each processor takes one file at one time and execute this function.
        """
        print('Processing file %s (%s)...' % (file_path, multi_processing.get_pid()))

        """
        Give spacy tokenizer special treatment here (not in Tokenizer in word_processor.py).
        Because spacy has error :
            AttributeError: Can't pickle local object 'FeatureExtracter.<locals>.feature_extracter_fwd'
        So it can't be transferred as an object by using 'self', self.tokenizer is useless in this case.
        Each thread loads spacy once when a job has been sent to this thread.        
        """
        spacy_loader = None
        if self.word_tokenizer == 'spacy' or self.remove_stop_words:
            if self.language == 'en':
                # print('en spacy tokenizer loaded')
                spacy_loader = spacy.load('en')
            elif self.language == 'fr':
                # print('fr spacy tokenizer loaded')
                spacy_loader = spacy.load('fr')

        word2id = dict()  # key: word <-> value: index
        id2word = dict()
        encoded_text = []

        for sent in self.file_parser(file_path):
            encoded_sent = []
            for word in self.tokenizer.apply(sent, spacy_loader=spacy_loader):  # sent is already striped in file_parser
                word = self.word_preprocessor.apply(word, spacy_loader=spacy_loader)
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

    @staticmethod
    def read_first_column_file_to_build_set(file):
        d = set()
        with open(file, encoding='utf-8') as f:
            for line in f:
                (key, val) = line.rstrip('\n').split("\t")
                d.add(key)
        return d

    def local_dicts_merger_worker(self, file_paths):
        all_keys = set()
        for file_path in file_paths:
            all_keys |= self.read_first_column_file_to_build_set(file_path)
        return all_keys

    def merge_local_dict(self, process_num):
        # Take all files in the folder starting with "dict_" but not "dict_merged.txt"
        files = [os.path.join(self.output_folder, name) for name in os.listdir(self.output_folder)
                 if (os.path.isfile(os.path.join(self.output_folder, name))
                     and name.startswith("dict_") and (name != 'dict_merged.txt'))]
        if len(files) == 1:
            all_keys = self.read_first_column_file_to_build_set(files[0])
        else:
            # Fix process_num
            if len(files)//2 < process_num:
                process_num = len(files)//2
                print('process_num set to', process_num, 'for local dict merging')
            # multiprocessing
            files_list = multi_processing.chunkify(lst=files, n=process_num)
            p = Pool(process_num)
            sub_merged_dicts = p.starmap(self.local_dicts_merger_worker, zip(files_list))
            p.close()
            p.join()
            print('All sub-processes done.')

            all_keys = set()
            for sub_merged_dict in sub_merged_dicts:
                all_keys |= sub_merged_dict

        result = dict(zip(all_keys, range(len(all_keys))))
        util.write_dict(self.output_folder + 'dict_merged.txt', result)
        return result

    def apply(self, data_folder, process_num):
        # Handle the single training file case.
        target_file = multi_processing.get_files_endswith_in_all_subfolders(data_folder=data_folder,
                                                                            file_extension=self.file_extension)
        if len(target_file) == 1:
            print("Single text file founded! Do you want to split it into several smaller text files? y/n\n"
                  "('y' is recommended for the large text file to benefit from multi-processing.)")
            yes = {'yes', 'y', 'ye'}
            no = {'no', 'n'}
            while True:
                choice = input().lower()
                if choice in yes:
                    # Splitting single large text file into smaller ones
                    lines_per_file = 500  # TODO determine a reasonable number
                    if data_folder.endswith('/'):
                        new_folder = data_folder[:-1] + '_small_files/'
                    else:
                        new_folder = data_folder + '_small_files/'
                    if not os.path.exists(new_folder):
                        os.makedirs(new_folder + 'one/')
                    else:
                        print('[ERROR] ' + new_folder + ' already exists.')
                        exit()
                    smallfile = None
                    with open(target_file[0], encoding='utf-8') as bigfile:
                        for lineno, line in enumerate(bigfile):
                            if lineno % lines_per_file == 0:
                                if smallfile:
                                    smallfile.close()
                                small_filename = 'small_file_{}.txt'.format(lineno + lines_per_file)
                                smallfile = open(new_folder + 'one/' + small_filename, "w", encoding='utf-8')
                            smallfile.write(line)
                        if smallfile:
                            smallfile.close()
                    print(new_folder +
                          ' has been created with small split files. Please rerun this program with new <data_dir>.')
                    exit()
                elif choice in no:
                    print("Continue running program with single text file. Only one processor is used.")
                    break
                else:
                    print("Please respond with 'y'/'yes' or 'n'/'no'")

        # Now, multi-process all text files
        multi_processing.master(files_getter=multi_processing.get_files_endswith_in_all_subfolders,
                                data_folder=data_folder,
                                file_extension=self.file_extension,
                                worker=self.fromfile,
                                process_num=process_num)
        return self.merge_local_dict(process_num=process_num)

    def __call__(self, data_folder, process_num):
        self.apply(data_folder, process_num)
