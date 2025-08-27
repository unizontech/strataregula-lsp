"""
LSP request handlers for StrataRegula Language Server.
"""

from .completion import CompletionHandler
from .hover import HoverHandler
from .diagnostics import DiagnosticsHandler
from .definition import DefinitionHandler
from .references import ReferencesHandler
from .symbols import SymbolsHandler
from .rename import RenameHandler
from .formatting import FormattingHandler

__all__ = [
    "CompletionHandler",
    "HoverHandler",
    "DiagnosticsHandler",
    "DefinitionHandler",
    "ReferencesHandler",
    "SymbolsHandler",
    "RenameHandler",
    "FormattingHandler",
]