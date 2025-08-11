# -*- coding: utf-8 -*-

"""Unit test package for py_fx_bin."""

import os
import sys

# Set environment variable to disable loguru before it's imported elsewhere
os.environ["LOGURU_LEVEL"] = "ERROR"

# Configure loguru to be quiet during tests
from loguru import logger

# Remove default handler
logger.remove()

# Add a null handler or set to only critical errors
# This ensures any module that imports loguru after this will be quiet
logger.add(sys.stderr, level="CRITICAL")
