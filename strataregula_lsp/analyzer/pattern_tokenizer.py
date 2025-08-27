"""
Pattern Tokenizer - Analyzes pattern context for IntelliSense
Based on IntelliSense_Completion_Flow UML sequence diagram
"""
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .pattern_analyzer import PatternContext


@dataclass
class TokenContext:
    """Token context for pattern analysis"""
    token: str
    token_type: str  # 'key', 'value', 'partial_key', 'partial_value'
    depth: int
    position: int
    is_completion_point: bool


class PatternTokenizer:
    """
    Tokenizes YAML patterns for intelligent completion
    Core component in IntelliSense_Completion_Flow
    """
    
    def __init__(self):
        self.yaml_key_pattern = re.compile(r'^(\s*)([a-zA-Z_]\w*)(:?)(.*)$')
        self.yaml_value_pattern = re.compile(r'^(\s*[a-zA-Z_]\w*:\s*)(.*)$')
        self.service_pattern = re.compile(r'\b(prod|dev|test|staging)\b')
        
    def parsePatternContext(self, text_before_cursor: str) -> PatternContext:
        """
        Main entry point from IntelliSense flow sequence
        Analyzes pattern depth and extracts current pattern
        """
        lines = text_before_cursor.split('\n')
        if not lines:
            return PatternContext(0, "", [], (0, 0))
            
        current_line = lines[-1]
        previous_lines = lines[:-1]
        
        # Analyze pattern depth from indentation
        depth = self._analyze_pattern_depth(current_line)
        
        # Extract current pattern being typed
        current_pattern = self._extract_current_pattern(current_line)
        
        # Build parent pattern hierarchy
        parent_patterns = self._build_parent_hierarchy(previous_lines, depth)
        
        # Calculate position
        line_num = len(lines) - 1
        column = len(current_line)
        
        return PatternContext(
            depth=depth,
            current_pattern=current_pattern,
            parent_patterns=parent_patterns,
            position=(line_num, column)
        )
    
    def _analyze_pattern_depth(self, line: str) -> int:
        """Analyze YAML nesting depth from indentation"""
        if not line.strip():
            return 0
            
        # Count leading whitespace
        leading_spaces = len(line) - len(line.lstrip())
        
        # Standard YAML uses 2-space indentation
        yaml_depth = leading_spaces // 2
        
        # Check if this is a key or value position
        if ':' in line and not line.strip().endswith(':'):
            # This is a key-value pair, we're at value level
            return yaml_depth + 1
        elif line.strip().endswith(':') or '.' in line.strip():
            # This is a key or partial key
            return yaml_depth
        else:
            # Incomplete line, assume key level
            return yaml_depth
    
    def _extract_current_pattern(self, line: str) -> str:
        """Extract the current pattern being typed"""
        stripped = line.strip()
        
        if not stripped:
            return ""
            
        # Check for key completion (ends with . or partial key)
        if '.' in stripped:
            # Pattern like "prod." or "config.db."
            parts = stripped.split('.')
            return '.'.join(parts[:-1]) if len(parts) > 1 else parts[0]
        elif ':' in stripped:
            # Key-value pattern, extract key
            key_part = stripped.split(':')[0]
            return key_part.strip()
        else:
            # Partial key being typed
            return stripped
    
    def _build_parent_hierarchy(self, previous_lines: List[str], current_depth: int) -> List[str]:
        """Build hierarchy of parent patterns from previous lines"""
        parents = []
        
        # Process lines in reverse to build hierarchy
        for line in reversed(previous_lines):
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            line_depth = (len(line) - len(line.lstrip())) // 2
            
            # Only include lines that are parents (less indented)
            if line_depth < current_depth:
                key_match = re.match(r'^\s*([a-zA-Z_]\w*):?', line)
                if key_match:
                    key = key_match.group(1)
                    parents.insert(0, key)  # Insert at beginning to maintain order
                    current_depth = line_depth
                    
                    # Stop when we reach root level
                    if line_depth == 0:
                        break
                        
        return parents
    
    def isInValuePosition(self, text_before_cursor: str) -> bool:
        """
        Determine if cursor is in a value position vs key position
        Used by Pattern Provider in completion flow
        """
        lines = text_before_cursor.split('\n')
        if not lines:
            return False
            
        current_line = lines[-1]
        stripped = current_line.strip()
        
        # Value position indicators:
        # 1. Line contains : and cursor is after it
        # 2. Previous line ended with : and current line is indented
        
        if ':' in stripped and not stripped.endswith(':'):
            # Current line has key: value format
            colon_pos = stripped.find(':')
            after_colon = stripped[colon_pos + 1:].strip()
            return len(after_colon) == 0 or '.' in after_colon
            
        # Check if previous line ended with colon
        if len(lines) > 1:
            prev_line = lines[-2].strip()
            if prev_line.endswith(':'):
                current_indent = len(current_line) - len(current_line.lstrip())
                prev_indent = len(lines[-2]) - len(lines[-2].lstrip())
                return current_indent > prev_indent
                
        return False
    
    def tokenize_line(self, line: str) -> List[TokenContext]:
        """Tokenize a single YAML line into meaningful tokens"""
        tokens = []
        
        if not line.strip():
            return tokens
            
        # Calculate indentation depth
        leading_spaces = len(line) - len(line.lstrip())
        depth = leading_spaces // 2
        
        stripped = line.strip()
        
        # Handle different YAML line patterns
        if ':' in stripped:
            # Key-value line
            parts = stripped.split(':', 1)
            key_part = parts[0].strip()
            value_part = parts[1].strip() if len(parts) > 1 else ""
            
            # Key token
            tokens.append(TokenContext(
                token=key_part,
                token_type='key',
                depth=depth,
                position=leading_spaces,
                is_completion_point=False
            ))
            
            # Value token if present
            if value_part:
                tokens.append(TokenContext(
                    token=value_part,
                    token_type='value',
                    depth=depth + 1,
                    position=leading_spaces + len(key_part) + 2,
                    is_completion_point=value_part.endswith('.')
                ))
            else:
                # Empty value, completion point
                tokens.append(TokenContext(
                    token="",
                    token_type='value',
                    depth=depth + 1,
                    position=len(line),
                    is_completion_point=True
                ))
        else:
            # Partial key or list item
            token_type = 'partial_key' if not stripped.startswith('-') else 'list_item'
            
            tokens.append(TokenContext(
                token=stripped,
                token_type=token_type,
                depth=depth,
                position=leading_spaces,
                is_completion_point=stripped.endswith('.')
            ))
            
        return tokens
    
    def find_completion_context(self, text: str, position: int) -> Optional[TokenContext]:
        """Find the token context at the given cursor position"""
        lines = text.split('\n')
        current_pos = 0
        
        for line_num, line in enumerate(lines):
            line_end = current_pos + len(line)
            
            if current_pos <= position <= line_end:
                # Found the line containing the cursor
                column = position - current_pos
                tokens = self.tokenize_line(line)
                
                # Find the token at this column
                for token in tokens:
                    token_end = token.position + len(token.token)
                    if token.position <= column <= token_end:
                        return token
                        
                # If no token found, create a completion context
                return TokenContext(
                    token="",
                    token_type='partial_key',
                    depth=(len(line) - len(line.lstrip())) // 2,
                    position=column,
                    is_completion_point=True
                )
                
            current_pos = line_end + 1  # +1 for newline
            
        return None