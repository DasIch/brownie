# coding: utf-8
from attest import FancyReporter

import brownie.tests


brownie.tests.all.run(reporter=FancyReporter(style='native'))
