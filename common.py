__author__ = 'Zheng ZHANG'

import nltk.data
nltk.data.path.append("/Users/zzcoolj/Code/NLTK/nltk_data")


def randomly_select_lines(file_original, file_new, selection_quantity, starting_line=0, ending_with=''):
    import random

    with open(file_original) as f:
        content = f.readlines()

    # add a string to the end of each line
    if not ending_with:
        content = [x for x in content]
    else:
        content = [(x.strip() + ending_with + '\n') for x in content]

    # remove the first starting_line lines
    del content[0:starting_line]

    if selection_quantity > len(content):
        exit("The number of selection lines (" + str(selection_quantity)
             + ") is bigger than original file size ("
             + str(len(content)) + ") ")

    # sample function will not take the same line twice
    random_list = random.sample(content, selection_quantity)

    with open(file_new, 'w') as f:
        f.writelines(random_list)


def tokenize_text_into_sentences(file):
    # Tokenize Punkt module has many pre-trained tokenize model for many european languages.
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    fp = open(file)
    data = fp.read()
    # print(nltk.word_tokenize(data))
    return tokenizer.tokenize(data)


def tokenize_paragraph_into_sentences(paragraph):
    # TODO Attention:
    """
    It works for paragraph like:
        and "Down with Japanese imperialism". The movement then spread to other parts of China
    But does not work for:
        and "Down with Japanese imperialism".The movement then spread to other parts of China
    It needs "." comes with a space
    """

    # Tokenize Punkt module has many pre-trained tokenize model for many european languages.
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(paragraph)


def tokenize_informal_paragraph_into_sentences(paragraph):
    # TODO Using Pierre's slide to make replacement rule more accurate
    paragraph = paragraph.replace(".", ". ")

    # Tokenize Punkt module has many pre-trained tokenize model for many european languages.
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(paragraph)


def tokenize_text_into_words(text, word_tokenizer='Treebank'):
    if word_tokenizer == 'Treebank':
        from nltk.tokenize import TreebankWordTokenizer
        tokenizer = TreebankWordTokenizer()
    elif word_tokenizer == 'PunktWord':
        # PunktTokenizer splits on punctuation, but keeps it with the word. => [‘this’, “‘s”, ‘a’, ‘test’]
        from nltk.tokenize import PunktWordTokenizer
        tokenizer = PunktWordTokenizer()
    elif word_tokenizer == 'WordPunct':
        # WordPunctTokenizer splits all punctuations into separate tokens. => [‘This’, “‘”, ‘s’, ‘a’, ‘test’]
        from nltk.tokenize import WordPunctTokenizer
        tokenizer = WordPunctTokenizer()
    else:
        return -1
    return tokenizer.tokenize(text)


def stem_word(word):
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    return ps.stem(word)


def count_time(start):
    # return the time in seconds
    import time

    end = time.time()
    return end-start


def search_all_specific_nodes_in_xml_known_only_node_name(file, node_name):
    # Element.iter(): iterate recursively over all the sub-tree below it (its children, their children, and so on)
    import xml.etree.ElementTree as etree
    tree = etree.parse(file)
    root = tree.getroot()
    for paragraph in root.iter(node_name):
        yield paragraph.text


def search_all_specific_nodes_in_xml_known_node_path(file, node_path):
    # Element.findall() finds only elements with a tag which are direct children of the current element.
    import xml.etree.ElementTree as etree
    tree = etree.parse(file)
    root = tree.getroot()
    for node in root.findall(node_path):
        yield node.text


# File Functions

def read_first_column_file_to_build_set(file):
    d = set()
    with open(file) as f:
        for line in f:
            (key, val) = line.rstrip('\n').split("\t")
            d.add(key)
    return d


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
            d[key_type(key)] = value_type(val)
    return d


def read_two_specific_columns_to_build_dictionary_type_specified_comment_allowed(
        file, key_column, key_type, value_column, value_type, comment_mark):
    d = {}
    with open(file) as f:
        for line in f:
            if line[0] in comment_mark: continue
            print(line)

            elements = line.rstrip('\n').split("\t")
            print(elements)
            print(len(elements))
            key = elements[key_column]
            val = elements[value_column]
            d[key_type(key)] = value_type(val)
    return d


def read_two_columns_file_to_build_list_of_tuples_type_specified(file, first_column_type, second_column_type):
    d = []
    with open(file) as f:
        for line in f:
            (first, second) = line.rstrip('\n').split("\t")
            d.append((first_column_type(first), second_column_type(second)))
    return d


def read_n_columns_file_to_build_dict(file_path):
    d = {}
    with open(file_path) as f:
        for line in f:
            elements = line.rstrip('\n').split("\t")
            key = elements[0]
            val = elements[1:]
            d[key] = val
    return d


def read_n_columns_file_to_build_list_of_lists_type_specified(file_path, types):
    l = []
    with open(file_path) as f:
        for line in f:
            line_elements = line.rstrip('\n').split("\t")
            for i in range(len(line_elements)):
                line_elements[i] = types[i](line_elements[i])
            l.append(line_elements)
    return l


def read_file_line_yielder(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.rstrip('\n')


def read_pickle(pickle_path):
    import pickle
    with open(pickle_path, 'rb') as fp:
        result = pickle.load(fp)
    return result


def build_translation_file(fileA, fileB, fileAB, file_new):
    """
    fileAB：
        zh-000000176    en-000093983
        zh-000000206    en-000139179
    fileA:
        zh-000000002    包括理论心理学与应用心理学两大领域
    fileB:
        en-000000001    Food waste or food loss is food that is discarded or lost uneaten.

    Output:
        zh-000000206	此外还需要大量数据处理， 病历记录才能便于使用。	en-000139179	It also requires a lot of data processing to make the records usable.
    """
    da = read_two_columns_file_to_build_dictionary(fileA)
    db = read_two_columns_file_to_build_dictionary(fileB)

    with open(file_new, 'w') as f:
        with open(fileAB) as fAB:
            for lineAB in fAB:
                da_key, db_key = lineAB.rstrip('\n').split("\t")
                f.write(da_key + "\t" + da[da_key] + "\t" + db_key + "\t" + db[db_key] + "\n")


def write_simple_list_to_file(file, list_to_write):
    with open(file, 'w') as f:
        for item in list_to_write:
            f.write(item + '\n')


def write_list_to_file(file, list_to_write):
    with open(file, 'w') as f:
        for item in list_to_write:
            f.write("%s\n" % ('\t'.join(str(item_of_item) for item_of_item in item)))


def write_to_pickle(object_to_write, pickle_path):
    import pickle
    with open(pickle_path, 'wb') as fp:
        pickle.dump(object_to_write, fp, protocol=pickle.HIGHEST_PROTOCOL)


# TODO merge write_dict_to_file & write_dict_to_file_value_type_specified to key and value specified function
def write_dict_to_file(file_path, dictionary, key_type):
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


def write_dict_to_file_value_type_specified(file_path, dictionary, value_type):
    f = open(file_path, 'w')
    if value_type is str:
        for key, value in dictionary.items():
            f.write('%s\t%s\n' % (key, value))
    elif value_type is list:
        for key, value in dictionary.items():
            value_str = '\t'.join(value)
            f.write('%s\t%s\n' % (key, value_str))





# TESTS
# randomly_select_lines("/Users/zzcoolj/Code/word2vec/data/questions-words.txt", "word2vec_city_country.txt", 250, 1, ".")

# print(tokenize_text_into_sentences("/Users/zzcoolj/Code/GoW/data/test.txt"))

# print(tokenize_text_into_words("Before their execution, detainees were brought before a \"military field court\" in the capital's Qaboun district for \"trials\" lasting between one and three minutes, the report says."))

# print(read_two_columns_file_to_build_dictionary("/Users/zzcoolj/Code/BUCC/bucc2017/zh-en/zh-en.training.en"))

# build_translation_file("/Users/zzcoolj/Code/BUCC/bucc2017/zh-en/zh-en.training.zh",
#                        "/Users/zzcoolj/Code/BUCC/bucc2017/zh-en/zh-en.training.en",
#                        "/Users/zzcoolj/Code/BUCC/bucc2017/zh-en/zh-en.training.gold",
#                        "test.txt")

# for test in search_all_specific_nodes_in_xml_known_only_node_name("/Users/zzcoolj/Code/GoW/data/aquaint-2_sample_xin_eng_200512.xml", "P"):
#     print(test)
#
# for test in search_all_specific_nodes_in_xml_known_node_path("/Users/zzcoolj/Code/GoW/data/aquaint-2_sample_xin_eng_200512.xml", "./DOC/TEXT/P"):
#     print(test)

# print(read_two_columns_file_to_build_dictionary_type_specified('../GoW/data/dicts/dict_xin_eng_200410.dicloc', str, int))
