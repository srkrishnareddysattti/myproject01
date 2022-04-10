#!/usr/bin/env python
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

from __future__ import print_function
import os.path
import sys

import argparse

from yamllint import APP_DESCRIPTION, APP_NAME, APP_VERSION
from yamllint.config import YamlLintConfig, YamlLintConfigError
from yamllint import linter


def find_files_recursively(items):
    for item in items:
        if os.path.isdir(item):
            for root, dirnames, filenames in os.walk(item):
                for filename in [f for f in filenames
                                 if f.endswith(('.yml', '.yaml'))]:
                    yield os.path.join(root, filename)
        else:
            yield item


class Format(object):
    @staticmethod
    def parsable(problem, filename):
        return ('%(file)s:%(line)s:%(column)s: [%(level)s] %(message)s' %
                {'file': filename,
                 'line': problem.line,
                 'column': problem.column,
                 'level': problem.level,
                 'message': problem.message})

    @staticmethod
    def standard(problem, filename):
        line = '  \033[2m%d:%d\033[0m' % (problem.line, problem.column)
        line += max(20 - len(line), 0) * ' '
        if problem.level == 'warning':
            line += '\033[33m%s\033[0m' % problem.level
        else:
            line += '\033[31m%s\033[0m' % problem.level
        line += max(38 - len(line), 0) * ' '
        line += problem.desc
        if problem.rule:
            line += '  \033[2m(%s)\033[0m' % problem.rule
        return line


def run(argv=None):
    parser = argparse.ArgumentParser(prog=APP_NAME,
                                     description=APP_DESCRIPTION)
    parser.add_argument('files', metavar='FILE_OR_DIR', nargs='+',
                        help='files to check')
    parser.add_argument('-c', '--config', dest='config_file', action='store',
                        help='path to a custom configuration')
    parser.add_argument('-f', '--format',
                        choices=('parsable', 'standard'), default='standard',
                        help='format for parsing output')
    parser.add_argument('-v', '--version', action='version',
                        version='%s %s' % (APP_NAME, APP_VERSION))

    # TODO: read from stdin when no filename?

    args = parser.parse_args(argv)

    try:
        if args.config_file is not None:
            conf = YamlLintConfig(file=args.config_file)
        elif os.path.isfile('.yamllint'):
            conf = YamlLintConfig(file='.yamllint')
        else:
            conf = YamlLintConfig('extends: default')
    except YamlLintConfigError as e:
        print(e, file=sys.stderr)
        sys.exit(-1)

    return_code = 0

    for file in find_files_recursively(args.files):
        try:
            first = True
            with open(file) as f:
                for problem in linter.run(f, conf):
                    if args.format == 'parsable':
                        print(Format.parsable(problem, file))
                    else:
                        if first:
                            print('\033[4m%s\033[0m' % file)
                            first = False

                        print(Format.standard(problem, file))

                    if return_code == 0 and problem.level == 'error':
                        return_code = 1

            if not first and args.format != 'parsable':
                print('')
        except EnvironmentError as e:
            print(e)
            return_code = -1

    sys.exit(return_code)
