from setuptools import setup, find_packages

setup(
    name='corpus2graph',  # Required
    version='0.0.1',  # Required
    description='tools to generate graph from corpus',  # Required
    url='https://github.com/zzcoolj/corpus2graph',  # Optional
    author='Zheng Zhang and Ruiqing Yin',  # Optional
    author_email='zheng.zhang@limsi.fr',  # Optional


    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],


    packages=find_packages(),  # Required
    install_requires=['nltk >= 3.2.5',
                      'docopt >= 0.6.2'
                      ],  # Optional

    entry_points={  # Optional
        'console_scripts': [
            'graph_from_corpus=corpus2graph.applications.graph_from_corpus:main',
        ],
    },


)