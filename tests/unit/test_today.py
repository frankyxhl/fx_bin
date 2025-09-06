"""Unit tests for fx today command functionality.

These tests follow TDD principles - written before implementation.
They test the core functionality of creating and managing daily workspace directories.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import os
import tempfile
import shutil
from click.testing import CliRunner


class TestGetTodayPath(unittest.TestCase):
    """Test the get_today_path function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_date = datetime(2025, 9, 6)
        
    @patch('fx_bin.today.datetime')
    def test_get_today_path_default(self, mock_datetime):
        """Test default path generation ~/Downloads/YYYYMMDD."""
        from fx_bin.today import get_today_path
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        
        result = get_today_path()
        
        self.assertTrue(str(result).endswith('Downloads/20250906'))
        self.assertIsInstance(result, Path)
        
    @patch('fx_bin.today.datetime')
    def test_get_today_path_custom_base(self, mock_datetime):
        """Test custom base directory."""
        from fx_bin.today import get_today_path
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        
        result = get_today_path(base_dir='~/Projects')
        
        self.assertTrue(str(result).endswith('Projects/20250906'))
        
    @patch('fx_bin.today.datetime')
    def test_get_today_path_custom_format(self, mock_datetime):
        """Test custom date format."""
        from fx_bin.today import get_today_path
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        
        result = get_today_path(date_format='%Y-%m-%d')
        
        self.assertTrue(str(result).endswith('Downloads/2025-09-06'))
        
    @patch('fx_bin.today.datetime')
    def test_get_today_path_relative_base(self, mock_datetime):
        """Test relative base directory."""
        from fx_bin.today import get_today_path
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        
        result = get_today_path(base_dir='./temp')
        
        self.assertTrue(str(result).endswith('temp/20250906'))
        
    def test_expand_home_directory(self):
        """Test that ~ is properly expanded to home directory."""
        from fx_bin.today import get_today_path
        
        result = get_today_path(base_dir='~/TestDir')
        
        self.assertNotIn('~', str(result))
        self.assertTrue(result.is_absolute())


class TestEnsureDirectoryExists(unittest.TestCase):
    """Test the ensure_directory_exists function."""
    
    def setUp(self):
        """Create a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_create_directory_if_not_exists(self):
        """Test creating a new directory."""
        from fx_bin.today import ensure_directory_exists
        
        test_path = Path(self.temp_dir) / 'new_directory'
        self.assertFalse(test_path.exists())
        
        result = ensure_directory_exists(test_path)
        
        self.assertTrue(result)
        self.assertTrue(test_path.exists())
        self.assertTrue(test_path.is_dir())
        
    def test_handle_existing_directory(self):
        """Test handling when directory already exists."""
        from fx_bin.today import ensure_directory_exists
        
        test_path = Path(self.temp_dir) / 'existing_directory'
        test_path.mkdir()
        self.assertTrue(test_path.exists())
        
        result = ensure_directory_exists(test_path)
        
        self.assertTrue(result)
        self.assertTrue(test_path.exists())
        self.assertTrue(test_path.is_dir())
        
    def test_create_nested_directories(self):
        """Test creating nested directory structure."""
        from fx_bin.today import ensure_directory_exists
        
        test_path = Path(self.temp_dir) / 'level1' / 'level2' / 'level3'
        self.assertFalse(test_path.exists())
        
        result = ensure_directory_exists(test_path)
        
        self.assertTrue(result)
        self.assertTrue(test_path.exists())
        self.assertTrue(test_path.is_dir())
        
    @patch('pathlib.Path.mkdir')
    def test_handle_permission_error(self, mock_mkdir):
        """Test graceful handling of permission denied."""
        from fx_bin.today import ensure_directory_exists
        
        mock_mkdir.side_effect = PermissionError("Permission denied")
        test_path = Path(self.temp_dir) / 'no_permission'
        
        result = ensure_directory_exists(test_path)
        
        self.assertFalse(result)
        
    def test_handle_file_exists_as_non_directory(self):
        """Test handling when path exists but is a file, not directory."""
        from fx_bin.today import ensure_directory_exists
        
        test_file = Path(self.temp_dir) / 'existing_file'
        test_file.touch()  # Create a file, not a directory
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.is_file())
        
        result = ensure_directory_exists(test_file)
        
        self.assertFalse(result)


class TestValidation(unittest.TestCase):
    """Test validation functions."""
    
    def test_validate_date_format_valid(self):
        """Test validation of valid date format strings."""
        from fx_bin.today import validate_date_format
        
        valid_formats = [
            '%Y%m%d',
            '%Y-%m-%d',
            '%Y_%m_%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%B_%d_%Y'
        ]
        
        for fmt in valid_formats:
            with self.subTest(format=fmt):
                self.assertTrue(validate_date_format(fmt))
                
    def test_validate_date_format_invalid(self):
        """Test validation of invalid date format strings."""
        from fx_bin.today import validate_date_format
        
        invalid_formats = [
            'invalid_format',
            '2025-09-06',  # Not a format string, but actual date
            '%Z',  # Invalid format code
            '',  # Empty string
            None  # None value
        ]
        
        for fmt in invalid_formats:
            with self.subTest(format=fmt):
                self.assertFalse(validate_date_format(fmt))
                
    def test_validate_date_format_security_traversal(self):
        """Test that malicious date formats with path traversal are rejected."""
        from fx_bin.today import validate_date_format
        
        malicious_formats = [
            "%Y../../..",      # Basic traversal
            "%Y/%m/../..",     # Multiple level traversal
            "%Y\\..\\..\\",    # Windows-style traversal
            "%Y/../sensitive", # Attempt to access parent directory
            "%Y/./../../etc",  # Complex traversal with current dir
            "%Y%m%d/../..",    # Traversal after valid date
            "../%Y%m%d",       # Traversal before valid date
            "%Y/%m/%d/..",     # Partial traversal in structured date
        ]
        
        for fmt in malicious_formats:
            with self.subTest(format=fmt):
                self.assertFalse(validate_date_format(fmt))
                
    def test_validate_date_format_security_separators(self):
        """Test that invalid separators and structures are rejected."""
        from fx_bin.today import validate_date_format
        
        # These should be rejected due to backslashes (Windows path separators)
        # or unsafe prefixes/suffixes that could cause issues
        invalid_formats = [
            "%Y\\%m\\%d",      # Backslashes (Windows style - rejected by regex)
            "prefix/%Y%m%d",   # Path prefix (literal text before date)
            "%Y%m%d/suffix",   # Path suffix (literal text after date)  
        ]
        
        for fmt in invalid_formats:
            with self.subTest(format=fmt):
                self.assertFalse(validate_date_format(fmt))
                
    def test_validate_date_format_valid_separators(self):
        """Test that valid date formats with separators are allowed."""
        from fx_bin.today import validate_date_format
        
        # These should be allowed as they create valid date directory structures
        valid_formats = [
            "%Y/%m/%d",        # Standard date path (2025/09/06)
            "%Y/%m",           # Year/month path (2025/09) 
            "%Y-%m/%d",        # Mixed separators (2025-09/06)
        ]
        
        for fmt in valid_formats:
            with self.subTest(format=fmt):
                self.assertTrue(validate_date_format(fmt))

    def test_validate_date_format_month_names(self):
        """Test that date formats with month names are allowed."""
        from fx_bin.today import validate_date_format
        
        month_formats = [
            "%Y/%B/%d",        # 2025/September/06  
            "%B-%d-%Y",        # September-06-2025
            "%d_%B_%Y",        # 06_September_2025 (single directory, underscore)
            "%Y/%b/%d",        # 2025/Sep/06 (abbreviated month)
        ]
        
        for fmt in month_formats:
            with self.subTest(format=fmt):
                self.assertTrue(validate_date_format(fmt))
                
    def test_validate_date_format_security_special_chars(self):
        """Test that date formats with special characters are rejected."""
        from fx_bin.today import validate_date_format
        
        special_char_formats = [
            "%Y%m%d\x00",      # Null byte
            "%Y%m%d\n",        # Newline
            "%Y%m%d\t",        # Tab
            "%Y%m%d*",         # Wildcard
            "%Y%m%d?",         # Question mark
            "%Y%m%d|",         # Pipe character  
            "%Y%m%d<",         # Less than
            "%Y%m%d>",         # Greater than
            "%Y%m%d:",         # Colon
            "%Y%m%d;",         # Semicolon
            "%Y%m%d\"",        # Quote
        ]
        
        for fmt in special_char_formats:
            with self.subTest(format=fmt):
                self.assertFalse(validate_date_format(fmt))


class TestDetectShell(unittest.TestCase):
    """Test shell detection functionality."""
    
    def test_detect_shell_from_environment(self):
        """Test detecting shell from SHELL environment variable."""
        from fx_bin.today import detect_shell_executable
        import os
        from unittest.mock import patch
        
        with patch.dict(os.environ, {'SHELL': '/bin/zsh'}):
            with patch('os.path.isfile', return_value=True):
                result = detect_shell_executable()
                self.assertEqual(result, '/bin/zsh')
                
    def test_detect_shell_unix_fallbacks(self):
        """Test Unix shell fallback detection."""
        from fx_bin.today import detect_shell_executable
        import os
        from unittest.mock import patch
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.isfile') as mock_isfile:
                # Mock that zsh exists but bash doesn't
                def side_effect(path):
                    return path == '/bin/zsh'
                mock_isfile.side_effect = side_effect
                
                result = detect_shell_executable()
                self.assertEqual(result, '/bin/zsh')
                
    def test_detect_shell_windows(self):
        """Test Windows shell detection."""
        from fx_bin.today import detect_shell_executable
        import os
        from unittest.mock import patch
        
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('shutil.which') as mock_which:
                    # Mock that pwsh is available
                    def side_effect(name):
                        if name == 'pwsh':
                            return 'C:\\Program Files\\PowerShell\\7\\pwsh.exe'
                        return None
                    mock_which.side_effect = side_effect
                    
                    result = detect_shell_executable()
                    self.assertTrue(result.endswith('pwsh.exe'))
                    
    def test_detect_shell_windows_fallback(self):
        """Test Windows shell fallback to cmd."""
        from fx_bin.today import detect_shell_executable
        import os
        from unittest.mock import patch
        
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('shutil.which') as mock_which:
                    # Mock that only cmd is available
                    def side_effect(name):
                        if name == 'cmd':
                            return 'C:\\Windows\\System32\\cmd.exe'
                        return None
                    mock_which.side_effect = side_effect
                    
                    result = detect_shell_executable()
                    self.assertTrue(result.endswith('cmd.exe'))


class TestExecShell(unittest.TestCase):
    """Test exec shell functionality."""
    
    def setUp(self):
        """Set up test environment."""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_main_with_exec_shell_unix(self):
        """Test main function with exec_shell=True on Unix."""
        from fx_bin.today import main
        from unittest.mock import patch, MagicMock
        import os
        
        # Mock dependencies
        with patch('fx_bin.today.validate_base_path', return_value=True), \
             patch('fx_bin.today.validate_date_format', return_value=True), \
             patch('fx_bin.today.get_today_path') as mock_path, \
             patch('fx_bin.today.ensure_directory_exists', return_value=True), \
             patch('fx_bin.today.detect_shell_executable', return_value='/bin/zsh'), \
             patch('os.chdir') as mock_chdir, \
             patch('os.execv') as mock_execv, \
             patch('sys.platform', 'darwin'):
            
            mock_path.return_value = self.temp_dir
            
            # Call main with exec_shell=True
            main(exec_shell=True)
            
            # Verify directory change and shell execution
            mock_chdir.assert_called_once_with(self.temp_dir)
            mock_execv.assert_called_once_with('/bin/zsh', ['zsh'])
            
    def test_main_with_exec_shell_windows(self):
        """Test main function with exec_shell=True on Windows."""
        from fx_bin.today import main
        from unittest.mock import patch, MagicMock
        
        # Mock dependencies
        with patch('fx_bin.today.validate_base_path', return_value=True), \
             patch('fx_bin.today.validate_date_format', return_value=True), \
             patch('fx_bin.today.get_today_path') as mock_path, \
             patch('fx_bin.today.ensure_directory_exists', return_value=True), \
             patch('fx_bin.today.detect_shell_executable', return_value='powershell'), \
             patch('os.chdir') as mock_chdir, \
             patch('os.execv') as mock_execv, \
             patch('sys.platform', 'win32'):
            
            mock_path.return_value = self.temp_dir
            
            # Call main with exec_shell=True
            main(exec_shell=True)
            
            # Verify directory change and shell execution
            mock_chdir.assert_called_once_with(self.temp_dir)
            mock_execv.assert_called_once_with('powershell', ['powershell', '-NoLogo'])
            
    def test_main_exec_shell_error_handling(self):
        """Test exec shell error handling."""
        from fx_bin.today import main
        from unittest.mock import patch
        import sys
        
        # Mock dependencies to raise an exception during execv
        with patch('fx_bin.today.validate_base_path', return_value=True), \
             patch('fx_bin.today.validate_date_format', return_value=True), \
             patch('fx_bin.today.get_today_path') as mock_path, \
             patch('fx_bin.today.ensure_directory_exists', return_value=True), \
             patch('fx_bin.today.detect_shell_executable', return_value='/bin/zsh'), \
             patch('os.chdir'), \
             patch('os.execv', side_effect=Exception("Shell execution failed")), \
             patch('sys.exit') as mock_exit:
            
            mock_path.return_value = self.temp_dir
            
            # Call main with exec_shell=True - should handle the exception
            main(exec_shell=True)
            
            # Verify sys.exit was called due to error
            mock_exit.assert_called_once_with(1)
                
    def test_validate_base_path_security(self):
        """Test path traversal attack prevention."""
        from fx_bin.today import validate_base_path
        
        unsafe_paths = [
            '../../../etc',
            '~/Downloads/../../../etc',
            '/etc/../root',
            '././../../../etc'
        ]
        
        for path in unsafe_paths:
            with self.subTest(path=path):
                self.assertFalse(validate_base_path(path))
                
    def test_validate_base_path_safe(self):
        """Test validation of safe base paths."""
        from fx_bin.today import validate_base_path
        
        safe_paths = [
            '~/Downloads',
            '~/Projects',
            './temp',
            '/Users/test/Documents',
            'relative/path'
        ]
        
        for path in safe_paths:
            with self.subTest(path=path):
                self.assertTrue(validate_base_path(path))


class TestMainFunction(unittest.TestCase):
    """Test the main CLI function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_date = datetime(2025, 9, 6)
        
    @patch('fx_bin.today.datetime')
    @patch('fx_bin.today.ensure_directory_exists')
    def test_main_with_cd_flag(self, mock_ensure, mock_datetime):
        """Test main function with --cd flag outputs path only."""
        from fx_bin.today import main
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        mock_ensure.return_value = True
        
        with patch('click.echo') as mock_echo:
            main(output_for_cd=True, base_dir='~/Downloads', date_format='%Y%m%d')
            
            # Should output path only for shell integration
            mock_echo.assert_called_once()
            call_args = mock_echo.call_args[0][0]
            self.assertIn('Downloads/20250906', call_args)
            
    @patch('fx_bin.today.datetime')
    @patch('fx_bin.today.ensure_directory_exists')
    def test_main_without_cd_flag(self, mock_ensure, mock_datetime):
        """Test main function without --cd flag outputs friendly message."""
        from fx_bin.today import main
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        mock_ensure.return_value = True
        
        with patch('click.echo') as mock_echo:
            main(output_for_cd=False, base_dir='~/Downloads', date_format='%Y%m%d')
            
            # Should output friendly message
            mock_echo.assert_called_once()
            call_args = mock_echo.call_args[0][0]
            self.assertIn("Today's workspace:", call_args)
            self.assertIn('Downloads/20250906', call_args)
            
    @patch('fx_bin.today.ensure_directory_exists')
    def test_main_handles_creation_failure(self, mock_ensure):
        """Test main function handles directory creation failure."""
        from fx_bin.today import main
        
        mock_ensure.return_value = False
        
        with self.assertRaises(SystemExit) as cm:
            main(output_for_cd=True, base_dir='~/Downloads', date_format='%Y%m%d')
            
        self.assertEqual(cm.exception.code, 1)
        
    def test_main_handles_invalid_date_format(self):
        """Test main function handles invalid date format."""
        from fx_bin.today import main
        
        with self.assertRaises(SystemExit) as cm:
            main(output_for_cd=True, base_dir='~/Downloads', date_format='invalid')
            
        self.assertEqual(cm.exception.code, 1)
        
    def test_main_handles_invalid_base_path(self):
        """Test main function handles invalid base path."""
        from fx_bin.today import main
        
        with self.assertRaises(SystemExit) as cm:
            main(output_for_cd=True, base_dir='../../../etc', date_format='%Y%m%d')
            
        self.assertEqual(cm.exception.code, 1)
        
    @patch('fx_bin.today.datetime')
    @patch('fx_bin.today.ensure_directory_exists')
    def test_main_with_verbose_flag(self, mock_ensure, mock_datetime):
        """Test main function with verbose output."""
        from fx_bin.today import main
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        mock_ensure.return_value = True
        
        with patch('click.echo') as mock_echo:
            main(output_for_cd=False, base_dir='~/Downloads', 
                 date_format='%Y%m%d', verbose=True)
            
            # Should have multiple echo calls for verbose output
            self.assertTrue(mock_echo.call_count > 1)
            
    @patch('fx_bin.today.datetime')
    def test_main_with_dry_run(self, mock_datetime):
        """Test main function with dry run mode."""
        from fx_bin.today import main
        
        mock_datetime.now.return_value = self.test_date
        mock_datetime.strftime = datetime.strftime
        
        with patch('click.echo') as mock_echo:
            with patch('fx_bin.today.ensure_directory_exists') as mock_ensure:
                main(output_for_cd=False, base_dir='~/Downloads', 
                     date_format='%Y%m%d', dry_run=True)
                
                # Should NOT call ensure_directory_exists in dry run
                mock_ensure.assert_not_called()
                
                # Should output what would be created
                mock_echo.assert_called()
                call_args = mock_echo.call_args[0][0]
                self.assertIn('Would create:', call_args)


if __name__ == '__main__':
    unittest.main()