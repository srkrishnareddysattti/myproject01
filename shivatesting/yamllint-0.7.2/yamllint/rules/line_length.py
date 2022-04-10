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

"""
Use this rule to set a limit to lines length.

.. rubric:: Options

* ``max`` defines the maximal (inclusive) length of lines.
* ``allow-non-breakable-words`` is used to allow non breakable words (without
  spaces inside) to overflow the limit. This is useful for long URLs, for
  instance. Use ``yes`` to allow, ``no`` to forbid.

.. rubric:: Examples

#. With ``line-length: {max: 70}``

   the following code snippet would **PASS**:
   ::

    long sentence:
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna aliqua.

   the following code snippet would **FAIL**:
   ::

    long sentence:
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua.

#. With ``line-length: {max: 60, allow-non-breakable-words: yes}``

   the following code snippet would **PASS**:
   ::

    this:
      is:
        - a:
            http://localhost/very/very/very/very/very/very/very/very/long/url

    # this comment is too long,
    # but hard to split:
    # http://localhost/another/very/very/very/very/very/very/very/very/long/url

   the following code snippet would **FAIL**:
   ::

    - this line is waaaaaaaaaaaaaay too long but could be easily splitted...

#. With ``line-length: {max: 60, allow-non-breakable-words: no}``

   the following code snippet would **FAIL**:
   ::

    this:
      is:
        - a:
            http://localhost/very/very/very/very/very/very/very/very/long/url
"""


from yamllint.linter import LintProblem


ID = 'line-length'
TYPE = 'line'
CONF = {'max': int,
        'allow-non-breakable-words': bool}


def check(conf, line):
    if line.end - line.start > conf['max']:
        if conf['allow-non-breakable-words']:
            start = line.start
            while start < line.end and line.buffer[start] == ' ':
                start += 1

            if start != line.end:
                if line.buffer[start] == '#':
                    start += 2

                if line.buffer.find(' ', start, line.end) == -1:
                    return

        yield LintProblem(line.line_no, conf['max'] + 1,
                          'line too long (%d > %d characters)' %
                          (line.end - line.start, conf['max']))
