"""
Completion handler for StrataRegula Language Server.
"""

from typing import List, Optional
from lsprotocol.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    CompletionItemKind,
    InsertTextFormat,
    MarkupContent,
    MarkupKind,
)


class CompletionHandler:
    """Handles completion requests for StrataRegula patterns."""
    
    def __init__(self, server):
        self.server = server
        self.snippets = self._load_snippets()
    
    def _load_snippets(self) -> List[CompletionItem]:
        """Load StrataRegula snippets and patterns."""
        return [
            CompletionItem(
                label="service_times",
                kind=CompletionItemKind.Snippet,
                insert_text="service_times:\n  ${1:service}.${2:*}.${3:metric}: ${4:100}",
                insert_text_format=InsertTextFormat.Snippet,
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value="Service timing configuration with wildcard patterns"
                )
            ),
            CompletionItem(
                label="resource_limits",
                kind=CompletionItemKind.Snippet,
                insert_text="resource_limits:\n  ${1:service}.${2:*}.cpu: ${3:80}\n  ${1:service}.${2:*}.memory: ${4:512}",
                insert_text_format=InsertTextFormat.Snippet,
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value="Resource limit configuration for services"
                )
            ),
            CompletionItem(
                label="traffic_routing",
                kind=CompletionItemKind.Snippet,
                insert_text="traffic_routing:\n  ${1:source}.${2:*} -> ${3:destination}.${4:*}: ${5:weight}",
                insert_text_format=InsertTextFormat.Snippet,
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value="Traffic routing configuration with patterns"
                )
            ),
            # Wildcard patterns
            CompletionItem(
                label="*",
                kind=CompletionItemKind.Operator,
                insert_text="*",
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value="**Single-level wildcard**: Matches one hierarchy level\n\nExample: `web.*.response` matches `web.frontend.response` but not `web.api.v1.response`"
                )
            ),
            CompletionItem(
                label="**",
                kind=CompletionItemKind.Operator,
                insert_text="**",
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value="**Recursive wildcard**: Matches multiple hierarchy levels\n\nExample: `api.**.timeout` matches both `api.v1.timeout` and `api.v1.users.timeout`"
                )
            ),
            # Common keys
            CompletionItem(
                label="regions",
                kind=CompletionItemKind.Property,
                insert_text="regions:\n  ${1:region_name}:",
                insert_text_format=InsertTextFormat.Snippet,
            ),
            CompletionItem(
                label="environments",
                kind=CompletionItemKind.Property,
                insert_text="environments:\n  ${1:env_name}:",
                insert_text_format=InsertTextFormat.Snippet,
            ),
        ]
    
    async def handle(self, params: CompletionParams) -> CompletionList:
        """Handle completion request."""
        uri = params.text_document.uri
        position = params.position
        
        # Get document content
        content = self.server.get_document_content(uri)
        if not content:
            return CompletionList(is_incomplete=False, items=[])
        
        # Get context at cursor position
        lines = content.split('\n')
        if position.line >= len(lines):
            return CompletionList(is_incomplete=False, items=[])
        
        line = lines[position.line]
        col = position.character
        
        # Determine context and filter completions
        items = self._get_context_completions(line, col)
        
        return CompletionList(is_incomplete=False, items=items)
    
    def _get_context_completions(self, line: str, col: int) -> List[CompletionItem]:
        """Get completions based on context."""
        # For now, return all snippets
        # TODO: Implement context-aware filtering
        return self.snippets