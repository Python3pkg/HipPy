import hippy
from setuptools import setup

setup(
    name=hippy.__title__,
    version=hippy.__version__,
    author=hippy.__author__,
    author_email=hippy.__email__,
    description=hippy.__description__,
    long_description=open('README.rst').read(),
    url=hippy.__homepage__,
    download_url=hippy.__download__,
    packages=['hippy'],
)
