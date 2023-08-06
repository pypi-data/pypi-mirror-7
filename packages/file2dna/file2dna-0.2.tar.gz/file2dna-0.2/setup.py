
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='file2dna',
    version='0.2',
    author = 'Allan Inocencio de Souza Costa',
    author_email = 'allaninocencio@yahoo.com.br',
    description = 'A script to encode/decode arbitrary computer files into DNA sequences.',
    packages=['dna',],
    license='MIT',
    keywords= 'dna encoding decoding file',
    long_description=read('README.rst'),
    entry_points = {
        'console_scripts': ['dna=dna.dna:main'],
    }
)