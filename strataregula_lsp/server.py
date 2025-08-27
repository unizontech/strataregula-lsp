"""
Main Language Server implementation for StrataRegula.
"""

import logging
import sys
from typing import Optional, List, Any, Dict
from pathlib import Path

from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_REFERENCES,
    TEXT_DOCUMENT_DOCUMENT_SYMBOL,
    TEXT_DOCUMENT_RENAME,
    TEXT_DOCUMENT_FORMATTING,
    TEXT_DOCUMENT_RANGE_FORMATTING,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_DID_CLOSE,
    CompletionItem,
    CompletionList,
    CompletionParams,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    DidCloseTextDocumentParams,
    HoverParams,
    Hover,
    DefinitionParams,
    Location,
    ReferenceParams,
    DocumentSymbolParams,
    DocumentSymbol,
    RenameParams,
    WorkspaceEdit,
    DocumentFormattingParams,
    DocumentRangeFormattingParams,
    TextEdit,
    InitializeParams,
    InitializeResult,
    ServerCapabilities,
    TextDocumentSyncKind,
    CompletionOptions,
    HoverOptions,
    DefinitionOptions,
    ReferenceOptions,
    DocumentSymbolOptions,
    RenameOptions,
    DocumentFormattingOptions,
    DocumentRangeFormattingOptions,
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position,
    MarkupContent,
    MarkupKind,
)

from .handlers import (
    CompletionHandler,
    HoverHandler,
    DiagnosticsHandler,
    DefinitionHandler,
    ReferencesHandler,
    SymbolsHandler,
    RenameHandler,
    FormattingHandler,
)
from .analyzer import YamlAnalyzer, PatternValidator
from .utils import ConfigLoader

logger = logging.getLogger(__name__)


class StrataRegulaLanguageServer(LanguageServer):
    """Language Server for StrataRegula YAML configuration files."""
    
    def __init__(self, *args, **kwargs):
        super().__init__("strataregula-lsp", "v0.1.0", *args, **kwargs)
        
        # Initialize handlers
        self.completion_handler = CompletionHandler(self)
        self.hover_handler = HoverHandler(self)
        self.diagnostics_handler = DiagnosticsHandler(self)
        self.definition_handler = DefinitionHandler(self)
        self.references_handler = ReferencesHandler(self)
        self.symbols_handler = SymbolsHandler(self)
        self.rename_handler = RenameHandler(self)
        self.formatting_handler = FormattingHandler(self)
        
        # Initialize analyzer
        self.analyzer = YamlAnalyzer()
        self.validator = PatternValidator()
        
        # Configuration
        self.config = ConfigLoader()
        
        # Document cache
        self.documents = {}
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all LSP method handlers."""
        
        @self.feature(TEXT_DOCUMENT_COMPLETION)
        async def completion(params: CompletionParams) -> CompletionList:
            """Handle completion requests."""
            return await self.completion_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_HOVER)
        async def hover(params: HoverParams) -> Optional[Hover]:
            """Handle hover requests."""
            return await self.hover_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_DEFINITION)
        async def definition(params: DefinitionParams) -> Optional[List[Location]]:
            """Handle go to definition requests."""
            return await self.definition_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_REFERENCES)
        async def references(params: ReferenceParams) -> Optional[List[Location]]:
            """Handle find references requests."""
            return await self.references_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
        async def document_symbol(params: DocumentSymbolParams) -> Optional[List[DocumentSymbol]]:
            """Handle document symbol requests."""
            return await self.symbols_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_RENAME)
        async def rename(params: RenameParams) -> Optional[WorkspaceEdit]:
            """Handle rename requests."""
            return await self.rename_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_FORMATTING)
        async def formatting(params: DocumentFormattingParams) -> Optional[List[TextEdit]]:
            """Handle document formatting requests."""
            return await self.formatting_handler.handle(params)
        
        @self.feature(TEXT_DOCUMENT_RANGE_FORMATTING)
        async def range_formatting(params: DocumentRangeFormattingParams) -> Optional[List[TextEdit]]:
            """Handle range formatting requests."""
            return await self.formatting_handler.handle_range(params)
        
        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        def did_open(params: DidOpenTextDocumentParams):
            """Handle document open events."""
            doc = params.text_document
            self.documents[doc.uri] = {
                "version": doc.version,
                "content": doc.text,
                "language_id": doc.language_id
            }
            # Run diagnostics
            self._run_diagnostics(doc.uri)
        
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams):
            """Handle document change events."""
            doc = params.text_document
            if doc.uri in self.documents:
                self.documents[doc.uri]["version"] = doc.version
                # For incremental sync, apply changes
                for change in params.content_changes:
                    if hasattr(change, 'text'):
                        self.documents[doc.uri]["content"] = change.text
                # Run diagnostics if configured for on-change
                if self.config.get("validation.on_change", False):
                    self._run_diagnostics(doc.uri)
        
        @self.feature(TEXT_DOCUMENT_DID_SAVE)
        def did_save(params: DidSaveTextDocumentParams):
            """Handle document save events."""
            doc = params.text_document
            # Run diagnostics on save
            if self.config.get("validation.on_save", True):
                self._run_diagnostics(doc.uri)
        
        @self.feature(TEXT_DOCUMENT_DID_CLOSE)
        def did_close(params: DidCloseTextDocumentParams):
            """Handle document close events."""
            doc = params.text_document
            if doc.uri in self.documents:
                del self.documents[doc.uri]
                # Clear diagnostics for closed document
                self.publish_diagnostics(doc.uri, [])
    
    def _run_diagnostics(self, uri: str):
        """Run diagnostics on a document."""
        if uri not in self.documents:
            return
        
        content = self.documents[uri]["content"]
        diagnostics = self.diagnostics_handler.analyze(uri, content)
        self.publish_diagnostics(uri, diagnostics)
    
    def get_document(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get document from cache."""
        return self.documents.get(uri)
    
    def get_document_content(self, uri: str) -> Optional[str]:
        """Get document content from cache."""
        doc = self.get_document(uri)
        return doc["content"] if doc else None


def main():
    """Main entry point for the language server."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
        stream=sys.stderr
    )
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="StrataRegula Language Server")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Use stdio for communication (default)"
    )
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="Use TCP for communication"
    )
    parser.add_argument(
        "--ws",
        action="store_true",
        help="Use WebSocket for communication"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for TCP/WebSocket mode"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for TCP/WebSocket mode"
    )
    
    args = parser.parse_args()
    
    # Create and start server
    server = StrataRegulaLanguageServer()
    
    if args.tcp:
        logger.info(f"Starting StrataRegula LSP server on TCP {args.host}:{args.port}")
        server.start_tcp(args.host, args.port)
    elif args.ws:
        logger.info(f"Starting StrataRegula LSP server on WebSocket {args.host}:{args.port}")
        server.start_ws(args.host, args.port)
    else:
        logger.info("Starting StrataRegula LSP server on stdio")
        server.start_io()


if __name__ == "__main__":
    main()