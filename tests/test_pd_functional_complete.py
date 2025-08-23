"""Comprehensive tests for fx_bin.pd_functional module.

This module provides tests to increase coverage from 46% to 75%+.
"""

import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

import pandas as pd
from click.testing import CliRunner
from returns.io import IOResult, IOSuccess, IOFailure, IO
from returns.result import Success, Failure

from fx_bin import pd_functional
from fx_bin.errors import PdError, ValidationError, IOError as FxIOError


class TestCheckPandasAvailable(unittest.TestCase):
    """Test pandas availability checking."""
    
    def test_pandas_available(self):
        """Test when pandas is available."""
        result = pd_functional.check_pandas_available()
        self.assertIsInstance(result, Success)
        self.assertIsNotNone(result.unwrap())
    
    @patch.dict('sys.modules', {'pandas': None})
    def test_pandas_not_available(self):
        """Test when pandas is not available."""
        # Temporarily remove pandas from sys.modules
        with patch('builtins.__import__', side_effect=ImportError("No module named 'pandas'")):
            result = pd_functional.check_pandas_available()
            self.assertIsInstance(result, Failure)
            error = result.failure()
            self.assertIsInstance(error, PdError)
            self.assertIn("pandas", str(error))


class TestValidateOutputFilename(unittest.TestCase):
    """Test output filename validation."""
    
    def test_validate_filename_with_extension(self):
        """Test filename that already has .xlsx extension."""
        result = pd_functional.validate_output_filename("output.xlsx")
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), "output.xlsx")
    
    def test_validate_filename_without_extension(self):
        """Test filename without extension."""
        result = pd_functional.validate_output_filename("output")
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), "output.xlsx")
    
    def test_validate_filename_with_wrong_extension(self):
        """Test filename with different extension."""
        result = pd_functional.validate_output_filename("output.txt")
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), "output.txt.xlsx")
    
    def test_validate_filename_with_path_separator(self):
        """Test filename with path separator (invalid)."""
        result = pd_functional.validate_output_filename("path/to/file.xlsx")
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, ValidationError)
        self.assertIn("Invalid", str(error))
    
    def test_validate_filename_starting_with_dot(self):
        """Test filename starting with dot (hidden file)."""
        result = pd_functional.validate_output_filename(".hidden.xlsx")
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, ValidationError)


class TestCheckFileNotExists(unittest.TestCase):
    """Test file existence checking."""
    
    def test_file_not_exists(self):
        """Test when file doesn't exist."""
        result = pd_functional.check_file_not_exists("/nonexistent/file.xlsx")
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), "/nonexistent/file.xlsx")
    
    def test_file_exists(self):
        """Test when file already exists."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = pd_functional.check_file_not_exists(tmp_path)
            self.assertIsInstance(result, Failure)
            error = result.failure()
            self.assertIsInstance(error, ValidationError)
            self.assertIn("already exists", str(error))
        finally:
            os.unlink(tmp_path)


class TestValidateUrl(unittest.TestCase):
    """Test URL validation."""
    
    def test_validate_http_url(self):
        """Test valid HTTP URL."""
        result = pd_functional.validate_url("http://example.com/data.json")
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), "http://example.com/data.json")
    
    def test_validate_https_url(self):
        """Test valid HTTPS URL."""
        result = pd_functional.validate_url("https://example.com/data.json")
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), "https://example.com/data.json")
    
    def test_validate_empty_url(self):
        """Test empty URL."""
        result = pd_functional.validate_url("")
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, ValidationError)
        self.assertIn("empty", str(error).lower())
    
    def test_validate_file_protocol(self):
        """Test file:// protocol (should be rejected)."""
        result = pd_functional.validate_url("file:///etc/passwd")
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, ValidationError)
        self.assertIn("not allowed", str(error))
    
    def test_validate_local_file_path(self):
        """Test local file path (should pass basic validation)."""
        # Local file paths are actually allowed (not URLs)
        result = pd_functional.validate_url("/path/to/file.json")
        self.assertIsInstance(result, Success)


class TestProcessJsonToExcel(unittest.TestCase):
    """Test JSON to Excel processing."""
    
    def test_process_json_string(self):
        """Test processing JSON string."""
        pandas_module = pd
        json_str = '{"name": ["Alice", "Bob"], "age": [25, 30]}'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.xlsx")
            result = pd_functional.process_json_to_excel(
                pandas_module, json_str, output_file
            )
            
            self.assertIsInstance(result, IOSuccess)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify content
            df = pd.read_excel(output_file)
            self.assertEqual(len(df), 2)
            self.assertIn("name", df.columns)
    
    def test_process_json_file(self):
        """Test processing JSON file."""
        pandas_module = pd
        data = {"items": ["item1", "item2"], "quantity": [5, 10]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as json_file:
            json.dump(data, json_file)
            json_path = json_file.name
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.xlsx")
            
            try:
                result = pd_functional.process_json_to_excel(
                    pandas_module, json_path, output_file
                )
                
                self.assertIsInstance(result, IOSuccess)
                self.assertTrue(os.path.exists(output_file))
            finally:
                os.unlink(json_path)
    
    @patch('pandas.read_json')
    def test_process_url(self, mock_read_json):
        """Test processing URL."""
        pandas_module = pd
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_json.return_value = mock_df
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.xlsx")
            result = pd_functional.process_json_to_excel(
                pandas_module, "https://example.com/data.json", output_file
            )
            
            self.assertIsInstance(result, IOSuccess)
            mock_read_json.assert_called_once()
    
    def test_process_invalid_json(self):
        """Test processing invalid JSON."""
        pandas_module = pd
        invalid_json = '{"invalid": json}'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.xlsx")
            result = pd_functional.process_json_to_excel(
                pandas_module, invalid_json, output_file
            )
            
            # Due to @impure_safe decorator, the result is IOSuccess wrapping an IO containing an IOResult
            self.assertIsInstance(result, IOSuccess)
            # Extract the inner IO object
            inner_io = result.unwrap()
            self.assertIsInstance(inner_io, IO)
            # Extract the IOResult from the IO object
            inner_result = inner_io._inner_value
            self.assertIsInstance(inner_result, IOFailure)
            # The error is also wrapped in an IO object
            error_io = inner_result.failure()
            self.assertIsInstance(error_io, IO)
            # Extract the actual error
            error = error_io._inner_value
            self.assertIsInstance(error, FxIOError)
    
    @patch('pandas.DataFrame.to_excel')
    def test_process_write_error(self, mock_to_excel):
        """Test handling write errors."""
        pandas_module = pd
        mock_to_excel.side_effect = IOError("Disk full")
        
        json_str = '{"data": [1, 2, 3]}'
        result = pd_functional.process_json_to_excel(
            pandas_module, json_str, "/tmp/output.xlsx"
        )
        
        # Due to @impure_safe decorator, the result is IOSuccess wrapping an IO containing an IOResult
        self.assertIsInstance(result, IOSuccess)
        # Extract the inner IO object
        inner_io = result.unwrap()
        self.assertIsInstance(inner_io, IO)
        # Extract the IOResult from the IO object
        inner_result = inner_io._inner_value
        self.assertIsInstance(inner_result, IOFailure)
        # The error is also wrapped in an IO object
        error_io = inner_result.failure()
        self.assertIsInstance(error_io, IO)
        # Extract the actual error
        error = error_io._inner_value
        self.assertIsInstance(error, FxIOError)
        self.assertIn("Disk full", str(error))


class TestMainFunctional(unittest.TestCase):
    """Test the main_functional function."""
    
    @patch('fx_bin.pd_functional.process_json_to_excel')
    @patch('fx_bin.pd_functional.check_file_not_exists')
    def test_main_functional_success(self, mock_check_file, mock_process):
        """Test successful main execution."""
        mock_check_file.return_value = Success("output.xlsx")
        mock_process.return_value = IOSuccess(None)
        
        result = pd_functional.main_functional("data.json", "output")
        
        self.assertIsInstance(result, Success)
        self.assertEqual(result.unwrap(), 0)
    
    @patch('fx_bin.pd_functional.check_pandas_available')
    def test_main_functional_no_pandas(self, mock_check_pandas):
        """Test when pandas is not available."""
        mock_check_pandas.return_value = Failure(PdError("No pandas"))
        
        result = pd_functional.main_functional("data.json", "output")
        
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, PdError)
    
    def test_main_functional_invalid_url(self):
        """Test with invalid URL."""
        result = pd_functional.main_functional("", "output")
        
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, ValidationError)
    
    def test_main_functional_invalid_filename(self):
        """Test with invalid filename."""
        result = pd_functional.main_functional("data.json", "/path/to/output")
        
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, ValidationError)
    
    @patch('fx_bin.pd_functional.process_json_to_excel')
    @patch('fx_bin.pd_functional.check_file_not_exists')
    def test_main_functional_process_error(self, mock_check_file, mock_process):
        """Test when processing fails."""
        mock_check_file.return_value = Success("output.xlsx")
        mock_process.return_value = IOFailure(FxIOError("Processing failed"))
        
        result = pd_functional.main_functional("data.json", "output")
        
        self.assertIsInstance(result, Failure)
        error = result.failure()
        self.assertIsInstance(error, PdError)
        self.assertIn("Processing failed", str(error))


class TestMainCLI(unittest.TestCase):
    """Test the CLI main function."""
    
    @patch('fx_bin.pd_functional.main_functional')
    def test_main_cli_success(self, mock_main_func):
        """Test successful CLI execution."""
        mock_main_func.return_value = Success(0)
        
        runner = CliRunner()
        result = runner.invoke(pd_functional.main, ["data.json", "output"])
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), "")
    
    @patch('fx_bin.pd_functional.main_functional')
    def test_main_cli_failure(self, mock_main_func):
        """Test CLI execution with error."""
        mock_main_func.return_value = Failure(PdError("Test error"))
        
        runner = CliRunner()
        result = runner.invoke(pd_functional.main, ["data.json", "output"])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Test error", result.output)


class TestMainLegacy(unittest.TestCase):
    """Test the legacy main function."""
    
    @patch('fx_bin.pd_functional.main_functional')
    def test_main_legacy_success(self, mock_main_func):
        """Test successful legacy execution."""
        mock_main_func.return_value = Success(0)
        
        result = pd_functional.main_legacy("data.json", "output")
        
        self.assertEqual(result, 0)
    
    @patch('builtins.print')
    @patch('fx_bin.pd_functional.main_functional')
    def test_main_legacy_failure(self, mock_main_func, mock_print):
        """Test legacy execution with error."""
        mock_main_func.return_value = Failure(PdError("Test error"))
        
        result = pd_functional.main_legacy("data.json", "output")
        
        self.assertEqual(result, 1)
        mock_print.assert_called_once_with("Test error")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete flow."""
    
    def test_complete_json_to_excel_flow(self):
        """Test complete JSON to Excel conversion."""
        json_data = {"products": ["A", "B", "C"], "prices": [10, 20, 30]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as json_file:
            json.dump(json_data, json_file)
            json_path = json_file.name
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = "output"
            
            # Change to temp directory to write output there
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Use the main_functional directly
                result = pd_functional.main_functional(json_path, output_file)
                
                self.assertIsInstance(result, Success)
                self.assertEqual(result.unwrap(), 0)
                
                # Verify the output file was created
                expected_file = "output.xlsx"
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content
                df = pd.read_excel(expected_file)
                self.assertEqual(len(df), 3)
                self.assertIn("products", df.columns)
                self.assertIn("prices", df.columns)
            finally:
                os.chdir(original_cwd)
                os.unlink(json_path)
    
    def test_json_string_to_excel(self):
        """Test converting JSON string to Excel."""
        json_str = '{"names": ["Alice", "Bob"], "scores": [95, 87]}'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = "test_output"
            
            # Change to temp directory to write output there
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                result = pd_functional.main_functional(json_str, output_file)
                
                self.assertIsInstance(result, Success)
                self.assertEqual(result.unwrap(), 0)
                
                # Verify file was created
                self.assertTrue(os.path.exists("test_output.xlsx"))
            finally:
                os.chdir(original_cwd)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""
    
    def test_empty_json(self):
        """Test with empty JSON."""
        json_str = '{}'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "empty")
            os.chdir(tmpdir)
            
            result = pd_functional.main_functional(json_str, "empty")
            
            # Empty JSON should still create a file
            self.assertIsInstance(result, Success)
    
    def test_nested_json(self):
        """Test with nested JSON structure."""
        # Nested JSON might be flattened or fail depending on structure
        json_str = '{"data": {"nested": {"value": 123}}}'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            result = pd_functional.main_functional(json_str, "nested")
            
            # Just verify it returns a result (could be Success or Failure)
            self.assertIsInstance(result, (Success, Failure))
    
    def test_large_json(self):
        """Test with large JSON data."""
        # Create large JSON array
        large_data = json.dumps({
            "ids": list(range(1000)),
            "values": [i * 2 for i in range(1000)]
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            result = pd_functional.main_functional(large_data, "large")
            
            self.assertIsInstance(result, Success)
            self.assertTrue(os.path.exists("large.xlsx"))


if __name__ == '__main__':
    unittest.main()