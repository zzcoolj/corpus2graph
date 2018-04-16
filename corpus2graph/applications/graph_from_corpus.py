"""
generate graph from file

Usage:
    graph_from_corpus all [--max_window_size=<max_window_size> --process_num=<process_num> --min_count=<min_count> --max_vocab_size=<max_vocab_size> --safe_files_number_per_processor=<safe_files_number_per_processor>] <data_dir> <output_dir>
    graph_from_corpus wordprocessing [--max_window_size=<max_window_size> --process_num=<process_num> --min_count=<min_count> --max_vocab_size=<max_vocab_size> --safe_files_number_per_processor=<safe_files_number_per_processor>] <data_dir> <output_dir>
    graph_from_corpus sentenceprocessing [--max_window_size=<max_window_size> --process_num=<process_num> --min_count=<min_count> --max_vocab_size=<max_vocab_size> --safe_files_number_per_processor=<safe_files_number_per_processor>] <data_dir> <output_dir>
    graph_from_corpus wordpairsprocessing [--max_window_size=<max_window_size> --process_num=<process_num> --min_count=<min_count> --max_vocab_size=<max_vocab_size> --safe_files_number_per_processor=<safe_files_number_per_processor>] <data_dir> <output_dir>
    graph_from_corpus -h | --help
    graph_from_corpus --version
Options:
    <data_dir>                                                            Set data directory. This script expects
                                                                          all corpus data store in this directory
    <output_dir>                                                          Set output directory. The output graph matrix and
                                                                          other intermediate data will be stored in this directory.
                                                                          see "Output directory" section for more details
    --max_window_size=<max_window_size>                                   The maximum window size to generate the word pairs.
                                                                          [default: 5]
    --process_num=<process_num>                                           The number of process you want to use.
                                                                          [default: 3]
    --min_count=<min_count>                                               Mininum count for words.
                                                                          [default: 5]
    --max_vocab_size=<max_vocab_size>                                     The maximum number of words you want to use.
                                                                          [default: 10000]
    --safe_files_number_per_processor=<safe_files_number_per_processor>   Safe files number per processor
                                                                          [default: 200]
    -h --help                                                             Show this screen.
    --version                                                             Show version.
Output directory:
    Three sub-directory will be generated:
    --output_dir
         --dicts_and_encoded_texts                  store the encode data for words
         --edges                                    store the edges data
         --graph                                    store the graph
        ...................................................................
"all" mode:
        Genrerate the graph from corpus.
"wordprocessing" mode:
        Todo
"sentenceprocessing" mode:
        Todo
"wordpairsprocessing" mode:
        Todo
"""

from corpus2graph import Tokenizer, WordProcessing, SentenceProcessing, WordPairsProcessing, util
from docopt import docopt
import time

def main():
    arguments = docopt(__doc__, version='1.O.O')

    data_folder = arguments['<data_dir>']
    if not data_folder.endswith('/'):
        data_folder += '/'
    output_folder = arguments['<output_dir>']
    if not output_folder.endswith('/'):
        output_folder += '/'
    dicts_folder = output_folder + 'dicts_and_encoded_texts/'
    edges_folder = output_folder + 'edges/'
    graph_folder = output_folder + 'graph/'

    util.mkdir_p(output_folder)
    util.mkdir_p(dicts_folder)
    util.mkdir_p(edges_folder)
    util.mkdir_p(graph_folder)

    max_window_size = int(arguments['--max_window_size'])
    process_num = int(arguments['--process_num'])
    min_count = int(arguments['--min_count'])
    max_vocab_size = int(arguments['--max_vocab_size'])
    safe_files_number_per_processor = int(arguments['--safe_files_number_per_processor'])

    if arguments['all']:
        start_time = time.time()
        wp = WordProcessing(output_folder=dicts_folder, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                            remove_numbers=False, remove_punctuations=False, stem_word=False, lowercase=False)
        merged_dict = wp.apply(data_folder=data_folder, process_num=process_num)
        sp = SentenceProcessing(dicts_folder=dicts_folder, output_folder=edges_folder,
                                max_window_size=max_window_size, local_dict_extension='.dicloc')
        word_count_all = sp.apply(data_folder=dicts_folder, process_num=process_num)
        wpp = WordPairsProcessing(max_vocab_size=max_vocab_size, min_count=min_count,
                                  dicts_folder=dicts_folder, window_size=max_window_size,
                                  edges_folder=edges_folder, graph_folder=graph_folder,
                                  safe_files_number_per_processor=safe_files_number_per_processor)
        result = wpp.apply(process_num=process_num)
        # wpp.multiprocessing_merge_edges_count_of_a_specific_window_size(process_num=process_num, already_existed_window_size=4)
        print('time in seconds:', util.count_time(start_time))

    if arguments['wordprocessing']:
        start_time = time.time()
        wp = WordProcessing(output_folder=dicts_folder, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                            remove_numbers=False, remove_punctuations=False, stem_word=False, lowercase=False)
        merged_dict = wp.apply(data_folder=data_folder, process_num=process_num)
        print('time for word processing in seconds:', util.count_time(start_time))

    if arguments['sentenceprocessing']:
        start_time = time.time()
        sp = SentenceProcessing(dicts_folder=dicts_folder, output_folder=edges_folder,
                                max_window_size=max_window_size, local_dict_extension='.dicloc')
        word_count_all = sp.apply(data_folder=dicts_folder, process_num=process_num)
        print('time for sentence processing in seconds:', util.count_time(start_time))

    if arguments['wordpairsprocessing']:
        start_time = time.time()
        wpp = WordPairsProcessing(max_vocab_size=max_vocab_size, min_count=min_count,
                                  dicts_folder=dicts_folder, window_size=max_window_size,
                                  edges_folder=edges_folder, graph_folder=graph_folder,
                                  safe_files_number_per_processor=safe_files_number_per_processor)
        result = wpp.apply(process_num=process_num)
        # wpp.multiprocessing_merge_edges_count_of_a_specific_window_size(process_num=process_num, already_existed_window_size=4)
        print('time for word pairs processing in seconds:', util.count_time(start_time))
