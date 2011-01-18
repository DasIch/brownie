# coding: utf-8
from setuptools import setup
from codecs import open


setup(
    name='Brownie',
    version='0.4',
    url='http://github.com/DasIch/brownie/',
    license='BSD',
    author='Daniel Neuhäuser',
    author_email='dasdasich@gmail.com',
    description='Common utilities and datastructures for Python applications.',
    # don't ever depend on refcounting to close files anywhere else
    long_description=open('README.rst', encoding='utf-8').read(),
    packages=['brownie', 'brownie.tests'],
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
    ],
    use_2to3=True,
    test_loader='attest:Loader',
    test_suite='attest.tests.all'
)
