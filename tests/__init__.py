# -*- coding: utf-8 -*-

"""Unit test package for py_fx_bin."""

import os
import sys

# Add project root to Python path
tests_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(tests_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set environment variable to disable loguru before it's imported elsewhere
os.environ["LOGURU_LEVEL"] = "ERROR"

# Configure loguru to be quiet during tests - but handle case where it's not installed
try:
    from loguru import logger
    # Remove default handler
    logger.remove()
    # Add a null handler or set to only critical errors
    logger.add(sys.stderr, level="CRITICAL")
except ImportError:
    # Create a dummy logger if loguru is not available
    class DummyLogger:
        def remove(self): pass
        def add(self, *args, **kwargs): pass
        def debug(self, msg): pass
        def info(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
    
    # Make logger available for modules that import it
    sys.modules['loguru'] = type(sys)('loguru')
    sys.modules['loguru'].logger = DummyLogger()
