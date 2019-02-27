# corpus2graph

## Installation
```bash
$ conda create --name corpus2graph python=3.6 anaconda
$ source activate corpus2graph
$ git clone https://github.com/zzcoolj/corpus2graph.git
$ cd corpus2graph
$ pip install -e .
```

## Corpus requirements
* All text files should be in subfolders of ```<data-dir>``` (DO NOT put them directly in ```<data-dir>```); 
If there is only one text file, this tool will automatically provide you an option to split the file into several smaller files to benefit from multi-processing.
* If you use the default parser ```txt_parser```, please make sure that your text files meet the "one sentence per line" requirement. 

## Usage:
```bash
$ graph_from_corpus -h
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
```

## Frequently asked questions
* I got ```[ERROR] No valid files in the data folder.``` and how to solve it?
    * Please put all of your text files in subfolders of ```<data-dir>```, not directly in ```<data-dir>```.
    * Please make sure that your text files extensions are the same and are among ```txt```, ```xml``` and ```defined```.
    The file parser ```fparser``` must be defined in ```word_processor.py``` if the file extension is ```defined```.
* Will the organization (structure) of files in data folder influence the processing speed? 
For instance, is there any difference between the data folder which has only one sub-folder with 100 files inside and the data folder which contains ten sub-folders with 10 files in each
(under the condition that these 100 files are identical)?
    * No, there's no difference. 
    This tool will generate a list of all valid text files before multiprocessing. 


## Citation
If you use this tool, please cite the following paper:
```bash
@inproceedings{Zheng2018Eff,
  Author = {Zheng Zhang and Ruiqing Yin and Pierre Zweigenbaum},
  Title = {{Efficient Generation and Processing of Word Co-occurrence Networks Using corpus2graph}},
  Booktitle = {{TextGraphs workshop in NAACL 2018, 16th Annual Conference of the North American Chapter of the Association for Computational Linguistics}},
  Year = {2018},
  Month = {June},
  Url = {https://github.com/zzcoolj/corpus2graph}
}
```