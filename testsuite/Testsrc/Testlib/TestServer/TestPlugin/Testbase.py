import os
import sys
import logging
from mock import Mock, MagicMock, patch
from Bcfg2.Server.Plugin.base import *

# add all parent testsuite directories to sys.path to allow (most)
# relative imports in python 2.4
path = os.path.dirname(__file__)
while path != '/':
    if os.path.basename(path).lower().startswith("test"):
        sys.path.append(path)
    if os.path.basename(path) == "testsuite":
        break
    path = os.path.dirname(path)
from common import *


class TestDebuggable(Bcfg2TestCase):
    test_obj = Debuggable

    def get_obj(self):
        return self.test_obj()

    def test__init(self):
        d = self.get_obj()
        self.assertIsInstance(d.logger, logging.Logger)
        self.assertFalse(d.debug_flag)

    def test_set_debug(self):
        d = self.get_obj()
        d.debug_log = Mock()
        self.assertEqual(True, d.set_debug(True))
        self.assertEqual(d.debug_flag, True)
        self.assertTrue(d.debug_log.called)

        d.debug_log.reset_mock()

        self.assertEqual(False, d.set_debug(False))
        self.assertEqual(d.debug_flag, False)
        self.assertTrue(d.debug_log.called)

    def test_toggle_debug(self):
        d = self.get_obj()
        d.set_debug = Mock()
        orig = d.debug_flag
        self.assertEqual(d.toggle_debug(),
                         d.set_debug.return_value)
        d.set_debug.assert_called_with(not orig)

    def test_debug_log(self):
        d = self.get_obj()
        d.logger = Mock()
        d.debug_flag = False
        d.debug_log("test")
        self.assertFalse(d.logger.error.called)

        d.logger.reset_mock()
        d.debug_log("test", flag=True)
        self.assertTrue(d.logger.error.called)

        d.logger.reset_mock()
        d.debug_flag = True
        d.debug_log("test")
        self.assertTrue(d.logger.error.called)


class TestPlugin(TestDebuggable):
    test_obj = Plugin

    def get_obj(self, core=None):
        if core is None:
            core = Mock()
            core.setup = MagicMock()
        return self.test_obj(core, datastore)

    def test__init(self):
        core = Mock()
        core.setup = MagicMock()
        p = self.get_obj(core=core)
        self.assertEqual(p.data, os.path.join(datastore, p.name))
        self.assertEqual(p.core, core)

    @patch("os.makedirs")
    def test_init_repo(self, mock_makedirs):
        self.test_obj.init_repo(datastore)
        mock_makedirs.assert_called_with(os.path.join(datastore,
                                                      self.test_obj.name))
