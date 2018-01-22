import unittest
from corpus2graph.graph_data_provider import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing


class TestGraphDataProvider(unittest.TestCase):
    """ ATTENTION
    Normally, data_folder and output_folder should be user defined paths (absolute paths).
    For unittest, as input and output folders locations are fixed, these two paths are exceptionally relative paths.
    """
    data_folder = 'unittest_data/'
    output_folder = 'output/'
    # TODO create edges, dicts, graph folder based on output_folder, no need to define them below.
    dicts_folder = output_folder + 'dicts_and_encoded_texts/'
    edges_folder = output_folder + 'edges/'
    graph_folder = output_folder + 'graph/'

    file_extension = '.txt'
    max_window_size = 6
    process_num = 3
    data_type = 'txt'
    min_count = 5
    max_vocab_size = 3

    # APIs
    def test_word_preprocessor(self):
        wp = WordPreprocessor()
        result1 = wp.apply('18')
        self.assertEqual(result1, '')
        result2 = wp.apply(',')
        self.assertEqual(result2, '')
        result3 = wp.apply('Hello')
        self.assertEqual(result3, 'hello')

    def test_file_parser(self):
        tfp = FileParser()
        filepath = 'unittest_data/AA/wiki_03.txt'
        lines = list(tfp(filepath))
        reflines = ['alfred hitchcock', 'sir alfred joseph hitchcock ( 00 august 0000 – 00 april 0000 ) was '
                                        'an english film director and producer , at times referred to as " the master of suspense " .he pioneered many elements of the suspense and psychological thriller genres .']
        # TODO test by assertEqual, ('\n' is added to the end of the sentence)
        #self.assertEqual(lines, reflines)

    def test_tokenizer(self):
        # TODO test PunktWord
        tknizer = Tokenizer(word_tokenizer='WordPunct')
        result = tknizer.apply("this's a test")
        self.assertEqual(result, ['this', "'", "s", 'a', 'test'])

    # main classes
    def test_word_processing(self):
        wp = WordProcessing(output_folder=self.dicts_folder)
        # wp.fromfile(self.data_folder + 'AA/wiki_03.txt')
        wp.apply(data_folder=self.data_folder, process_num=self.process_num)

    def test_sentence_processing(self):
        sp = SentenceProcessing(dicts_folder=self.dicts_folder, output_folder=self.edges_folder,
                                max_window_size=self.max_window_size)
        # sp.fromfile(self.dicts_folder + 'dict_AA_wiki_03.dicloc')
        sp.apply(data_folder=self.dicts_folder, process_num=self.process_num)

    def test_word_pairs_processing(self):
        wpp = WordPairsProcessing(max_vocab_size=self.max_vocab_size, min_count=self.min_count,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder)
        wpp.apply(process_num=self.process_num)


if __name__ == '__main__':
    unittest.main()
