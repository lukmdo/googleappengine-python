#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests for devappserver2.update_checker."""


import unittest

import google
import mox

from google.appengine.tools import appcfg
from google.appengine.tools.devappserver2 import application_configuration
from google.appengine.tools.devappserver2 import update_checker


class GetUserAgentTest(unittest.TestCase):
  def test(self):
    self.assertRegexpMatches(update_checker._get_user_agent(),
                             r'devappserver2_py/\d+(\.\d+)* .* Python/.*')


class GetSourceNameTest(unittest.TestCase):
  def test(self):
    self.assertRegexpMatches(update_checker._get_source_name(),
                             r'Google-appcfg-\d+(\.\d+)*')


class CheckForUpdatesTest(unittest.TestCase):
  def setUp(self):
    self.mox = mox.Mox()
    self.update_check = self.mox.CreateMock(appcfg.UpdateCheck)
    self.config = self.mox.CreateMock(
        application_configuration.ApplicationConfiguration)
    self.mox.StubOutWithMock(appcfg, 'UpdateCheck')

  def tearDown(self):
    self.mox.UnsetStubs()

  def test_update_check_allowed(self):
    server1 = object()
    server2 = object()
    self.config.servers = [server1, server2]

    appcfg.UpdateCheck(mox.IgnoreArg(), server1).AndReturn(self.update_check)
    self.update_check.CheckSupportedVersion()
    self.update_check.AllowedToCheckForUpdates().AndReturn(True)
    self.update_check.CheckForUpdates()

    self.mox.ReplayAll()
    update_checker.check_for_updates(self.config)
    self.mox.VerifyAll()

  def test_update_check_forbidden(self):
    server1 = object()
    server2 = object()
    self.config.servers = [server1, server2]

    appcfg.UpdateCheck(mox.IgnoreArg(), server1).AndReturn(self.update_check)
    self.update_check.CheckSupportedVersion()
    self.update_check.AllowedToCheckForUpdates().AndReturn(False)

    self.mox.ReplayAll()
    update_checker.check_for_updates(self.config)
    self.mox.VerifyAll()

  def test_update_check_no_servers(self):
    self.config.servers = []

    self.mox.ReplayAll()
    update_checker.check_for_updates(self.config)
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()
