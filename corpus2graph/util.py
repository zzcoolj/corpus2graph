__author__ = 'Zheng ZHANG'

import nltk.data
import os
import errno
# TODO Does it still work after comment this? If not, add this in config.ini
# nltk.data.path.append("/Users/zzcoolj/Code/NLTK/nltk_data")


def tokenize_informal_paragraph_into_sentences(paragraph):
    # TODO Using Pierre's slide to make replacement rule more accurate
    paragraph = paragraph.replace(".", ". ")
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(paragraph)


def stem_word(word):
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    return ps.stem(word)


def count_time(start):
    """
    :param start:
    :return: return the time in seconds
    """
    import time
    end = time.time()
    return end-start


def search_all_specific_nodes_in_xml_known_node_path(file, node_path):
    # Element.findall() finds only elements with a tag which are direct children of the current element.
    import xml.etree.ElementTree as etree
    tree = etree.parse(file)
    root = tree.getroot()
    for node in root.findall(node_path):
        yield node.text


def read_two_columns_file_to_build_dictionary(file):
    """
    file:
        en-000000001    Food waste or food loss is food that is discarded or lost uneaten.

    Output:
        {'en-000000001': 'Food waste or food loss is food that is discarded or lost uneaten.'}
    """
    d = {}
    with open(file) as f:
        for line in f:
            (key, val) = line.rstrip('\n').split("\t")
            d[key] = val
    return d


def read_two_columns_file_to_build_dictionary_type_specified(file, key_type, value_type):
    d = {}
    with open(file, encoding='utf-8') as f:
        for line in f:
            (key, val) = line.rstrip('\n').split("\t")
            d[key_type(key)] = value_type(val)
        return d


def read_file_line_yielder(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.rstrip('\n')


def read_pickle(pickle_path):
    import pickle
    with open(pickle_path, 'rb') as fp:
        result = pickle.load(fp)
    return result


def read_valid_vocabulary(file_path):
    result = []
    with open(file_path) as f:
        for line in f:
            line_element = line.rstrip('\n')
            result.append(line_element)
    return result


def write_simple_list(file, list_to_write):
    with open(file, 'w') as f:
        for item in list_to_write:
            f.write(item + '\n')


def write_list_of_tuple(file, list_to_write):
    with open(file, 'w') as f:
        for item in list_to_write:
            f.write("%s\n" % ('\t'.join(str(item_of_item) for item_of_item in item)))


def write_to_pickle(object_to_write, pickle_path):
    import pickle
    with open(pickle_path, 'wb') as fp:
        pickle.dump(object_to_write, fp, protocol=pickle.HIGHEST_PROTOCOL)


def write_dict_type_specified(file_path, dictionary, key_type):
    with open(file_path, 'w') as f:
        if key_type is 'str':
            for key, value in dictionary.items():
                f.write('%s\t%s\n' % (str(key), str(value)))
        elif key_type is 'int':
            for key, value in dictionary.items():
                f.write('%s\t%s\n' % (int(key), float(value)))
        elif key_type is 'tuple':
            for key, value in dictionary.items():
                key_str = '\t'.join(map(str, key))
                f.write('%s\t%s\n' % (key_str, value))


def write_dict(file_path, dictionary):
    with open(file_path, 'w', encoding='utf-8') as f:
        for key, value in dictionary.items():
            f.write('%s\t%s\n' % (key, value))


def get_files_startswith(data_folder, starting):
    # Reason to add the third condition to verify files' names are not equal to 'word_count_all.txt': In case before
    # executing the code, dicts_and_encoded_texts_folder folder already has 'word_count_all.txt' file, this function
    # considers the previous word_count_all file as a normal local dict file.
    files = [os.path.join(data_folder, name) for name in os.listdir(data_folder)
             if (os.path.isfile(os.path.join(data_folder, name))
                 and name.startswith(starting)
                 and (name != 'word_count_all.txt'))]
    return files

def mkdir_p(path):
    """Create directory and all its parents if they do not exist
    This is the equivalent of Unix 'mkdir -p path'
    Parameter
    ---------
    path : str
        Path to new directory.
    Reference
    ---------
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise exc