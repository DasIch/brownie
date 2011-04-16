# coding: utf-8
"""
    brownie.terminal
    ~~~~~~~~~~~~~~~~

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from brownie.terminal import TerminalWriter, _colour_names, ATTRIBUTES

writer = TerminalWriter(sys.stdout)
for name in _colour_names:
    with writer.line():
        writer.write(name, text_colour=name)

    with writer.line():
        writer.write(name, background_colour=name)

for name in ATTRIBUTES:
    if name == 'reset':
        continue
    writer.writeline(name, **{name: True})

with writer.line():
    with writer.options(underline=True):
        writer.write('underline')
        with writer.options(background_colour='red'):
            writer.write('background')
            writer.write('text', text_colour='green')
            writer.write('background')
        writer.write('underline')
