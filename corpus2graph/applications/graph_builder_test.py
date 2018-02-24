import unittest


class TestGraphBuilder(unittest.TestCase):
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

    def test(self):
        self.assertRaises(True)
