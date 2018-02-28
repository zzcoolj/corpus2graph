import unittest
import warnings
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing, util
import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class TestProcessors(unittest.TestCase):
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

        def toto(word):
            return ''

        wp = WordPreprocessor(remove_numbers = False, remove_punctuations = False,
                 stem_word = False, lowercase = False, wpreprocessor = toto)
        result4 = wp.apply('Hello')
        self.assertEqual(result4, '')
        with warnings.catch_warnings(record=True) as w:
            wp = WordPreprocessor(remove_numbers=False, remove_punctuations=False,
                                  stem_word=False, lowercase=False, wpreprocessor='toto')
            result5 = wp.apply('Hello')
            assert "wpreprocessor" in str(w[-1].message)

        def titi(word):
            return None

        wp = WordPreprocessor(remove_numbers=False, remove_punctuations=False,
                              stem_word=False, lowercase=False, wpreprocessor=titi)
        self.assertRaises(ValueError, wp, 'hello')

    def test_file_parser(self):
        tfp = FileParser()
        filepath = 'unittest_data/AA/wiki_03.txt'
        lines = list(tfp(filepath))
        reflines = ['alfred hitchcock', 'sir alfred joseph hitchcock ( 00 august 0000 – 00 april 0000 ) was '
                                        'an english film director and producer , at times referred to as " the master of suspense " .he pioneered many elements of the suspense and psychological thriller genres .']
        # TODO test by assertEqual, ('\n' is added to the end of the sentence)
        # TODO test xml and txt parser
        # TODO NOW user defined parser function
        #self.assertEqual(lines, reflines)

        # TODO problem in test code, no problem in source code
        # tfp = FileParser('txxt')
        # self.assertRaises(ValueError, tfp, filepath)

        #self.assertRaises(ValueError, FileParser(file_parser='defined',
        #                xml_node_path=None, fparser=None), filepath)

        def txt_parser(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    yield line

        tfp = FileParser(file_parser='defined',
                        xml_node_path=None, fparser=txt_parser)
        filepath = 'unittest_data/AA/wiki_03.txt'
        lines = list(tfp(filepath))
        #print(lines)

    def test_tokenizer(self):
        # TODO test PunktWord
        tknizer = Tokenizer(word_tokenizer='WordPunct')
        result = tknizer.apply("this's a test")
        self.assertEqual(result, ['this', "'", "s", 'a', 'test'])

        def mytok(s):
            return list(s)

        tknizer = Tokenizer(word_tokenizer='', wtokenizer=mytok)
        self.assertEqual(tknizer('h l'), ['h', ' ', 'l'])

        # tknizer = Tokenizer(word_tokenizer='tree')
        # tknizer = Tokenizer(word_tokenizer='', wtokenizer='tt')
        self.assertRaises(ValueError, Tokenizer, 'tree')

        with warnings.catch_warnings(record=True) as w:
            tknizer = Tokenizer(word_tokenizer='', wtokenizer='tt')
            assert "wtokenizer" in str(w[-1].message)


if __name__ == '__main__':
    unittest.main()
