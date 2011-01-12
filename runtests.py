# coding: utf-8
from attest import FancyReporter

from brownie.tests import all_tests


all_tests.run(reporter=FancyReporter(style='native'))
