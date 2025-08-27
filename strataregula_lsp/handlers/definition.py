"""Definition handler for StrataRegula Language Server."""
from typing import List, Optional
from lsprotocol.types import Location, DefinitionParams

class DefinitionHandler:
    def __init__(self, server): self.server = server
    async def handle(self, params: DefinitionParams) -> Optional[List[Location]]: return None
