# coding: utf-8
import sys

from attest import FancyReporter

from brownie.importing import import_string


def main(tests=sys.argv[1:]):
    prefix = 'brownie.tests.'
    if not tests:
        import_string(prefix + 'all').run(
            reporter=FancyReporter(style='native')
        )
    for tests in (import_string(prefix + test + '.tests') for test in tests):
        tests.run(reporter=FancyReporter(style='native'))


if __name__ == '__main__':
    main()
