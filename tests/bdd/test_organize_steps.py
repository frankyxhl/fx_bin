"""Step definitions for file organization BDD scenarios.

This module implements pytest-bdd step definitions for the fx organize command.
This is a placeholder file for the RED phase - step implementations will follow.
"""

import pytest
from pytest_bdd import scenarios

# Load all scenarios from the organize feature file
# This will cause pytest to discover all scenarios but report missing steps
scenarios("organize.feature")
