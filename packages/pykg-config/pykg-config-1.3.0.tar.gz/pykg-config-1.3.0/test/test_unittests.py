#!/usr/bin/env python

# Copyright (c) 2009-2012, Geoffrey Biggs
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Geoffrey Biggs nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# File: test_unittests.py
# Author: Geoffrey Biggs
# Part of pykg-config.

__version__ = "$Revision: $"
# $Source$

import os
import re
import subprocess
import unittest

from pykg_config import packagespeclist
from pykg_config import substitute
from pykg_config import dependency
from pykg_config import version


def call_process(args):
    env = os.environ
    env['PKG_CONFIG_PATH'] = '{0}:{1}'.format(os.getcwd(),
            env['PKG_CONFIG_PATH'])
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()
    output = (output[0].strip(), output[1].strip())
    return_code = process.returncode
    return output[0], output[1], return_code


class TestVersion(unittest.TestCase):
    def setUp(self):
        self.strings = ['2.3', '5.0-svn', '1.2.3.4.a.6', '15', '2.3.0',
                        '2.3.1', '2.3-a']
        self.parsed = [[2, 3], [5, 0, 'svn'], [1, 2, 3, 4, 'a', 6], [15],
                       [2, 3, 0], [2, 3, 1], [2, 3, 'a']]

    def test_constructor(self):
        for case, result in zip(self.strings, self.parsed):
            self.assertEqual(version.Version(case).comps, result)

    def test_comparisons(self):
        versions = []
        for verstring in self.strings:
            versions.append(version.Version(verstring))
        self.assert_(versions[0] < versions[1])
        self.assert_(versions[0] < versions[5])
        self.assert_(versions[0] < versions[6])
        self.assert_(versions[0] <= versions[0])
        self.assert_(versions[0] <= versions[1])
        self.assert_(versions[0] <= versions[4])
        self.assert_(versions[0] == versions[0])
        self.assert_(versions[0] == versions[4])
        self.assert_(versions[1] == versions[1])
        self.assert_(versions[0] != versions[1])
        self.assert_(versions[0] != versions[2])
        self.assert_(versions[0] != versions[3])
        self.assert_(versions[0] > versions[2])
        self.assert_(versions[0] >= versions[0])
        self.assert_(versions[0] >= versions[2])
        self.assert_(versions[0] >= versions[4])

        self.assertFalse(versions[0] < versions[2])
        self.assertFalse(versions[0] <= versions[2])
        self.assertFalse(versions[0] == versions[1])
        self.assertFalse(versions[0] == versions[2])
        self.assertFalse(versions[0] == versions[3])
        self.assertFalse(versions[0] != versions[4])
        self.assertFalse(versions[0] >= versions[1])
        self.assertFalse(versions[0] >= versions[3])
        self.assertFalse(versions[0] >= versions[5])
        self.assertFalse(versions[0] >= versions[6])
        self.assertFalse(versions[0] > versions[1])
        self.assertFalse(versions[0] > versions[3])

class TestPackage(unittest.TestCase):
    def test_parse_package_spec_list(self):
        parsed = packagespeclist.parse_package_spec_list('blag < 2.3, \
                blerg>=5-svn blork, bleck = 15')
        expected = [dependency.Dependency('blag', dependency.LESS_THAN,
                                          version.Version('2.3')),
                    dependency.Dependency('blerg', dependency.GREATER_THAN_EQUAL,
                                          version.Version('5-svn')),
                    dependency.Dependency('blork', dependency.ALWAYS_MATCH,
                                          version.Version()),
                    dependency.Dependency('bleck', dependency.EQUAL,
                                          version.Version('15'))]
        self.assertEqual(parsed, expected)


class TestSubstitutions(unittest.TestCase):
    def setUp(self):
        self.pykg_config_cmd = '../pykg-config.py'
        self.vars = {'blag1': 'not recursive',
                     'blag2': 'references ${blag1} variable',
                     'blag3': 'recursive with ${blag3}'}

    def test_escaping(self):
        value = 'a $${blag1} that should not be replaced'
        result = 'a ${blag1} that should not be replaced'
        self.assertEqual(substitute.substitute(value, self.vars), result)

    def test_substitute(self):
        value = 'stuff ${blag2} more stuff ${blag1} ${blag3}'
        result = 'stuff references not recursive variable more stuff not recursive recursive with ${blag3}'
        self.assertEqual(substitute.substitute(value, self.vars), result)

    def test_get_to_replace_re(self):
        self.assertEqual(substitute.get_to_replace_re('blag'),
                         re.compile ('(?<!\$)\$\{blag\}', re.U))

    def test_get_all_substitutions(self):
        nameful = '${lots} of ${names} ${reffed}.'
        self.assertEqual(substitute.get_all_substitutions(nameful),
                         ['lots', 'names', 'reffed'])

    def test_undefined_var(self):
        args = ['--cflags', 'global_var']
        stdout, stderr, ret_code = call_process([self.pykg_config_cmd] + args)
        self.assertEqual(ret_code, 1)

    def test_global_var(self):
        args = ['--cflags', 'global_var', '--define-variable=global_var=blurg']
        stdout, stderr, ret_code = call_process([self.pykg_config_cmd] + args)
        self.assertEqual(stdout, '-Iblurg')
        self.assertEqual(ret_code, 0)


class TestQuoteEscapes(unittest.TestCase):
    def setUp(self):
        self.pykg_config_cmd = '../pykg-config.py'

    def test_maintain_escaping(self):
        args = ['--cflags', 'unittests1']
        stdout, stderr, ret_code = call_process([self.pykg_config_cmd] + args)
        self.assertEqual(stdout, r'-DPATH=\"/opt/shaders/\"')
        self.assertEqual(ret_code, 0)



if __name__ == '__main__':
    unittest.main()


# vim: tw=79

