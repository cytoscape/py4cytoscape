# -*- coding: utf-8 -*-

""" Test functions in sandbox.py.
"""
from cytoolz.itertoolz import remove

"""License:
    Copyright 2020 The Cytoscape Consortium

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions
    of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import unittest
import time
from requests import HTTPError

from test_utils import *

_TEST_SANDBOX_NAME = 'test_sandbox'
_TEST_FILE = 'test file'
_ALTTEST_SANDBOX_NAME = '.test.sandbox'

class SandboxTests(unittest.TestCase):
    def setUp(self):
        # Close all browser windows if possible
        try:
            notebook_is_running(False)
            reset_default_sandbox()
        except:
            pass

    def tearDown(self):
        pass



    @print_entry_exit
    def test_sandbox_set_invalid(self):
        # Set invalid sandboxes (null, "", having a path, having '.', having '..', having absolute path
        self.assertRaises(HTTPError, sandbox_set, 'foo/bar')
        self.assertRaises(HTTPError, sandbox_set, '.')
        self.assertRaises(HTTPError, sandbox_set, '..')
        self.assertRaises(HTTPError, sandbox_set, '...')
        self.assertRaises(HTTPError, sandbox_set, '/windows/system32')

    @print_entry_exit
    def test_sandbox_set_remove_standalone(self):
        # Verify that setting an empty sandbox really creates one that it points to Cytoscape program directory
        sandbox = sandbox_set(None)
        sandbox1 = self._verify_empty_sandbox()
        self.assertEqual(sandbox, sandbox1)

        # Remove the null sandbox and verify the error
        self.assertRaises(CyError, sandbox_remove)

        # Set an actual sandbox, and verify it exists with copied samples and no other files
        sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        self._verify_sandbox_path(sandbox)
        self.assertEqual(len(os.listdir(sandbox)), 1)
        self.assertEqual(os.path.isdir(os.path.join(sandbox, 'sampleData')), True)

        # Remove the sandbox and verify it's gone
        self._verify_removed(_TEST_SANDBOX_NAME, True, sandbox)
        self._verify_empty_sandbox()

        # Remove the sandbox again and verify it didn't exist
        self._verify_removed(_TEST_SANDBOX_NAME, False, sandbox)
        self._verify_empty_sandbox()

        # Set a sandbox without samples and verify it exists but is empty
        sandbox = sandbox_set(_TEST_SANDBOX_NAME, copy_samples=False)
        self._verify_sandbox_path(sandbox)
        self.assertEqual(len(os.listdir(sandbox)), 0)

        # Add a single file to the sandbox, and then re-set it to make sure the file is still there, then try again
        # with copying samples in, too
        self._write_file(sandbox)
        self.assertEqual(len(os.listdir(sandbox)), 1)
        self.assertEqual(os.path.isfile(os.path.join(sandbox, _TEST_FILE)), True)

        new_sandbox = sandbox_set(_TEST_SANDBOX_NAME, copy_samples=False, reinitialize=False)
        self._verify_sandbox_path(new_sandbox)
        self.assertEqual(len(os.listdir(sandbox)), 1)
        self.assertEqual(os.path.isfile(os.path.join(sandbox, _TEST_FILE)), True)

        new_sandbox = sandbox_set(_TEST_SANDBOX_NAME, copy_samples=True, reinitialize=False)
        self._verify_sandbox_path(new_sandbox)
        self.assertEqual(len(os.listdir(sandbox)), 2)
        self.assertEqual(os.path.isfile(os.path.join(sandbox, _TEST_FILE)), True)
        self.assertEqual(os.path.isdir(os.path.join(sandbox, 'sampleData')), True)

        # Remove the sandbox and verify it's gone
        self._verify_removed(_TEST_SANDBOX_NAME, True, sandbox)
        self._verify_empty_sandbox()

        # Set a sandbox having a name containing '.', and then remove it
        new_sandbox = sandbox_set(_ALTTEST_SANDBOX_NAME)
        self._verify_sandbox_path(new_sandbox, _ALTTEST_SANDBOX_NAME)
        self._verify_removed(_ALTTEST_SANDBOX_NAME, True, new_sandbox)
        self._verify_empty_sandbox()


    @print_entry_exit
    def test_sandbox_set_remove_standalone_multiple(self):

        def check_sandbox_files(test_file, alt_file):
            self.assertEqual(os.path.isfile(os.path.join(test_sandbox, _TEST_FILE)), test_file)
            self.assertEqual(os.path.isdir(os.path.join(test_sandbox, 'sampleData')), True)
            self.assertEqual(os.path.isfile(os.path.join(alt_sandbox, _TEST_FILE)), alt_file)
            self.assertEqual(os.path.isdir(os.path.join(alt_sandbox, 'sampleData')), True)
            self.assertEqual(os.path.isfile(os.path.join(empty_sandbox, _TEST_FILE)), False)
            self.assertEqual(os.path.isdir(os.path.join(empty_sandbox, 'sampleData')), True)

        # Set two real sandboxes but revert back to the null sandbox ... both real sandboxes should remain intact
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        alt_sandbox = sandbox_set(_ALTTEST_SANDBOX_NAME)
        empty_sandbox = sandbox_set(None)
        self._verify_sandbox_path(test_sandbox, _TEST_SANDBOX_NAME)
        self._verify_sandbox_path(alt_sandbox, _ALTTEST_SANDBOX_NAME)
        self._verify_empty_sandbox()

        # Switch back to a real sandbox (with real content) and verify that it's current
        self._write_file(test_sandbox)
        test1_sandbox = sandbox_set(_TEST_SANDBOX_NAME, copy_samples=False, reinitialize=False)
        self.assertEqual(test_sandbox, test1_sandbox)
        check_sandbox_files(True, False)
        alt1_sandbox = sandbox_set(_ALTTEST_SANDBOX_NAME, copy_samples=False, reinitialize=False)
        self.assertEqual(alt_sandbox, alt1_sandbox)
        self._write_file(alt_sandbox)
        check_sandbox_files(True, True)
        empty1_sandbox = sandbox_set(None)
        self.assertEqual(empty_sandbox, empty1_sandbox)
        check_sandbox_files(True, True)

        # Set the current sandbox to a real one, then delete the other real one ... the current sandbox shouldn't change
        test1_sandbox = sandbox_set(_TEST_SANDBOX_NAME, copy_samples=False, reinitialize=False)
        self.assertEqual(test_sandbox, test1_sandbox)
        self._verify_removed(_ALTTEST_SANDBOX_NAME, True, alt_sandbox)
        test1_sandbox = self._verify_valid_sandbox()
        self.assertEqual(test_sandbox, test1_sandbox)

        # Verify that deleting the current sandbox makes the empty sandbox current
        self._verify_removed(_TEST_SANDBOX_NAME, True, test_sandbox)
        empty1_sandbox = self._verify_empty_sandbox()
        self.assertEqual(empty_sandbox, empty1_sandbox)

    @print_entry_exit
    def test_sandbox_set_remove_notebook(self):
        notebook_is_running(True) # Should cause default notebook to be created

        # Verify that setting an empty sandbox resolves to the pre-created sandbox
        default_sandbox = sandbox_set(None)
        default_sandbox1 = self._verify_preset_sandbox()
        self.assertEqual(default_sandbox, default_sandbox1)

        # Remove the default sandbox and verify that it's actually removed
        self._verify_removed(None, True, default_sandbox)
        self.assertFalse(os.path.exists(default_sandbox))

        # Verify that the slightest operation causes the default sandbox to be re-created
        default_sandbox1 = self._verify_preset_sandbox()

        # Verify that deleting it erases it. Verify that even deleting the sandbox causes it to be re-created before
        # it's then deleted ... and then verify that the slightest operation also causes it to be automatically re-created
        self._verify_removed(None, True, default_sandbox)
        self._verify_removed(None, True, default_sandbox)
        default_sandbox1 = self._verify_preset_sandbox()

        # Create a new sandbox and verify that it's not the default.
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        self._verify_sandbox_path(test_sandbox, _TEST_SANDBOX_NAME)
        self.assertNotEqual(default_sandbox, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox(), test_sandbox) # Verify that the new sandbox exists and it's the current sandbox

        # Verify that deleting the new sandbox causes the default sandbox to become current again ... and without messing up the default sandbox
        self._verify_removed(None, True, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox(), default_sandbox)

        # Create the new sandbox again and verify that it's not the default.
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        self._verify_sandbox_path(test_sandbox, _TEST_SANDBOX_NAME)
        self.assertNotEqual(default_sandbox, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox(),
                         test_sandbox)  # Verify that the new sandbox exists and it's the current sandbox

        # Verify that deleting the default sandbox leaves the new sandbox as the current sandbox
        self._verify_removed(PREDEFINED_SANDBOX_NAME, True, default_sandbox)
        self.assertEqual(self._verify_valid_sandbox(),
                         test_sandbox)  # Verify that the new sandbox exists and it's the current sandbox

        # Next ... verify that the default sandbox gets created once the new sandbox is deleted
        self._verify_removed(None, True, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox(), default_sandbox)
        self._write_file(default_sandbox)

        # With the default sandbox being current, verify that deleting the new sandbox again leaves the default as current
        self._verify_removed(_TEST_SANDBOX_NAME, False, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox(), default_sandbox)
        self.assertEqual(os.path.isfile(os.path.join(default_sandbox, _TEST_FILE)), True)

    def _verify_valid_sandbox(self):
        sandbox = sandbox_get_file_info('.')
        self.assertIsInstance(sandbox, dict)
        self.assertSetEqual(set(sandbox.keys()), {'filePath', 'modifiedTime', 'isFile'})
        self.assertNotEqual(sandbox['modifiedTime'], '')
        self.assertEqual(sandbox['isFile'], False)
        return sandbox['filePath']

    def _verify_empty_sandbox(self):
        empty_sandbox = self._verify_valid_sandbox()
        self.assertEqual(os.path.isfile(os.path.join(empty_sandbox, 'Cytoscape.vmoptions')), True)
        return empty_sandbox

    def _verify_preset_sandbox(self):
        sandbox = self._verify_valid_sandbox()
        self.assertEqual(len(os.listdir(sandbox)), 1)
        self.assertEqual(os.path.isdir(os.path.join(sandbox, 'sampleData')), True)
        return sandbox

    def _verify_removed(self, sandbox_name, existed, original_sandbox_path):
        removed_sandbox = sandbox_remove(sandbox_name)
        self.assertIsInstance(removed_sandbox, dict)
        self.assertSetEqual(set(removed_sandbox.keys()), {'sandboxPath', 'existed'})
        self.assertEqual(removed_sandbox['sandboxPath'], original_sandbox_path)
        self.assertEqual(removed_sandbox['existed'], existed)

    def _verify_sandbox_path(self, sandbox_path, sandbox_name=_TEST_SANDBOX_NAME):
        self.assertIsInstance(sandbox_path, str)
        test_sandbox_path = os.path.split(sandbox_path)
        filetransfer_path = os.path.split(test_sandbox_path[0])
        cyconfig_path = os.path.split(filetransfer_path[0])
        self.assertEqual(test_sandbox_path[1], sandbox_name)
        self.assertEqual(filetransfer_path[1], 'filetransfer')
        self.assertEqual(cyconfig_path[1], 'CytoscapeConfiguration')

    def _write_file(self, sandbox_name):
        with open(os.path.join(sandbox_name, _TEST_FILE), 'w') as file:
            file.write('This is a test')


if __name__ == '__main__':
    unittest.main()
