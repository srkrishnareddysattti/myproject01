# -*- coding: utf-8 -*-
# Copyright (C) 2016 Adrien Vergé
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tests.common import RuleTestCase


class LineLengthTestCase(RuleTestCase):
    rule_id = 'line-length'

    def test_disabled(self):
        conf = ('line-length: disable\n'
                'empty-lines: disable\n'
                'new-line-at-end-of-file: disable\n'
                'document-start: disable\n')
        self.check('', conf)
        self.check('\n', conf)
        self.check('---\n', conf)
        self.check(81 * 'a', conf)
        self.check('---\n' + 81 * 'a' + '\n', conf)
        self.check(1000 * 'b', conf)
        self.check('---\n' + 1000 * 'b' + '\n', conf)

    def test_default(self):
        conf = ('line-length: {max: 80}\n'
                'empty-lines: disable\n'
                'new-line-at-end-of-file: disable\n'
                'document-start: disable\n')
        self.check('', conf)
        self.check('\n', conf)
        self.check('---\n', conf)
        self.check(80 * 'a', conf)
        self.check('---\n' + 80 * 'a' + '\n', conf)
        self.check(16 * 'aaaa ' + 'z', conf, problem=(1, 81))
        self.check('---\n' + 16 * 'aaaa ' + 'z' + '\n', conf, problem=(2, 81))
        self.check(1000 * 'word ' + 'end', conf, problem=(1, 81))
        self.check('---\n' + 1000 * 'word ' + 'end\n', conf, problem=(2, 81))

    def test_max_length_10(self):
        conf = ('line-length: {max: 10}\n'
                'new-line-at-end-of-file: disable\n')
        self.check('---\nABCD EFGHI', conf)
        self.check('---\nABCD EFGHIJ', conf, problem=(2, 11))
        self.check('---\nABCD EFGHIJ\n', conf, problem=(2, 11))

    def test_spaces(self):
        conf = ('line-length: {max: 80}\n'
                'new-line-at-end-of-file: disable\n'
                'trailing-spaces: disable\n')
        self.check('---\n' + 81 * ' ', conf, problem=(2, 81))
        self.check('---\n' + 81 * ' ' + '\n', conf, problem=(2, 81))

    def test_non_breakable_word(self):
        conf = 'line-length: {max: 20, allow-non-breakable-words: yes}'
        self.check('---\n' + 30 * 'A' + '\n', conf)
        self.check('---\n'
                   'this:\n'
                   '  is:\n'
                   '    - a:\n'
                   '        http://localhost/very/long/url\n'
                   '...\n', conf)
        self.check('---\n'
                   'this:\n'
                   '  is:\n'
                   '    - a:\n'
                   '        # http://localhost/very/long/url\n'
                   '        comment\n'
                   '...\n', conf)

        conf = 'line-length: {max: 20, allow-non-breakable-words: no}'
        self.check('---\n' + 30 * 'A' + '\n', conf, problem=(2, 21))
        self.check('---\n'
                   'this:\n'
                   '  is:\n'
                   '    - a:\n'
                   '        http://localhost/very/long/url\n'
                   '...\n', conf, problem=(5, 21))
        self.check('---\n'
                   'this:\n'
                   '  is:\n'
                   '    - a:\n'
                   '        # http://localhost/very/long/url\n'
                   '        comment\n'
                   '...\n', conf, problem=(5, 21))
