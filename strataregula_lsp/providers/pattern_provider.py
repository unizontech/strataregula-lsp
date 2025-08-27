"""
Pattern Provider - Main completion provider for StrataRegula patterns
Based on IntelliSense_Completion_Flow sequence diagram
"""
from typing import List, Optional, Dict, Any
from lsprotocol.types import (
    CompletionItem, CompletionItemKind, Position,
    CompletionParams, InsertTextFormat
)
from ..analyzer.pattern_analyzer import PatternAnalyzer, PatternContext, LearnedPattern
from ..analyzer.pattern_tokenizer import PatternTokenizer


class PatternProvider:
    """
    Core completion provider following IntelliSense_Completion_Flow
    Integrates with Pattern Analyzer and Tokenizer
    """
    
    def __init__(self, pattern_analyzer: PatternAnalyzer):
        self.analyzer = pattern_analyzer
        self.tokenizer = PatternTokenizer()
        
        # Common StrataRegula patterns
        self.base_patterns = {
            "services": ["frontend", "backend", "api", "worker", "database", "cache", "queue", "proxy", "web"],
            "environments": ["prod", "dev", "test", "staging", "local"],
            "config_types": ["database", "redis", "kafka", "elasticsearch", "monitoring"],
            "wildcard_patterns": ["*", "**", "service.*", "*.prod", "prod.*"]
        }
        
    def provideCompletions(self, document: Any, position: Position) -> List[CompletionItem]:
        """
        Main completion entry point from LSP handler
        Follows the IntelliSense_Completion_Flow sequence
        """
        # Get document text and cursor position
        text = document.source if hasattr(document, 'source') else (
            document.text if hasattr(document, 'text') else str(document)
        )
        text_before_cursor = self._get_text_before_cursor(text, position)
        
        # Parse pattern context using tokenizer
        context = self.tokenizer.parsePatternContext(text_before_cursor)
        
        # Check if we're in a value position
        is_value_pos = self.tokenizer.isInValuePosition(text_before_cursor)
        
        # Always provide completions if we have a pattern context
        if context.current_pattern or is_value_pos:
            # Query learned patterns database
            learned_services = self._query_learned_services(context.current_pattern)
            
            # Generate completions based on context
            completions = self.generateCompletions(context, learned_services)
            
            return completions
        
        # No completions for this context
        return []
    
    def generateCompletions(self, context: PatternContext, learned_services: List[str]) -> List[CompletionItem]:
        """Generate completion items based on pattern context and depth"""
        completions = []
        
        # Always provide some basic completions
        if context.depth <= 1:
            # Services level - provide service completions
            completions.extend(self.createServiceCompletions(context, learned_services))
            completions.extend(self._add_wildcard_options())
            
        if context.depth == 2:
            # Config Types level
            completions.extend(self.createConfigTypeCompletions(context))
            
        if context.depth > 2:
            # Advanced completions for deeper nesting
            completions.extend(self.createAdvancedCompletions(context))
        
        # If no completions generated, provide basic service patterns
        if not completions:
            completions.extend(self.createServiceCompletions(context, []))
            
        return completions
    
    def createServiceCompletions(self, context: PatternContext, learned_services: List[str]) -> List[CompletionItem]:
        """Create service-level completions"""
        completions = []
        current_pattern = context.current_pattern.lower()
        
        # Add learned services first (higher priority)
        for service in learned_services:
            if service.lower().startswith(current_pattern):
                completions.append(CompletionItem(
                    label=service,
                    kind=CompletionItemKind.Module,
                    detail=f"Learned service pattern",
                    documentation=f"Service: {service} (learned from existing configurations)",
                    insert_text=service,
                    sort_text=f"0_{service}"  # High priority
                ))
        
        # Add base service patterns
        for service in self.base_patterns["services"]:
            if current_pattern == "" or service.lower().startswith(current_pattern):
                if service not in learned_services:  # Avoid duplicates
                    completions.append(CompletionItem(
                        label=service,
                        kind=CompletionItemKind.Module,
                        detail="Standard service type",
                        documentation=f"Common service pattern: {service}",
                        insert_text=service,
                        sort_text=f"1_{service}"  # Lower priority than learned
                    ))
        
        # Add environment patterns if they match
        for env in self.base_patterns["environments"]:
            if current_pattern == "" or env.lower().startswith(current_pattern):
                completions.append(CompletionItem(
                    label=env,
                    kind=CompletionItemKind.Enum,
                    detail="Environment name",
                    documentation=f"Environment: {env}",
                    insert_text=env,
                    sort_text=f"2_{env}"  # Lower priority than services
                ))
        
        return completions
    
    def createConfigTypeCompletions(self, context: PatternContext) -> List[CompletionItem]:
        """Create configuration type completions"""
        completions = []
        current_pattern = context.current_pattern.lower()
        
        for config_type in self.base_patterns["config_types"]:
            if config_type.lower().startswith(current_pattern):
                # Create snippet-style completion
                snippet_text = self._create_config_snippet(config_type)
                
                completions.append(CompletionItem(
                    label=config_type,
                    kind=CompletionItemKind.Class,
                    detail=f"{config_type.title()} configuration",
                    documentation=f"Configuration block for {config_type} service",
                    insert_text=snippet_text,
                    insert_text_format=InsertTextFormat.Snippet,
                    sort_text=f"0_{config_type}"
                ))
                
        return completions
    
    def createAdvancedCompletions(self, context: PatternContext) -> List[CompletionItem]:
        """Create advanced completions for deep nesting"""
        completions = []
        current_pattern = context.current_pattern.lower()
        
        # Environment-specific completions
        if any(env in context.parent_patterns for env in self.base_patterns["environments"]):
            for env in self.base_patterns["environments"]:
                if env.startswith(current_pattern):
                    completions.append(CompletionItem(
                        label=env,
                        kind=CompletionItemKind.Enum,
                        detail=f"Environment: {env}",
                        insert_text=env,
                        sort_text=f"env_{env}"
                    ))
        
        # Configuration keys based on parent context
        if "database" in context.parent_patterns:
            db_keys = ["host", "port", "name", "user", "password", "ssl", "pool_size"]
            for key in db_keys:
                if key.startswith(current_pattern):
                    completions.append(CompletionItem(
                        label=key,
                        kind=CompletionItemKind.Property,
                        detail=f"Database {key}",
                        insert_text=f"{key}: ",
                        sort_text=f"db_{key}"
                    ))
        
        return completions
    
    def _add_wildcard_options(self) -> List[CompletionItem]:
        """Add wildcard pattern options"""
        wildcards = []
        
        for pattern in self.base_patterns["wildcard_patterns"]:
            wildcards.append(CompletionItem(
                label=pattern,
                kind=CompletionItemKind.Keyword,
                detail="Wildcard pattern",
                documentation=f"Matches multiple services: {pattern}",
                insert_text=pattern,
                sort_text=f"z_{pattern}"  # Low priority
            ))
            
        return wildcards
    
    def _query_learned_services(self, pattern: str) -> List[str]:
        """Query learned services from pattern database"""
        if not pattern:
            return []
            
        learned_patterns = self.analyzer.query_patterns(pattern, max_depth=1)
        services = []
        
        for learned_pattern in learned_patterns:
            services.extend(list(learned_pattern.services))
            
        # Remove duplicates and sort by relevance
        unique_services = list(set(services))
        unique_services.sort()
        
        return unique_services[:10]  # Limit to top 10
    
    def _get_text_before_cursor(self, text: str, position: Position) -> str:
        """Extract text before cursor position"""
        lines = text.split('\n')
        
        if position.line >= len(lines):
            return text
            
        # Get all lines before cursor line
        before_lines = lines[:position.line]
        
        # Get partial line up to cursor
        current_line = lines[position.line]
        current_line_part = current_line[:position.character]
        
        # Combine
        all_before = '\n'.join(before_lines + [current_line_part])
        return all_before
    
    def _create_config_snippet(self, config_type: str) -> str:
        """Create configuration snippets for different service types"""
        snippets = {
            "database": """host: ${1:localhost}
port: ${2:5432}
name: ${3:dbname}
user: ${4:username}
password: ${5:password}""",
            
            "redis": """host: ${1:localhost}
port: ${2:6379}
db: ${3:0}
password: ${4:}""",
            
            "kafka": """brokers: ${1:localhost:9092}
topic: ${2:events}
group_id: ${3:consumer-group}""",
            
            "elasticsearch": """hosts: ${1:localhost:9200}
index: ${2:logs}
timeout: ${3:30s}""",
            
            "monitoring": """enabled: ${1:true}
interval: ${2:30s}
endpoint: ${3:/metrics}"""
        }
        
        return snippets.get(config_type, f"{config_type}: ${{1:value}}")