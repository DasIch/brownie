# coding: utf-8
from setuptools import setup


setup(
    name='Brownie',
    version='0.1.1',
    url='http://github.com/DasIch/brownie/',
    license='BSD',
    author='Daniel Neuhäuser',
    author_email='dasdasich@gmail.com',
    description='Common utilities and datastructures for Python applications.',
    # don't ever depend on refcounting to close files anywhere else
    long_description=open('README.rst').read().decode('utf-8'),
    packages=['brownie'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
    ]
)
