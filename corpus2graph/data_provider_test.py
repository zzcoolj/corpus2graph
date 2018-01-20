import unittest
from graph_data_provider import FileParser, WordPreprocessor, Tokenizer, WordProcessing, SentenceProcessing

class TestGraphDataProvider(unittest.TestCase):
    data_folder = 'data/training data/unittest_data/'
    file_extension = '.txt'
    max_window_size = 6
    process_num = 4
    data_type = 'txt'
    dicts_folder = 'output/intermediate data for unittest/dicts_and_encoded_texts/'
    edges_folder = 'output/intermediate data for unittest/edges/'
    graph_folder = 'output/intermediate data for unittest/graph/'
    min_count = 5
    max_vocab_size = 3

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
        filepath = '/Users/yin/projects/corpus2graph/corpus2graph/unittest_data/AA/wiki_03.txt'
        lines = list(tfp(filepath))
        reflines = ['alfred hitchcock', 'sir alfred joseph hitchcock ( 00 august 0000 – 00 april 0000 ) was '
                                        'an english film director and producer , at times referred to as " the master of suspense " .he pioneered many elements of the suspense and psychological thriller genres .']
        #self.assertEqual(lines, reflines)
        # TODO
        print(lines)

    def test_tokenizer(self):
        # TODO test PunktWord
        tknizer = Tokenizer(word_tokenizer='WordPunct')
        result = tknizer.apply("this's a test")
        self.assertEqual(result, ['this', "'", "s", 'a', 'test'])

    def test_word_processing(self):
        wp = WordProcessing('output/intermediate data for unittest/dicts_and_encoded_texts/')
        wp.fromfile('/Users/yin/projects/corpus2graph/corpus2graph/unittest_data/ZT/wiki_95.txt')
        wp.merge_local_dict()

    def test_sentence_processing(self):
        sp = SentenceProcessing('output/intermediate data for unittest/dicts_and_encoded_texts/', 'output/intermediate data for unittest/edges/', 6)
        sp.fromfile('/Users/yin/projects/corpus2graph/corpus2graph/output/intermediate data for unittest/dicts_and_encoded_texts/dict_AA_wiki_03.dicloc')
        sp.merge_transferred_word_count()
if __name__ == '__main__':
    unittest.main()
