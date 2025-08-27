"""
StrataRegula Language Server Protocol Implementation.

Provides intelligent YAML configuration pattern analysis and validation
for StrataRegula configuration files.
"""

__version__ = "0.1.0"
__author__ = "StrataRegula Team"

from .server import StrataRegulaLanguageServer

__all__ = ["StrataRegulaLanguageServer"]