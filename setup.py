# coding: utf-8
from setuptools import setup
from codecs import open


setup(
    name='Brownie',
    version='0.5.1',
    url='http://github.com/DasIch/brownie/',
    license='BSD',
    author='Daniel Neuhäuser',
    author_email='dasdasich@gmail.com',
    description='Common utilities and datastructures for Python applications.',
    # don't ever depend on refcounting to close files anywhere else
    long_description=open('README.rst', encoding='utf-8').read(),
    packages=['brownie', 'brownie.datastructures', 'brownie.tests'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ]
)
