from collections import Counter
from . import util
from . import multi_processing
from .sentence_processor import WordPairsExtractor


class SentenceProcessing(object):
    def __init__(self, dicts_folder, output_folder, max_window_size, local_dict_extension):
        self.dicts_folder = dicts_folder
        self.output_folder = output_folder
        self.max_window_size = max_window_size
        self.word_pair_extractor = WordPairsExtractor(max_window_size=max_window_size, type='position')
        self.local_dict_extension = local_dict_extension
        self.merged_dict = util.read_two_columns_file_to_build_dictionary_type_specified_bis(
            file=dicts_folder + '/dict_merged.txt', key_type=str,
            value_type=int)

    def word_count(self, encoded_text, file_name, local_dict_file_path):
        result = dict(Counter([item for sublist in encoded_text for item in sublist]))
        folder_name = multi_processing.get_file_folder(local_dict_file_path)
        util.write_dict_to_file(folder_name + "/word_count_" + file_name + ".txt", result, 'str')
        return result

    def get_transfer_dict_for_local_dict(self, local_dict, merged_dict):
        """
        local_dict:
            "hello": 37
        merged_dict:
            "hello": 52
        transfer_dict:
            37: 52
        """
        transfer_dict = {}
        for key, value in local_dict.items():
            transfer_dict[value] = merged_dict[key]
        return transfer_dict

    def write_edges_of_different_window_size(self, encoded_text, file_basename):
        edges = self.word_pair_extractor(encoded_text, file_basename)
        # Write edges to files
        if not self.output_folder.endswith('/'):
            self.output_folder += '/'
        for i in range(2, self.max_window_size + 1):
            util.write_list_to_file(
                self.output_folder + file_basename + "_encoded_edges_distance_{0}.txt".format(i), edges[i])

    def fromfile(self, local_dict_file_path):
        print('Processing file %s (%s)...' % (local_dict_file_path, multi_processing.get_pid()))

        local_dict = util.read_two_columns_file_to_build_dictionary_type_specified_bis(local_dict_file_path, str, int)
        transfer_dict = self.get_transfer_dict_for_local_dict(local_dict, self.merged_dict)
        '''
        Local dict and local encoded text must be in the same folder,
        and their names should be look like below:
            local_dict_file_path:       dict_xin_eng_200410.txt
            local_encoded_text_pickle:  pickle_encoded_text_xin_eng_200410
        '''
        # Get encoded_text_pickle path according to local_dict_file_path
        local_encoded_text_pickle = local_dict_file_path.replace("dict_", "encoded_text_")[
                                    :-len(self.local_dict_extension)]
        local_encoded_text = util.read_pickle(local_encoded_text_pickle + ".pickle")
        # Translate the local encoded text with transfer_dict
        transferred_encoded_text = []
        for encoded_sent in local_encoded_text:
            transfered_encoded_sent = []
            for encoded_word in encoded_sent:
                transfered_encoded_sent.append(transfer_dict[encoded_word])
            transferred_encoded_text.append(transfered_encoded_sent)

        file_name = multi_processing.get_file_name(local_dict_file_path).replace("dict_", "")
        # Word count
        self.word_count(transferred_encoded_text, file_name, local_dict_file_path)
        # Write edges files of different window size based on the transfered encoded text
        self.write_edges_of_different_window_size(transferred_encoded_text, file_name)

    def merge_transferred_word_count(self):
        # TODO NOW Zheng multiprocessing
        def sum_counter(l):
            if len(l) == 1:
                return Counter(util.read_two_columns_file_to_build_dictionary_type_specified(l[0], int, int))
            else:
                mid = len(l) // 2
                return sum_counter(l[:mid]) + sum_counter(l[mid:])

        files = util.get_files_startswith(self.dicts_folder, "word_count_")
        return dict(sum_counter(files))
        # c = Counter()
        # for file in files:
        #     counter_temp = util.read_two_columns_file_to_build_dictionary_type_specified(file, int, int)
        #     c += counter_temp
        # util.write_dict_to_file(self.dicts_folder + "word_count_all.txt", dict(c), 'str')
        # return dict(c)

    def apply(self, data_folder, process_num):
        multi_processing.master(files_getter=multi_processing.get_files_endswith,
                                data_folder=data_folder,
                                file_extension=self.local_dict_extension,
                                worker=self.fromfile,
                                process_num=process_num)
        self.merge_transferred_word_count()

    def __call__(self, data_folder, process_num):
        self.apply(data_folder, process_num)
