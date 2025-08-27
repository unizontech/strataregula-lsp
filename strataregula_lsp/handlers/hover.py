"""Hover handler for StrataRegula Language Server."""

from typing import Optional
from lsprotocol.types import Hover, HoverParams, MarkupContent, MarkupKind


class HoverHandler:
    """Handles hover requests."""
    
    def __init__(self, server):
        self.server = server
    
    async def handle(self, params: HoverParams) -> Optional[Hover]:
        """Handle hover request."""
        # TODO: Implement hover logic
        return None