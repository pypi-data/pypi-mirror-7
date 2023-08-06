from setuptools import setup,Command,os
from setuptools.command import sdist

# Disable setup's overly-eager file finding.
sdist.finders[:]

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read() 

class veryclean(Command):
    description = 'Delete any non-source file.'
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import os
        os.system('rm -rf *.html docs/*.html')
        os.system('rm -rf *.pyc tests/*.pyc')
        os.system('rm -rf testfile.txt tests/testfile.txt')
        os.system('rm -rf build')
        os.system('rm -rf dist')
        os.system('rm -rf lookaheadtools.egg-info')

setup(
    name = 'lookaheadtools',
    cmdclass = {'veryclean':veryclean},
    version = '0.2b',
    description = 'Make any iterator a look-ahead iterator. Specialized look-ahead iterators for text files.',
    author = 'David B. Curtis',
    author_email = 'davecurtis@sonic.net',
    url = 'http://github.com/dbc/lookaheadtools',
    long_description = '\n'.join([read('README.rst'),read('NEWS.rst')]),
    license='BSD',
    platforms=['any'],
    py_modules=['lookaheadtools'],
    test_suite='tests',
)


