# -*- coding: utf-8 -*-

""" Test functions in sandbox.py.
"""

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

    _notebook_was_running = None

    def setUp(self):
        # Close all browser windows if possible
        global _notebook_was_running
        try:
            _notebook_was_running = set_notebook_is_running(False)
            reset_default_sandbox()
        except:
            pass

    def tearDown(self):
        reset_default_sandbox()
        set_notebook_is_running(_notebook_was_running)

    @print_entry_exit
    def test_sandbox_set_invalid(self):
        # Set invalid sandboxes (null, "", having a path, having '.', having '..', having absolute path
        self.assertRaises(CyError, sandbox_set, 'foo/bar')
        self.assertRaises(CyError, sandbox_set, '.')
        self.assertRaises(CyError, sandbox_set, '..')
        self.assertRaises(CyError, sandbox_set, '...')
        self.assertRaises(CyError, sandbox_set, '../..')
        self.assertRaises(CyError, sandbox_set, '/windows/system32')

    @print_entry_exit
    def test_sandbox_set_remove_standalone(self):
        # This tests that common/casual set/remove options on sandboxes work when running standalone Python

        # Verify that setting an empty sandbox really creates one that points to Cytoscape program directory
        sandbox = sandbox_set(None)
        sandbox1 = self._verify_sandbox_is_native_filesystem()
        self.assertEqual(sandbox, sandbox1)

        # Remove the null sandbox and verify the error
        self.assertRaises(CyError, sandbox_remove)

        # Set an actual sandbox, and verify it exists with copied samples and no other files
        sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        self._verify_sandbox_path(sandbox)
        self.assertEqual(len(os.listdir(sandbox)), 1)
        self.assertEqual(os.path.isdir(os.path.join(sandbox, 'sampleData')), True)

        # Remove the sandbox and verify it's gone
        self._remove_sandbox_and_verify(_TEST_SANDBOX_NAME, True, sandbox)
        self._verify_sandbox_is_native_filesystem()

        # Remove the sandbox again and verify it didn't exist
        self._remove_sandbox_and_verify(_TEST_SANDBOX_NAME, False, sandbox)
        self._verify_sandbox_is_native_filesystem()

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
        self._remove_sandbox_and_verify(_TEST_SANDBOX_NAME, True, sandbox)
        self._verify_sandbox_is_native_filesystem()

        # Set a sandbox having a name containing '.', and then remove it
        new_sandbox = sandbox_set(_ALTTEST_SANDBOX_NAME)
        self._verify_sandbox_path(new_sandbox, _ALTTEST_SANDBOX_NAME)
        self._remove_sandbox_and_verify(_ALTTEST_SANDBOX_NAME, True, new_sandbox)
        self._verify_sandbox_is_native_filesystem()


    @print_entry_exit
    def test_sandbox_set_remove_standalone_multiple(self):
        # This tests that multiple sandboxes are managed properly when running Python standalone. The hardest part of
        # this is to make sure that when the current sandbox is deleted, we fall back to the native Cytoscape file system.

        def check_sandbox_files(test_file, alt_file):
            self.assertEqual(os.path.isfile(os.path.join(test_sandbox, _TEST_FILE)), test_file)
            self.assertEqual(os.path.isdir(os.path.join(test_sandbox, 'sampleData')), True)
            self.assertEqual(os.path.isfile(os.path.join(alt_sandbox, _TEST_FILE)), alt_file)
            self.assertEqual(os.path.isdir(os.path.join(alt_sandbox, 'sampleData')), True)
            self.assertEqual(os.path.isfile(os.path.join(empty_sandbox, _TEST_FILE)), False)
            self.assertEqual(os.path.isdir(os.path.join(empty_sandbox, 'sampleData')), False)

        # Set two real sandboxes but revert back to the null sandbox ... both real sandboxes should remain intact
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        alt_sandbox = sandbox_set(_ALTTEST_SANDBOX_NAME)
        empty_sandbox = sandbox_set(None)
        self._verify_sandbox_path(test_sandbox, _TEST_SANDBOX_NAME)
        self._verify_sandbox_path(alt_sandbox, _ALTTEST_SANDBOX_NAME)
        self._verify_sandbox_is_native_filesystem()

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
        self._remove_sandbox_and_verify(_ALTTEST_SANDBOX_NAME, True, alt_sandbox)
        test1_sandbox = self._verify_valid_sandbox_file()
        self.assertEqual(test_sandbox, test1_sandbox)

        # Verify that deleting the current sandbox makes the empty sandbox current
        self._remove_sandbox_and_verify(_TEST_SANDBOX_NAME, True, test_sandbox)
        empty1_sandbox = self._verify_sandbox_is_native_filesystem()
        self.assertEqual(empty_sandbox, empty1_sandbox)

    @print_entry_exit
    def test_sandbox_set_remove_notebook(self):
        # This tests that the default sandbox is created when in a notebook or remote execution. We make sure that
        # if the current sandbox gets deleted, we fall back to the default sandbox. And we make sure that if the
        # default sandbox is deleted, we re-create it before trying to use it.

        set_notebook_is_running(True) # Should cause default notebook to be created

        # Verify that setting an empty sandbox resolves to the pre-created sandbox
        default_sandbox = sandbox_set(None)
        default_sandbox1 = self._verify_current_sandbox_is_preset()
        self.assertEqual(default_sandbox, default_sandbox1)

        # Remove the default sandbox and verify that it's actually removed
        self._remove_sandbox_and_verify(None, True, default_sandbox)
        self.assertFalse(os.path.exists(default_sandbox))

        # Verify that the slightest operation causes the default sandbox to be re-created ... in this case, a get_file_info
        default_sandbox1 = self._verify_current_sandbox_is_preset()

        # Verify that deleting it erases it. Verify that even deleting the sandbox causes it to be re-created before
        # it's then deleted ... and then verify that the slightest operation also causes it to be automatically re-created
        self._remove_sandbox_and_verify(None, True, default_sandbox)
        self.assertFalse(os.path.exists(default_sandbox))
        self._remove_sandbox_and_verify(None, True, default_sandbox)
        self.assertFalse(os.path.exists(default_sandbox))
        default_sandbox1 = self._verify_current_sandbox_is_preset() # side effect of looking: create default sandbox first

        # Create a new sandbox and verify that it's not the default.
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        self._verify_sandbox_path(test_sandbox, _TEST_SANDBOX_NAME)
        self.assertNotEqual(default_sandbox, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox_file(), test_sandbox) # Verify that the new sandbox exists and it's the current sandbox

        # Verify that deleting the new sandbox causes the default sandbox to become current again ... and without messing up the default sandbox
        self._remove_sandbox_and_verify(None, True, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox_file(), default_sandbox)

        # Create the new sandbox again and verify that it's not the default.
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        self._verify_sandbox_path(test_sandbox, _TEST_SANDBOX_NAME)
        self.assertNotEqual(default_sandbox, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox_file(),
                         test_sandbox)  # Verify that the new sandbox exists and it's the current sandbox

        # Verify that deleting the default sandbox leaves the new sandbox as the current sandbox
        self._remove_sandbox_and_verify(PREDEFINED_SANDBOX_NAME, True, default_sandbox)
        self.assertEqual(self._verify_valid_sandbox_file(),
                         test_sandbox)  # Verify that the new sandbox exists and it's the current sandbox

        # Next ... verify that the default sandbox gets created once the new sandbox is deleted
        self._remove_sandbox_and_verify(None, True, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox_file(), default_sandbox)
        self._write_file(default_sandbox)

        # With the default sandbox being current, verify that deleting the new sandbox again leaves the default as current
        self._remove_sandbox_and_verify(_TEST_SANDBOX_NAME, False, test_sandbox)
        self.assertEqual(self._verify_valid_sandbox_file(), default_sandbox)
        self.assertEqual(os.path.isfile(os.path.join(default_sandbox, _TEST_FILE)), True)

    @print_entry_exit
    def test_sandbox_file_info_standalone(self):
        # Verify that the Cytoscape install directory is returned when asking for '.' during standalone Python execution
        empty_sandbox = self._verify_sandbox_is_native_filesystem()

        # Verify that a non-existent file name returns an empty modifiedTime
        no_such_file = self._verify_missing_sandbox_file('complete garbage name')

        # Verify that a non-existent directory name returns an empty modifiedTime
        no_such_file = self._verify_missing_sandbox_file('garbage/')

        # Verify that an existing directory returns a modifiedTime and valid info
        dir_file = self._verify_valid_sandbox_file(file_name='data/')

        # Verify that a sandbox can have files in subdirectories
        gal_filtered_file = self._verify_valid_sandbox_file(file_name='data/Yeast Perturbation.cys', is_file=True)

        # Verify that a file outside of the Cytoscape install directory (i.e., anywhere) is allowed (... this isn't
        # allowed in a strict sandboxing mode like notebooks and remote execution gets)
        parent_dir = self._verify_missing_sandbox_file('../../fooled')
        root_dir = self._verify_valid_sandbox_file(file_name='/')

        # Verify that a file can be found in a named sandbox, including using all forms of the "current sandbox" name
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        gal_filtered_file = self._verify_valid_sandbox_file(sandbox_name=_TEST_SANDBOX_NAME, file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)
        self.assertTrue(gal_filtered_file.startswith(test_sandbox))
        gal_filtered_file = self._verify_valid_sandbox_file(sandbox_name=None, file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)
        self.assertTrue(gal_filtered_file.startswith(test_sandbox))
        gal_filtered_file = self._verify_valid_sandbox_file(sandbox_name="   ", file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)
        self.assertTrue(gal_filtered_file.startswith(test_sandbox))

        # Verify that null file names always fail
        self.assertRaises(CyError, sandbox_get_file_info, file_name=None)
        self.assertRaises(CyError, sandbox_get_file_info, file_name='')
        self.assertRaises(CyError, sandbox_get_file_info, file_name='  ')

    @print_entry_exit
    def test_sandbox_file_info_notebook(self):
        set_notebook_is_running(True) # Should cause default notebook to be created

        # Verify that the Cytoscape install directory is returned when asking for '.' during standalone Python execution
        default_sandbox = self._verify_valid_sandbox_file()
        self._verify_sandbox_path(default_sandbox, sandbox_name=PREDEFINED_SANDBOX_NAME)

        # Verify that a non-existent file name returns an empty modifiedTime
        no_such_file = self._verify_missing_sandbox_file('complete garbage name')

        # Verify that a non-existent directory name returns an empty modifiedTime
        no_such_file = self._verify_missing_sandbox_file('garbage/')

        # Verify that an existing directory returns a modifiedTime and valid info
        dir_file = self._verify_valid_sandbox_file(file_name='sampleData/sessions/')

        # Verify that a sandbox can have files in subdirectories
        gal_filtered_file = self._verify_valid_sandbox_file(file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)

        # Verify that a file outside of the Cytoscape install directory (i.e., anywhere) is disllowed (... this is
        # allowed in a standalone Python mode)
        self.assertRaises(CyError, sandbox_get_file_info, file_name='../../fooled')

        # Verify that a file can be found in a named sandbox, including using all forms of the "current sandbox" name
        test_sandbox = sandbox_set(_TEST_SANDBOX_NAME)
        gal_filtered_file = self._verify_valid_sandbox_file(sandbox_name=_TEST_SANDBOX_NAME, file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)
        self.assertTrue(gal_filtered_file.startswith(test_sandbox))
        gal_filtered_file = self._verify_valid_sandbox_file(sandbox_name=None, file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)
        self.assertTrue(gal_filtered_file.startswith(test_sandbox))
        gal_filtered_file = self._verify_valid_sandbox_file(sandbox_name="   ", file_name='sampleData/sessions/Yeast Perturbation.cys', is_file=True)
        self.assertTrue(gal_filtered_file.startswith(test_sandbox))

        # Verify that null file names always fail
        self.assertRaises(CyError, sandbox_get_file_info, file_name=None)
        self.assertRaises(CyError, sandbox_get_file_info, file_name='')
        self.assertRaises(CyError, sandbox_get_file_info, file_name='  ')

    @print_entry_exit
    def test_sandbox_from(self):
        _FROM_FILE_NAME = 'data/Styles Demo.cys'
        _FROM_FILE_BYTES = 2548166
        _FROM_FILE_NAME_SANDBOX = 'sampleData/sessions/Styles Demo.cys'
        _ALT_FROM_FILE_NAME = 'data/Import & Save.cys'
        _ALT_FROM_FILE_BYTES = 2410184
        _ALT_FROM_FILE_NAME_SANDBOX = 'sampleData/sessions/Import & Save.cys'
        _LOCAL_DEST_FILE_NAME = _TEST_FILE

        def check_from_result(res, sandbox_path, expected_length, expected_file_name=_LOCAL_DEST_FILE_NAME):
            self.assertIsInstance(res, dict)
            self.assertSetEqual(set(res.keys()), {'filePath', 'modifiedTime', 'fileByteCount'})
            self.assertNotEqual(res['modifiedTime'], '')
            self.assertEqual(res['fileByteCount'], expected_length)
            self.assertTrue(res['filePath'].startswith(sandbox_path))
            self.assertEqual(os.path.isfile(expected_file_name), True)
            self.assertEqual(os.path.getsize(expected_file_name), expected_length)

        def check_from_sandbox(sandbox_path, from_file_name = _FROM_FILE_NAME, alt_from_file_name = _ALT_FROM_FILE_NAME):
            # Remove local file if it exists
            if os.path.exists(_LOCAL_DEST_FILE_NAME): os.remove(_LOCAL_DEST_FILE_NAME)

            # Verify that a file can be transferred from the sandbox
            res = sandbox_get_from(from_file_name, _LOCAL_DEST_FILE_NAME)
            check_from_result(res, sandbox_path, _FROM_FILE_BYTES)

            # Verify that the file can't be overwritten if we don't want it to be
            self.assertRaises(CyError, sandbox_get_from, source_file=from_file_name, dest_file=_LOCAL_DEST_FILE_NAME,
                              overwrite=False)
            self.assertEqual(os.path.isfile(_TEST_FILE), True)
            self.assertEqual(os.path.getsize(_TEST_FILE), _FROM_FILE_BYTES)

            # Verify that a different file can overwrite it if we allow it
            res = sandbox_get_from(alt_from_file_name, _TEST_FILE)
            check_from_result(res, sandbox_path, _ALT_FROM_FILE_BYTES)

            # Verify that if a destination file isn't provided, it defaults to the name of the source file
            res = sandbox_get_from(alt_from_file_name)
            head, tail = os.path.split(alt_from_file_name)
            check_from_result(res, sandbox_path, _ALT_FROM_FILE_BYTES, expected_file_name=tail)
            res = sandbox_get_from(alt_from_file_name, '  ', overwrite=True)
            check_from_result(res, sandbox_path, _ALT_FROM_FILE_BYTES, expected_file_name=tail)
            os.remove(tail)

            # Verify that trying to get a non-existent file files
            self.assertRaises(CyError, sandbox_get_from, 'totally bogus', dest_file=_LOCAL_DEST_FILE_NAME)
            self.assertRaises(CyError, sandbox_get_from, None, dest_file=_LOCAL_DEST_FILE_NAME)
            self.assertRaises(CyError, sandbox_get_from, None)
            self.assertRaises(CyError, sandbox_get_from, '  ', dest_file=_LOCAL_DEST_FILE_NAME)
            self.assertRaises(CyError, sandbox_get_from, _FROM_FILE_NAME, dest_file=_LOCAL_DEST_FILE_NAME,
                              sandbox_name='totally bogus')
            self.assertRaises(CyError, sandbox_get_from, _FROM_FILE_NAME, dest_file=_LOCAL_DEST_FILE_NAME,
                              sandbox_name='/totally/bogus/sandbox')

        # Check fetching from empty sandbox (Cytoscape install directory)
        empty_sandbox_path = self._verify_sandbox_is_native_filesystem()
        check_from_sandbox(empty_sandbox_path)

        # Check fetching from default sandbox (when Notebook is running)
        reset_default_sandbox()
        set_notebook_is_running(True) # Should cause default notebook to be created
        default_sandbox_path = sandbox_set(None)
        check_from_sandbox(default_sandbox_path, from_file_name=_FROM_FILE_NAME_SANDBOX, alt_from_file_name=_ALT_FROM_FILE_NAME_SANDBOX)

    @print_entry_exit
    def test_sandbox_to_remove(self):
        _FROM_FILE_NAME = 'data/Multiple Collections.cys'
        _FROM_FILE_BYTES = 4445369
        _ALT_FROM_FILE_NAME = 'data/Affinity Purification.cys'
        _ALT_FROM_FILE_BYTES = 1054245
        _NESTED_DIR = '1/2/3/'
        _ESCAPE_DIR = '1/../../../2/3/'

        def check_to_result(res, sandbox_path, sandbox_name, file_name, expected_length):
            self.assertIsInstance(res, dict)
            self.assertSetEqual(set(res.keys()), {'filePath'})
            self.assertTrue(res['filePath'].startswith(sandbox_path))
            self._verify_valid_sandbox_file(sandbox_name=sandbox_name, file_name=file_name, is_file=True)
            self.assertEqual(os.path.getsize(res['filePath']), expected_length)

        def check_remove_file(res, sandbox_path, existed):
            self.assertIsInstance(res, dict)
            self.assertSetEqual(set(res.keys()), {'filePath', 'existed'})
            self.assertEqual(res['existed'], existed)
            self.assertTrue(res['filePath'].startswith(sandbox_path))

        def check_to_sandbox(sandbox_path, sandbox_name):
            # Get rid of the sandbox test file if it already exists ... and verify empty remove either way
            res = sandbox_get_file_info(_TEST_FILE)
            if res['modifiedTime']:
                check_remove_file(sandbox_remove_file(_TEST_FILE), sandbox_path, True)
            check_remove_file(sandbox_remove_file(_TEST_FILE), sandbox_path, False)

            # Verify that a file can be transferred to the sandbox
            res = sandbox_send_to(_FROM_FILE_NAME, _TEST_FILE)
            check_to_result(res, sandbox_path, sandbox_name, _TEST_FILE, _FROM_FILE_BYTES)

            # Verify that the file can't be overwritten if we don't want it to be
            self.assertRaises(CyError, sandbox_send_to, source_file=_ALT_FROM_FILE_NAME, dest_file=_TEST_FILE,
                              overwrite=False)
            check_to_result(res, sandbox_path, sandbox_name, _TEST_FILE, _FROM_FILE_BYTES)

            # Verify that a different file can overwrite it if we allow it
            res = sandbox_send_to(_ALT_FROM_FILE_NAME, _TEST_FILE)
            check_to_result(res, sandbox_path, sandbox_name, _TEST_FILE, _ALT_FROM_FILE_BYTES)

            # Verify that removing a file actually removes it, and removing twice is properly detected
            res = sandbox_remove_file(file_name=_TEST_FILE, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, True)
            res = sandbox_remove_file(file_name=_TEST_FILE, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, False)

            # Verify that a file can be written to a directory nested in the sandbox, with path to be created during write
            nested_test_file = _NESTED_DIR + _TEST_FILE
            res = sandbox_send_to(_FROM_FILE_NAME, nested_test_file)
            check_to_result(res, sandbox_path, sandbox_name, nested_test_file, _FROM_FILE_BYTES)
            res = sandbox_remove_file(file_name=nested_test_file, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, True)

            # Verify that if a destination file isn't provided, it defaults to the name of the source file
            res = sandbox_send_to(_FROM_FILE_NAME)
            head, tail = os.path.split(_FROM_FILE_NAME)
            check_to_result(res, sandbox_path, sandbox_name, tail, _FROM_FILE_BYTES)
            res = sandbox_remove_file(file_name=tail, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, True)

            # Verify that if a destination file is blank, it defaults to the name of the source file
            res = sandbox_send_to(_FROM_FILE_NAME, dest_file='  ')
            head, tail = os.path.split(_FROM_FILE_NAME)
            check_to_result(res, sandbox_path, sandbox_name, tail, _FROM_FILE_BYTES)
            res = sandbox_remove_file(file_name=tail, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, True)

            # Verify that trying to send a non-existent file fails
            self.assertRaises(CyError, sandbox_send_to, 'totally bogus', dest_file=_TEST_FILE)
            self.assertRaises(CyError, sandbox_send_to, None, dest_file=_TEST_FILE)
            self.assertRaises(CyError, sandbox_send_to, None)
            self.assertRaises(CyError, sandbox_send_to, '  ', dest_file=_TEST_FILE)
            self.assertRaises(CyError, sandbox_send_to, _FROM_FILE_NAME, dest_file=_TEST_FILE,
                              sandbox_name='totally bogus')
            self.assertRaises(CyError, sandbox_send_to, _FROM_FILE_NAME, dest_file=_TEST_FILE,
                              sandbox_name='/totally/bogus/sandbox')
            self.assertRaises(CyError, sandbox_send_to, _FROM_FILE_NAME, dest_file=_ESCAPE_DIR + _TEST_FILE)
            self.assertRaises(CyError, sandbox_remove_file, file_name=None)
            self.assertRaises(CyError, sandbox_remove_file, file_name=_TEST_FILE, sandbox_name='totally bogus')
            self.assertRaises(CyError, sandbox_remove_file, file_name=_TEST_FILE, sandbox_name='/totally/bogus/sandbox')
            self.assertRaises(CyError, sandbox_remove_file, file_name=_ESCAPE_DIR + _TEST_FILE)

        # Check sending to empty sandbox (Cytoscape install directory)
        default_sandbox_path = sandbox_set(PREDEFINED_SANDBOX_NAME)
        self._verify_current_sandbox_is_preset()
        check_to_sandbox(default_sandbox_path, PREDEFINED_SANDBOX_NAME)

        # Check fetching from default sandbox (when Notebook is running)
        reset_default_sandbox()
        set_notebook_is_running(True) # Should cause default notebook to be created
        default_sandbox_path = sandbox_set(None)
        check_to_sandbox(default_sandbox_path, PREDEFINED_SANDBOX_NAME)

    @print_entry_exit
    def test_sandbox_url_to_remove(self):
        _FROM_URL = 'https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0'
        _FROM_URL_BYTES = 5536880
        _ALT_FROM_URL = 'https://www.dropbox.com/s/8wc8o897tsxewt1/BIOGRID-ORGANISM-Saccharomyces_cerevisiae-3.2.105.mitab?dl=0'
        _ALT_FROM_URL_BYTES = 166981992
        _NESTED_DIR = '1/2/3/'
        _ESCAPE_DIR = '1/../../../2/3/'

        def check_url_to_result(res, sandbox_path, sandbox_name, file_name, expected_length):
            self.assertIsInstance(res, dict)
            self.assertSetEqual(set(res.keys()), {'filePath', 'fileByteCount'})
            self.assertTrue(res['filePath'].startswith(sandbox_path))
            self._verify_valid_sandbox_file(sandbox_name=sandbox_name, file_name=file_name, is_file=True)
            self.assertEqual(os.path.getsize(res['filePath']), expected_length)

        def check_remove_file(res, sandbox_path, existed):
            self.assertIsInstance(res, dict)
            self.assertSetEqual(set(res.keys()), {'filePath', 'existed'})
            self.assertEqual(res['existed'], existed)
            self.assertTrue(res['filePath'].startswith(sandbox_path))

        def check_url_to_sandbox(sandbox_path, sandbox_name):
            # Get rid of the sandbox test file if it already exists ... and verify empty remove either way
            res = sandbox_get_file_info(_TEST_FILE)
            if res['modifiedTime']:
                check_remove_file(sandbox_remove_file(_TEST_FILE), sandbox_path, True)
            check_remove_file(sandbox_remove_file(_TEST_FILE), sandbox_path, False)

            # Verify that a file can be transferred to the sandbox
            res = sandbox_url_to(_FROM_URL, _TEST_FILE)
            check_url_to_result(res, sandbox_path, sandbox_name, _TEST_FILE, _FROM_URL_BYTES)

            # Verify that the file can't be overwritten if we don't want it to be
            self.assertRaises(CyError, sandbox_url_to, source_url=_ALT_FROM_URL, dest_file=_TEST_FILE,
                              overwrite=False)
            check_url_to_result(res, sandbox_path, sandbox_name, _TEST_FILE, _FROM_URL_BYTES)

            # Verify that a different file can overwrite it if we allow it
            res = sandbox_url_to(_ALT_FROM_URL, _TEST_FILE)
            check_url_to_result(res, sandbox_path, sandbox_name, _TEST_FILE, _ALT_FROM_URL_BYTES)

            # Verify that removing a file actually removes it, and removing twice is properly detected
            res = sandbox_remove_file(file_name=_TEST_FILE, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, True)
            res = sandbox_remove_file(file_name=_TEST_FILE, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, False)

            # Verify that a file can be written to a directory nested in the sandbox, with path to be created during write
            nested_test_file = _NESTED_DIR + _TEST_FILE
            res = sandbox_url_to(_FROM_URL, nested_test_file)
            check_url_to_result(res, sandbox_path, sandbox_name, nested_test_file, _FROM_URL_BYTES)
            res = sandbox_remove_file(file_name=nested_test_file, sandbox_name=sandbox_name)
            check_remove_file(res, sandbox_path, True)

            # Verify that trying to send a non-existent file fails
            self.assertRaises(Exception, sandbox_url_to, source_url=_FROM_URL)
            self.assertRaises(CyError, sandbox_url_to, source_url='totally bogus', dest_file=_TEST_FILE)
            self.assertRaises(CyError, sandbox_url_to, source_url=None, dest_file=_TEST_FILE)
            self.assertRaises(CyError, sandbox_url_to, source_url='  ', dest_file=_TEST_FILE)
            self.assertRaises(CyError, sandbox_url_to, source_url=_FROM_URL, dest_file=_TEST_FILE,
                              sandbox_name='totally bogus')
            self.assertRaises(CyError, sandbox_url_to, source_url=_FROM_URL, dest_file=_TEST_FILE,
                              sandbox_name='/totally/bogus/sandbox')
            self.assertRaises(CyError, sandbox_url_to, source_url=_FROM_URL, dest_file=_ESCAPE_DIR + _TEST_FILE)
            self.assertRaises(CyError, sandbox_remove_file, file_name=None)
            self.assertRaises(CyError, sandbox_remove_file, file_name=_TEST_FILE, sandbox_name='totally bogus')
            self.assertRaises(CyError, sandbox_remove_file, file_name=_TEST_FILE, sandbox_name='/totally/bogus/sandbox')
            self.assertRaises(CyError, sandbox_remove_file, file_name=_ESCAPE_DIR + _TEST_FILE)

        # Check sending to empty sandbox (Cytoscape install directory)
        default_sandbox_path = sandbox_set(PREDEFINED_SANDBOX_NAME)
        self._verify_current_sandbox_is_preset()
        check_url_to_sandbox(default_sandbox_path, PREDEFINED_SANDBOX_NAME)

        # Check fetching from default sandbox (when Notebook is running)
        reset_default_sandbox()
        set_notebook_is_running(True) # Should cause default notebook to be created
        default_sandbox_path = sandbox_set(None)
        check_url_to_sandbox(default_sandbox_path, PREDEFINED_SANDBOX_NAME)



    def _verify_missing_sandbox_file(self, file_name='.'):
        # Verify that a file in a sandbox is not present
        sandbox = sandbox_get_file_info(file_name)
        self.assertIsInstance(sandbox, dict)
        self.assertSetEqual(set(sandbox.keys()), {'filePath', 'modifiedTime', 'isFile'})
        self.assertEqual(sandbox['modifiedTime'], '')
        self.assertEqual(sandbox['isFile'], False)
        return sandbox['filePath']

    def _verify_valid_sandbox_file(self, sandbox_name=None, file_name='.', is_file=False):
        # Verify that a particular file in a sandbox is present, and is either a file or a directory
        sandbox = sandbox_get_file_info(sandbox_name=sandbox_name, file_name=file_name)
        self.assertIsInstance(sandbox, dict)
        self.assertSetEqual(set(sandbox.keys()), {'filePath', 'modifiedTime', 'isFile'})
        self.assertNotEqual(sandbox['modifiedTime'], '')
        self.assertEqual(sandbox['isFile'], is_file)
        return sandbox['filePath']

    def _verify_sandbox_is_native_filesystem(self):
        # Verify that the current sandbox is valid, and that it is in the native file system
        test_file_name = self._write_file('.')
        empty_sandbox_path = self._verify_valid_sandbox_file()
        self.assertEqual(os.path.isfile(test_file_name), True)
        os.remove(test_file_name)
        return empty_sandbox_path

    def _verify_current_sandbox_is_preset(self):
        # Verify that the current sandbox is 'default_sandbox'
        sandbox_path = self._verify_valid_sandbox_file()
        self.assertEqual(len(os.listdir(sandbox_path)), 1)
        self.assertEqual(os.path.isdir(os.path.join(sandbox_path, 'sampleData')), True)
        head, tail = os.path.split(sandbox_path)
        self.assertEqual(tail, PREDEFINED_SANDBOX_NAME)
        return sandbox_path

    def _remove_sandbox_and_verify(self, sandbox_name, existed, original_sandbox_path):
        # Remove a sandbox and verify the information returned by the sandbox_remove()
        removed_sandbox = sandbox_remove(sandbox_name)
        self.assertIsInstance(removed_sandbox, dict)
        self.assertSetEqual(set(removed_sandbox.keys()), {'sandboxPath', 'existed'})
        self.assertEqual(removed_sandbox['sandboxPath'], original_sandbox_path)
        self.assertEqual(removed_sandbox['existed'], existed)

    def _verify_sandbox_path(self, sandbox_path, sandbox_name=_TEST_SANDBOX_NAME):
        # Verify that a sandbox path looks legit ... that it is in the CytoscapeConfiguration/filetransfer directory
        self.assertIsInstance(sandbox_path, str)
        test_sandbox_path = os.path.split(sandbox_path)
        filetransfer_path = os.path.split(test_sandbox_path[0])
        cyconfig_path = os.path.split(filetransfer_path[0])
        self.assertEqual(test_sandbox_path[1], sandbox_name)
        self.assertEqual(filetransfer_path[1], 'filetransfer')
        self.assertEqual(cyconfig_path[1], 'CytoscapeConfiguration')

    def _write_file(self, sandbox_name):
        file_name = os.path.join(sandbox_name, _TEST_FILE)
        with open(file_name, 'w') as file:
            file.write('This is a test')
        return file_name


if __name__ == '__main__':
    unittest.main()
