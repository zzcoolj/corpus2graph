import os
from collections import Counter
from multiprocessing import Pool
from . import util
from . import multi_processing


class WordPairsProcessing(object):
    def __init__(self, max_vocab_size, min_count, window_size, dicts_folder, edges_folder, graph_folder,
                 safe_files_number_per_processor):
        self.max_vocab_size = max_vocab_size
        self.dicts_folder = dicts_folder
        self.min_count = min_count
        self.window_size = window_size
        self.edges_folder = edges_folder
        self.graph_folder = graph_folder
        self.safe_files_number_per_processor = safe_files_number_per_processor
        # initialize self.valid_vocabulary_path
        if (max_vocab_size == 'None') or (not max_vocab_size):
            self.valid_vocabulary_path = dicts_folder + 'valid_vocabulary_min_count_' + str(min_count) + '.txt'
        else:
            self.valid_vocabulary_path = dicts_folder + 'valid_vocabulary_min_count_' + str(min_count) + '_vocab_size_'\
                                         + str(max_vocab_size) + '.txt'

    def write_valid_vocabulary(self):
        merged_word_count = util.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'word_count_all.txt',
            key_type=str, value_type=int)
        if ((self.max_vocab_size == 'None') or (not self.max_vocab_size)) and (self.min_count == 0):
            valid_vocabulary = list(merged_word_count.keys())
        else:
            valid_word_count = {}
            for word_id, count in merged_word_count.items():
                if count >= self.min_count:
                    valid_word_count[word_id] = count
            if self.max_vocab_size and (self.max_vocab_size != 'None'):
                if int(self.max_vocab_size) < len(valid_word_count):
                    # TODO Zheng sort by value and then by key: change valid_word_count to tuple
                    valid_vocabulary = list(sorted(valid_word_count, key=valid_word_count.get, reverse=True))[
                                       :int(self.max_vocab_size)]
                else:
                    valid_vocabulary = list(valid_word_count.keys())
            else:
                valid_vocabulary = list(valid_word_count.keys())

        util.write_simple_list(self.valid_vocabulary_path, valid_vocabulary)
        return valid_vocabulary

    def get_counted_edges_worker(self, edges_files_paths):
        def counters_yielder():
            def read_edges_file_with_respect_to_valid_vocabulary(file_path, valid_vocabulary_dict):
                d = []
                with open(file_path) as f:
                    for line in f:
                        (first, second) = line.rstrip('\n').split("\t")
                        if (first in valid_vocabulary_dict) and (second in valid_vocabulary_dict):
                            d.append((first, second))
                return d

            valid_vocabulary = dict.fromkeys(util.read_valid_vocabulary(file_path=self.valid_vocabulary_path))
            for file in edges_files_paths:
                yield Counter(dict(Counter(
                    read_edges_file_with_respect_to_valid_vocabulary(file_path=file, valid_vocabulary_dict=valid_vocabulary))))

        total = len(edges_files_paths)
        print(total, "files to be counted.")
        count = 1
        counted_edges = Counter(dict())
        for c in counters_yielder():
            counted_edges += c
            print('%i/%i files processed.' % (count, total), end='\r', flush=True)
            count += 1
        # The result could be counted edges of several files (i.e. len(edges_files_paths) >= 1). Using the first file
        # name as part of the pickle file name is just to make sure the pickle name is unique (pickle file couldn't be
        # overwritten).
        util.write_to_pickle(counted_edges,
                             self.edges_folder + multi_processing.get_file_name(edges_files_paths[0]) + ".pickle")

    def multiprocessing_merge_edges_count_of_a_specific_window_size(self, process_num,
                                                                    already_existed_window_size=None):
        def counted_edges_from_worker_yielder(paths):
            for path in paths:
                yield Counter(util.read_pickle(path))

        def get_counted_edges(files, process_num=process_num):
            # Each thread processes several target edges files and save their counted_edges.
            files_size = len(files)
            num_tasks = files_size // int(self.safe_files_number_per_processor)
            if num_tasks < process_num:
                num_tasks = process_num
            if files_size <= num_tasks:  # extreme case: #files less than #tasks => use only one processor to handle all.
                num_tasks = 1
                process_num = 1
            files_list = multi_processing.chunkify(lst=files, n=num_tasks)
            # TODO test maxtasksperchild helps or not
            p = Pool(process_num, maxtasksperchild=1)

            p.starmap(self.get_counted_edges_worker,
                      zip(files_list))
            p.close()
            p.join()
            print('All sub-processes done.')

            # Merge all counted_edges from workers and get the final result.
            counted_edges_paths = multi_processing.get_files_endswith(data_folder=self.edges_folder,
                                                                      file_extension='.pickle')
            if len(counted_edges_paths) == 1:
                counted_edges = Counter(util.read_pickle(counted_edges_paths[0]))
            else:
                count = 1
                counted_edges = Counter(dict())
                for c in counted_edges_from_worker_yielder(paths=counted_edges_paths):
                    counted_edges += c
                    print('%i/%i files processed.' % (count, len(files_list)), end='\r', flush=True)
                    count += 1

            # Remove all counted_edges from workers.
            for file_path in counted_edges_paths:
                print('Remove file %s' % file_path)
                os.remove(file_path)

            return counted_edges

        # No encoded edges count already existed, calculate them from distance 2 to distance size.
        counted_edges_of_specific_window_size = None
        start_distance = 2

        # Generate counted edges of different window sizes in a stepwise way.
        if already_existed_window_size:
            if already_existed_window_size < self.window_size:
                already_existed_counted_edges_path = self.graph_folder + "encoded_edges_count_window_size_" \
                                                     + str(already_existed_window_size) + ".txt"
                d = {}
                with open(already_existed_counted_edges_path) as f:
                    for line in f:
                        (first, second, count) = line.rstrip('\n').split("\t")
                        d[(first, second)] = int(count)
                counted_edges_of_specific_window_size = Counter(d)
                start_distance = already_existed_window_size + 1
            else:
                print('[ERROR] already_existed_window_size is equal or larger than window_size: no edges information.')
                exit()

        for i in range(start_distance, self.window_size + 1):
            files_of_specific_distance = multi_processing.get_files_endswith(
                self.edges_folder, "_encoded_edges_distance_{0}.txt".format(i))
            if not files_of_specific_distance:
                print('No encoded edges file of window size ' + str(
                    self.window_size) + '. Reset window size to ' + str(
                    i - 1) + '.')
                self.window_size = i - 1
                break
            else:
                counted_edges_of_distance_i = get_counted_edges(files_of_specific_distance)
                if i == 2:
                    # counted edges of window size 2 = counted edges of distance 2
                    counted_edges_of_specific_window_size = counted_edges_of_distance_i
                else:
                    # counted edges of window size n (n>=3) = counted edges of window size n-1
                    #                                           + counted edges of distance n
                    counted_edges_of_specific_window_size += counted_edges_of_distance_i
                util.write_dict_type_specified(self.graph_folder + "encoded_edges_count_window_size_" + str(i) + ".txt",
                                               counted_edges_of_specific_window_size, 'tuple')
        return counted_edges_of_specific_window_size

    def convert_encoded_edges_count_for_undirected_graph(self, old_encoded_edges_count_path):
        """e.g.
        In old encoded edges count file:
            17  57  8
            ...
            57  17  2
        return:
            17  57  10 or 57   17  10 (only one of them will appear in the file.)


        nltk.data.path = ['/vol/datailes/tools/nlp/nltk_data/2016']

        # get undirected edges count for all file
        for i in range(2, 11):
            file_path = 'output/intermediate data/graph/encoded_edges_count_window_size_' + str(i) + '.txt'
            graph_data_provider.merge_encoded_edges_count_for_undirected_graph(file_path)
        """
        merged_weight_edges = {}
        for line in util.read_file_line_yielder(old_encoded_edges_count_path):
            (source, target, weight) = line.split("\t")
            if (target, source) in merged_weight_edges:
                # edge[source][target] inverse edge edge[target][source] already put into the merged_weight_edges
                merged_weight_edges[(target, source)] += int(weight)
            else:
                # The first time merged_weight_edges meets edge[source][target] or its inverse edge edge[target][source]
                merged_weight_edges[(source, target)] = int(weight)
        output_name = multi_processing.get_file_name(old_encoded_edges_count_path).split('.txt')[0] + '_undirected.txt'
        util.write_dict_type_specified(self.graph_folder + output_name, merged_weight_edges, 'tuple')
        return merged_weight_edges

    def apply(self, process_num):
        self.write_valid_vocabulary()
        return self.multiprocessing_merge_edges_count_of_a_specific_window_size(process_num=process_num)

    def __call__(self, process_num):
        self.apply(process_num)
