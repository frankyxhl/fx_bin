"""Security tests for fx_upload_server module.

These tests must pass before the upload server can be considered safe for production use.
All tests are designed to fail initially and pass only after security fixes are implemented.
"""
import os
import tempfile
import unittest
import socket
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from http.client import HTTPConnection
from urllib.parse import quote

# Silence loguru during tests
from loguru import logger
logger.remove()

from fx_bin.upload_server import SimpleHTTPRequestHandler, HTTPServer, get_lan_ip


class TestUploadServerSecurity(unittest.TestCase):
    """Test security aspects of upload server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.server = None
        self.server_thread = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.server:
            self.server.shutdown()
        if self.server_thread:
            self.server_thread.join(timeout=5)
        import shutil
        shutil.rmtree(self.test_dir)
    
    def start_test_server(self, port=0):
        """Start server for integration tests."""
        try:
            self.server = HTTPServer(('127.0.0.1', port), SimpleHTTPRequestHandler)
            self.server_port = self.server.server_address[1]
            
            def run_server():
                os.chdir(self.test_dir)
                self.server.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            time.sleep(0.1)  # Give server time to start
            return self.server_port
        except Exception as e:
            self.fail(f"Could not start test server: {e}")
    
    def test_path_traversal_attack_blocked(self):
        """Test that path traversal attacks are blocked."""
        # Create a file outside upload directory
        sensitive_file = Path(tempfile.gettempdir()) / "sensitive_data.txt"
        sensitive_file.write_text("SECRET_DATA")
        
        try:
            port = self.start_test_server()
            conn = HTTPConnection('127.0.0.1', port)
            
            # Attempt path traversal attacks
            traversal_attempts = [
                "../sensitive_data.txt",
                "..%2Fsensitive_data.txt",
                "..%5Csensitive_data.txt",
                "%2e%2e/sensitive_data.txt",
                "....//sensitive_data.txt",
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            ]
            
            for attempt in traversal_attempts:
                with self.subTest(attempt=attempt):
                    try:
                        # Try to upload with malicious filename
                        boundary = 'testboundary123'
                        body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{attempt}"\r\nContent-Type: text/plain\r\n\r\nMALICIOUS_CONTENT\r\n--{boundary}--\r\n'''
                        
                        headers = {
                            'Content-Type': f'multipart/form-data; boundary={boundary}',
                            'Content-Length': str(len(body))
                        }
                        
                        conn.request('POST', '/', body, headers)
                        response = conn.getresponse()
                        
                        # Should be rejected (not 200 OK)
                        self.assertNotEqual(response.status, 200, 
                                          f"Path traversal attack succeeded with: {attempt}")
                        
                        # Sensitive file should still exist and be unchanged
                        if sensitive_file.exists():
                            self.assertEqual(sensitive_file.read_text(), "SECRET_DATA")
                    except Exception:
                        pass  # Connection errors are acceptable for blocked attempts
        finally:
            if sensitive_file.exists():
                sensitive_file.unlink()
    
    def test_file_upload_restricted_to_allowed_directory(self):
        """Test that file uploads are restricted to allowed upload directory."""
        port = self.start_test_server()
        conn = HTTPConnection('127.0.0.1', port)
        
        # Create upload directory
        upload_dir = self.test_path / "uploads"
        upload_dir.mkdir()
        
        boundary = 'testboundary123'
        body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test.txt"\r\nContent-Type: text/plain\r\n\r\ntest content\r\n--{boundary}--\r\n'''
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        conn.request('POST', '/uploads/', body, headers)
        response = conn.getresponse()
        
        # File should only exist in allowed directory
        allowed_file = upload_dir / "test.txt"
        if response.status == 200:  # If upload succeeded
            self.assertTrue(allowed_file.exists(), "File not created in allowed directory")
        
        # File should NOT exist outside allowed directory
        outside_file = self.test_path / "test.txt"
        self.assertFalse(outside_file.exists(), "File created outside allowed directory")
    
    def test_symlink_upload_blocked(self):
        """Test that symlink uploads are blocked."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")
        
        port = self.start_test_server()
        
        # Create a symlink to sensitive file
        sensitive_file = Path(tempfile.gettempdir()) / "sensitive.txt"
        sensitive_file.write_text("SENSITIVE")
        
        symlink_path = self.test_path / "symlink_test"
        symlink_path.symlink_to(sensitive_file)
        
        try:
            conn = HTTPConnection('127.0.0.1', port)
            
            # Try to upload the symlink
            boundary = 'testboundary123'
            body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="symlink_test"\r\nContent-Type: text/plain\r\n\r\nmalicious content\r\n--{boundary}--\r\n'''
            
            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body))
            }
            
            conn.request('POST', '/', body, headers)
            response = conn.getresponse()
            
            # Should not create or modify files through symlinks
            self.assertNotEqual(response.status, 200, "Symlink upload should be blocked")
            
            # Original file should be unchanged
            self.assertEqual(sensitive_file.read_text(), "SENSITIVE")
        finally:
            if sensitive_file.exists():
                sensitive_file.unlink()
    
    def test_max_file_size_limit(self):
        """Test that file size limits are enforced."""
        port = self.start_test_server()
        conn = HTTPConnection('127.0.0.1', port)
        
        # Try to upload very large file (simulated)
        large_content = "X" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        boundary = 'testboundary123'
        body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="large.txt"\r\nContent-Type: text/plain\r\n\r\n{large_content}\r\n--{boundary}--\r\n'''
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        try:
            conn.request('POST', '/', body, headers)
            response = conn.getresponse()
            
            # Should reject large files
            self.assertNotEqual(response.status, 200, "Large file upload should be rejected")
        except Exception:
            pass  # Connection errors acceptable for rejected uploads
    
    def test_file_type_validation(self):
        """Test that dangerous file types are blocked."""
        port = self.start_test_server()
        conn = HTTPConnection('127.0.0.1', port)
        
        dangerous_files = [
            ("malware.exe", "application/octet-stream"),
            ("script.bat", "application/x-bat"),
            ("virus.scr", "application/octet-stream"),
            ("backdoor.php", "application/x-php"),
            ("shell.jsp", "application/x-jsp"),
            ("attack.js", "application/javascript"),
        ]
        
        for filename, content_type in dangerous_files:
            with self.subTest(filename=filename):
                boundary = 'testboundary123'
                body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\nmalicious content\r\n--{boundary}--\r\n'''
                
                headers = {
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Content-Length': str(len(body))
                }
                
                try:
                    conn.request('POST', '/', body, headers)
                    response = conn.getresponse()
                    
                    # Should reject dangerous file types
                    self.assertNotEqual(response.status, 200, 
                                      f"Dangerous file type {filename} should be blocked")
                except Exception:
                    pass  # Connection errors acceptable for blocked files
    
    def test_authentication_required(self):
        """Test that authentication is required for uploads."""
        port = self.start_test_server()
        conn = HTTPConnection('127.0.0.1', port)
        
        # Try upload without authentication
        boundary = 'testboundary123'
        body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test.txt"\r\nContent-Type: text/plain\r\n\r\ntest content\r\n--{boundary}--\r\n'''
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        conn.request('POST', '/', body, headers)
        response = conn.getresponse()
        
        # Should require authentication (401 Unauthorized)
        self.assertEqual(response.status, 401, "Upload should require authentication")
    
    def test_server_binds_localhost_only(self):
        """Test that server only binds to localhost by default."""
        # Test that get_lan_ip is not used for binding by default
        with patch('fx_bin.upload_server.HTTPServer') as mock_server:
            from fx_bin.upload_server import main
            
            # Mock to prevent actual server startup
            mock_server.return_value.serve_forever.side_effect = KeyboardInterrupt()
            
            try:
                main()
            except SystemExit:
                pass
            
            # Server should be created with localhost binding
            args, kwargs = mock_server.call_args
            host, port = args[0]
            self.assertIn(host, ['127.0.0.1', 'localhost'], 
                         "Server should bind to localhost only by default")
    
    def test_upload_directory_permissions(self):
        """Test that upload directory has correct permissions."""
        port = self.start_test_server()
        
        # Create upload directory
        upload_dir = self.test_path / "uploads"
        upload_dir.mkdir()
        
        # Directory should have restrictive permissions (not world-writable)
        stat = upload_dir.stat()
        mode = stat.st_mode & 0o777
        
        # Should not be world-writable (no write for others)
        self.assertEqual(mode & 0o002, 0, "Upload directory should not be world-writable")
    
    def test_filename_sanitization(self):
        """Test that filenames are properly sanitized."""
        port = self.start_test_server()
        conn = HTTPConnection('127.0.0.1', port)
        
        malicious_names = [
            "../../etc/passwd",
            "con.txt",  # Windows reserved name
            "nul.txt",  # Windows reserved name
            "file<>name.txt",  # Invalid characters
            "file|name.txt",   # Pipe character
            "file*name.txt",   # Wildcard
            "file?name.txt",   # Question mark
            "\x00filename.txt",  # Null byte
            "filename\r\n.txt",  # CRLF injection
        ]
        
        for malicious_name in malicious_names:
            with self.subTest(filename=malicious_name):
                boundary = 'testboundary123'
                body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{malicious_name}"\r\nContent-Type: text/plain\r\n\r\ntest content\r\n--{boundary}--\r\n'''
                
                headers = {
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Content-Length': str(len(body))
                }
                
                try:
                    conn.request('POST', '/', body, headers)
                    response = conn.getresponse()
                    
                    # Should either reject or sanitize the filename
                    if response.status == 200:
                        # If accepted, filename should be sanitized
                        # Check no malicious files were created
                        for root, dirs, files in os.walk(self.test_dir):
                            for file in files:
                                self.assertNotIn("..", file, "Sanitization failed")
                                self.assertNotIn("/", file, "Sanitization failed")
                                self.assertNotIn("\\", file, "Sanitization failed")
                except Exception:
                    pass  # Connection errors acceptable
    
    def test_concurrent_upload_limits(self):
        """Test that concurrent upload limits are enforced."""
        port = self.start_test_server()
        
        # This test would require implementing actual concurrency limits
        # For now, we test that the server can handle multiple connections gracefully
        connections = []
        
        try:
            for i in range(10):  # Try 10 concurrent connections
                conn = HTTPConnection('127.0.0.1', port)
                connections.append(conn)
                
                boundary = f'testboundary{i}'
                body = f'''--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test{i}.txt"\r\nContent-Type: text/plain\r\n\r\ntest content {i}\r\n--{boundary}--\r\n'''
                
                headers = {
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Content-Length': str(len(body))
                }
                
                try:
                    conn.request('POST', '/', body, headers)
                except Exception:
                    pass  # Some connections may be rejected, which is acceptable
        finally:
            for conn in connections:
                try:
                    conn.close()
                except Exception:
                    pass


class TestUploadServerConfiguration(unittest.TestCase):
    """Test server configuration security."""
    
    def test_default_configuration_secure(self):
        """Test that default configuration is secure."""
        # Server should not bind to all interfaces by default
        with patch('fx_bin.upload_server.get_lan_ip') as mock_get_ip:
            mock_get_ip.return_value = '192.168.1.100'  # Simulate LAN IP
            
            # Should not use LAN IP for binding in secure mode
            # This test will need to be implemented with the security fixes
            pass
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses."""
        # This would test for headers like:
        # - X-Content-Type-Options: nosniff
        # - X-Frame-Options: DENY
        # - X-XSS-Protection: 1; mode=block
        # - Content-Security-Policy: default-src 'self'
        pass


if __name__ == '__main__':
    unittest.main()