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
Use this rule to control the indentation.

.. rubric:: Options

* ``spaces`` defines the number of spaces that represent an indentation level.
* ``indent-sequences`` defines whether block sequences should be indented or
  not (when in a mapping, this indentation is not mandatory -- some people
  perceive the ``-`` as part of the indentation). Possible values: ``yes``,
  ``no`` and ``whatever`` (the latter means either indenting or not indenting
  block sequences is OK.
* ``check-multi-line-strings`` defines whether to lint indentation in
  multi-line strings. Set to ``yes`` to enable, ``no`` to disable.

.. rubric:: Examples

#. With ``indentation: {spaces: 1}``

   the following code snippet would **PASS**:
   ::

    history:
     - name: Unix
       date: 1969
     - name: Linux
       date: 1991
    nest:
     recurse:
      - haystack:
         needle

#. With ``indentation: {spaces: 4}``

   the following code snippet would **PASS**:
   ::

    history:
        - name: Unix
          date: 1969
        - name: Linux
          date: 1991
    nest:
        recurse:
            - haystack:
                  needle

   the following code snippet would **FAIL**:
   ::

    history:
      - name: Unix
        date: 1969
      - name: Linux
        date: 1991
    nest:
      recurse:
        - haystack:
            needle

#. With ``indentation: {spaces: 2, indent-sequences: no}``

   the following code snippet would **PASS**:
   ::

    list:
    - flying
    - spaghetti
    - monster

   the following code snippet would **FAIL**:
   ::

    list:
      - flying
      - spaghetti
      - monster

#. With ``indentation: {spaces: 2, indent-sequences: whatever}``

   the following code snippet would **PASS**:
   ::

    list:
    - flying:
      - spaghetti
      - monster
    - not flying:
        - spaghetti
        - sauce

#. With ``indentation: {spaces: 4, check-multi-line-strings: yes}``

   the following code snippet would **PASS**:
   ::

    Blaise Pascal:
        Je vous écris une longue lettre parce que
        je n'ai pas le temps d'en écrire une courte.

   the following code snippet would **PASS**:
   ::

    Blaise Pascal: Je vous écris une longue lettre parce que
                   je n'ai pas le temps d'en écrire une courte.

   the following code snippet would **FAIL**:
   ::

    Blaise Pascal: Je vous écris une longue lettre parce que
      je n'ai pas le temps d'en écrire une courte.

   the following code snippet would **FAIL**:
   ::

    C code:
        void main() {
            printf("foo");
        }

   the following code snippet would **PASS**:
   ::

    C code:
        void main() {
        printf("bar");
        }
"""

import yaml

from yamllint.linter import LintProblem
from yamllint.rules.common import is_explicit_key, get_real_end_line


ID = 'indentation'
TYPE = 'token'
CONF = {'spaces': int,
        'indent-sequences': (True, False, 'whatever'),
        'check-multi-line-strings': bool}

ROOT, B_MAP, F_MAP, B_SEQ, F_SEQ, B_ENT, KEY, VAL = range(8)
labels = ('ROOT', 'B_MAP', 'F_MAP', 'B_SEQ', 'F_SEQ', 'B_ENT', 'KEY', 'VAL')


class Parent(object):
    def __init__(self, type, indent, line_indent=None):
        self.type = type
        self.indent = indent
        self.line_indent = line_indent
        self.explicit_key = False
        self.implicit_block_seq = False

    def __repr__(self):
        return '%s:%d' % (labels[self.type], self.indent)


def check_scalar_indentation(conf, token, context):
    if token.start_mark.line == token.end_mark.line:
        return

    if token.plain:
        expected_indent = token.start_mark.column
    elif token.style in ('"', "'"):
        expected_indent = token.start_mark.column + 1
    elif token.style in ('>', '|'):
        if context['stack'][-1].type == B_SEQ:
            # - >
            #     multi
            #     line
            expected_indent = token.start_mark.column + conf['spaces']
        elif context['stack'][-1].type == KEY:
            assert context['stack'][-1].explicit_key
            # - ? >
            #       multi-line
            #       key
            #   : >
            #       multi-line
            #       value
            expected_indent = token.start_mark.column + conf['spaces']
        elif context['stack'][-1].type == VAL:
            if token.start_mark.line + 1 > context['cur_line']:
                # - key:
                #     >
                #       multi
                #       line
                expected_indent = context['stack'][-1].indent + conf['spaces']
            elif context['stack'][-2].explicit_key:
                # - ? key
                #   : >
                #       multi-line
                #       value
                expected_indent = token.start_mark.column + conf['spaces']
            else:
                # - key: >
                #     multi
                #     line
                expected_indent = context['stack'][-2].indent + conf['spaces']
        else:
            expected_indent = context['stack'][-1].indent + conf['spaces']

    line_no = token.start_mark.line + 1

    line_start = token.start_mark.pointer
    while True:
        line_start = token.start_mark.buffer.find(
            '\n', line_start, token.end_mark.pointer - 1) + 1
        if line_start == 0:
            break
        line_no += 1

        indent = 0
        while token.start_mark.buffer[line_start + indent] == ' ':
            indent += 1
        if token.start_mark.buffer[line_start + indent] == '\n':
            continue

        if indent != expected_indent:
            yield LintProblem(line_no, indent + 1,
                              'wrong indentation: expected %d but found %d' %
                              (expected_indent, indent))


def check(conf, token, prev, next, nextnext, context):
    if 'stack' not in context:
        context['stack'] = [Parent(ROOT, 0)]
        context['cur_line'] = -1

    # Step 1: Lint

    is_visible = (
        not isinstance(token, (yaml.StreamStartToken, yaml.StreamEndToken)) and
        not isinstance(token, yaml.BlockEndToken) and
        not (isinstance(token, yaml.ScalarToken) and token.value == ''))
    first_in_line = (is_visible and
                     token.start_mark.line + 1 > context['cur_line'])

    if first_in_line:
        found_indentation = token.start_mark.column
        expected = context['stack'][-1].indent

        if isinstance(token, (yaml.FlowMappingEndToken,
                              yaml.FlowSequenceEndToken)):
            expected = context['stack'][-1].line_indent
        elif (context['stack'][-1].type == KEY and
                context['stack'][-1].explicit_key and
                not isinstance(token, yaml.ValueToken)):
            expected += conf['spaces']

        if found_indentation != expected:
            yield LintProblem(token.start_mark.line + 1, found_indentation + 1,
                              'wrong indentation: expected %d but found %d' %
                              (expected, found_indentation))

    if (isinstance(token, yaml.ScalarToken) and
            conf['check-multi-line-strings']):
        for problem in check_scalar_indentation(conf, token, context):
            yield problem

    # Step 2.a:

    if is_visible:
        context['cur_line'] = get_real_end_line(token)
        if first_in_line:
            context['cur_line_indent'] = found_indentation

    # Step 2.b: Update state

    if isinstance(token, yaml.BlockMappingStartToken):
        assert isinstance(next, yaml.KeyToken)
        if next.start_mark.line == token.start_mark.line:
            #   - a: 1
            #     b: 2
            # or
            #   - ? a
            #     : 1
            indent = token.start_mark.column
        else:
            #   - ?
            #       a
            #     : 1
            indent = token.start_mark.column + conf['spaces']

        context['stack'].append(Parent(B_MAP, indent))

    elif isinstance(token, yaml.FlowMappingStartToken):
        if next.start_mark.line == token.start_mark.line:
            #   - {a: 1, b: 2}
            indent = next.start_mark.column
        else:
            #   - {
            #     a: 1, b: 2
            #   }
            indent = context['cur_line_indent'] + conf['spaces']

        context['stack'].append(Parent(F_MAP, indent,
                                       line_indent=context['cur_line_indent']))

    elif isinstance(token, yaml.BlockSequenceStartToken):
        #   - - a
        #     - b
        assert next.start_mark.line == token.start_mark.line
        assert isinstance(next, yaml.BlockEntryToken)

        indent = token.start_mark.column

        context['stack'].append(Parent(B_SEQ, indent))

    elif (isinstance(token, yaml.BlockEntryToken) and
            # in case of an empty entry
            not isinstance(next, (yaml.BlockEntryToken, yaml.BlockEndToken))):
        # It looks like pyyaml doesn't issue BlockSequenceStartTokens when the
        # list is not indented. We need to compensate that.
        if context['stack'][-1].type != B_SEQ:
            context['stack'].append(Parent(B_SEQ, token.start_mark.column))
            context['stack'][-1].implicit_block_seq = True

        if next.start_mark.line == token.end_mark.line:
            #   - item 1
            #   - item 2
            indent = next.start_mark.column
        else:
            #   -
            #     item 1
            #   -
            #     key:
            #       value
            indent = token.start_mark.column + conf['spaces']

        context['stack'].append(Parent(B_ENT, indent))

    elif isinstance(token, yaml.FlowSequenceStartToken):
        if next.start_mark.line == token.start_mark.line:
            #   - [a, b]
            indent = next.start_mark.column
        else:
            #   - [
            #   a, b
            # ]
            indent = context['cur_line_indent'] + conf['spaces']

        context['stack'].append(Parent(F_SEQ, indent,
                                       line_indent=context['cur_line_indent']))

    elif isinstance(token, yaml.KeyToken):
        indent = context['stack'][-1].indent

        context['stack'].append(Parent(KEY, indent))

        context['stack'][-1].explicit_key = is_explicit_key(token)

    elif isinstance(token, yaml.ValueToken):
        assert context['stack'][-1].type == KEY

        # Special cases:
        #     key: &anchor
        #       value
        # and:
        #     key: !!tag
        #       value
        if isinstance(next, (yaml.AnchorToken, yaml.TagToken)):
            if (next.start_mark.line == prev.start_mark.line and
                    next.start_mark.line < nextnext.start_mark.line):
                next = nextnext

        # Only if value is not empty
        if not isinstance(next, (yaml.BlockEndToken,
                                 yaml.FlowMappingEndToken,
                                 yaml.FlowSequenceEndToken,
                                 yaml.KeyToken)):
            if context['stack'][-1].explicit_key:
                #   ? k
                #   : value
                # or
                #   ? k
                #   :
                #     value
                indent = context['stack'][-1].indent + conf['spaces']
            elif next.start_mark.line == prev.start_mark.line:
                #   k: value
                indent = next.start_mark.column
            elif isinstance(next, (yaml.BlockSequenceStartToken,
                                   yaml.BlockEntryToken)):
                # NOTE: We add BlockEntryToken in the test above because
                # sometimes BlockSequenceStartToken are not issued. Try
                # yaml.scan()ning this:
                #     '- lib:\n'
                #     '  - var\n'
                if conf['indent-sequences'] is False:
                    indent = context['stack'][-1].indent
                elif conf['indent-sequences'] is True:
                    indent = context['stack'][-1].indent + conf['spaces']
                else:  # 'whatever'
                    if next.start_mark.column == context['stack'][-1].indent:
                        #   key:
                        #   - e1
                        #   - e2
                        indent = context['stack'][-1].indent
                    else:
                        #   key:
                        #     - e1
                        #     - e2
                        indent = context['stack'][-1].indent + conf['spaces']
            else:
                #   k:
                #     value
                indent = context['stack'][-1].indent + conf['spaces']

            context['stack'].append(Parent(VAL, indent))

    consumed_current_token = False
    while True:
        if (context['stack'][-1].type == F_SEQ and
                isinstance(token, yaml.FlowSequenceEndToken)):
            context['stack'].pop()

        elif (context['stack'][-1].type == F_MAP and
                isinstance(token, yaml.FlowMappingEndToken)):
            context['stack'].pop()

        elif (context['stack'][-1].type in (B_MAP, B_SEQ) and
                isinstance(token, yaml.BlockEndToken) and
                not context['stack'][-1].implicit_block_seq and
                not consumed_current_token):
            context['stack'].pop()
            consumed_current_token = True

        elif (context['stack'][-1].type == B_ENT and
                not isinstance(token, yaml.BlockEntryToken) and
                context['stack'][-2].implicit_block_seq and
                not isinstance(token, (yaml.AnchorToken, yaml.TagToken)) and
                not isinstance(next, yaml.BlockEntryToken)):
            context['stack'].pop()
            context['stack'].pop()

        elif (context['stack'][-1].type == B_ENT and
                isinstance(next, (yaml.BlockEntryToken, yaml.BlockEndToken))):
            context['stack'].pop()

        elif (context['stack'][-1].type == VAL and
                not isinstance(token, yaml.ValueToken) and
                not isinstance(token, (yaml.AnchorToken, yaml.TagToken))):
            assert context['stack'][-2].type == KEY
            context['stack'].pop()
            context['stack'].pop()

        elif (context['stack'][-1].type == KEY and
                isinstance(next, (yaml.BlockEndToken,
                                  yaml.FlowMappingEndToken,
                                  yaml.FlowSequenceEndToken,
                                  yaml.KeyToken))):
            # A key without a value: it's part of a set. Let's drop this key
            # and leave room for the next one.
            context['stack'].pop()

        else:
            break
