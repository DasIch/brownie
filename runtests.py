# coding: utf-8
import sys

from attest import FancyReporter

from brownie.importing import import_string


def main(tests=sys.argv[1:]):
    prefix = 'brownie.tests.'
    if not tests:
        tests = ['all']
    for module in (import_string(prefix + test) for test in tests):
        module.tests.run(reporter=FancyReporter(style='native'))


if __name__ == '__main__':
    main()
