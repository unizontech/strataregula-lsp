"""
Pattern Analyzer - Core YAML analysis and pattern extraction
Based on Pattern_Learning_Sequence and YAML_Analysis_Activity UML diagrams
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml
from dataclasses import dataclass


@dataclass
class LearnedPattern:
    """Core data structure for learned patterns from UML Core_Data_Structures"""
    pattern: str
    depth: int
    frequency: int
    context: str
    confidence: float
    services: Set[str]


@dataclass
class PatternContext:
    """Pattern context from IntelliSense completion flow"""
    depth: int
    current_pattern: str
    parent_patterns: List[str]
    position: Tuple[int, int]


class PatternAnalyzer:
    """Main pattern analysis engine following YAML_Analysis_Activity flow"""
    
    def __init__(self):
        self.learned_patterns: Dict[str, LearnedPattern] = {}
        self.hierarchy_cache: Dict[str, Dict] = {}
        
    def analyze_yaml_file(self, file_path: Path) -> Dict[str, LearnedPattern]:
        """
        Main entry point following YAML_Analysis_Activity diagram:
        File → Parse → Extract → Learn → Store
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse YAML content
            yaml_data = yaml.safe_load(content)
            if not yaml_data:
                return {}
                
            # Extract patterns from structure
            patterns = self._extract_patterns(yaml_data, file_path.stem)
            
            # Learn and update patterns
            for pattern_key, pattern in patterns.items():
                self._learn_pattern(pattern_key, pattern)
                
            return patterns
            
        except (yaml.YAMLError, IOError) as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}
    
    def _extract_patterns(self, yaml_data: Dict, context: str) -> Dict[str, LearnedPattern]:
        """Extract hierarchical patterns from YAML structure"""
        patterns = {}
        
        def traverse(data, path="", depth=0):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Create pattern for this key
                    pattern = LearnedPattern(
                        pattern=current_path,
                        depth=depth,
                        frequency=1,
                        context=context,
                        confidence=0.8,
                        services=self._extract_services(value)
                    )
                    patterns[current_path] = pattern
                    
                    # Recurse into nested structures
                    if isinstance(value, dict):
                        traverse(value, current_path, depth + 1)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                traverse(item, f"{current_path}[{i}]", depth + 1)
                                
        traverse(yaml_data)
        return patterns
    
    def _extract_services(self, value) -> Set[str]:
        """Extract service names from configuration values"""
        services = set()
        
        if isinstance(value, str):
            # Look for common service patterns
            service_patterns = [
                r'\b(frontend|backend|api|worker|database|cache|queue)\b',
                r'\b(\w+)[-_]service\b',
                r'\b(\w+)[-_](api|svc)\b'
            ]
            
            for pattern in service_patterns:
                matches = re.findall(pattern, value, re.IGNORECASE)
                services.update(match if isinstance(match, str) else match[0] for match in matches)
                
        elif isinstance(value, dict):
            # Check for service-like keys
            for key in value.keys():
                if any(service_key in key.lower() for service_key in ['service', 'svc', 'app']):
                    services.add(key)
                    
        return services
    
    def _learn_pattern(self, pattern_key: str, pattern: LearnedPattern):
        """Update learned patterns database with frequency and confidence"""
        if pattern_key in self.learned_patterns:
            existing = self.learned_patterns[pattern_key]
            existing.frequency += 1
            existing.confidence = min(1.0, existing.confidence + 0.1)
            existing.services.update(pattern.services)
        else:
            self.learned_patterns[pattern_key] = pattern
    
    def query_patterns(self, partial_pattern: str, max_depth: int = None) -> List[LearnedPattern]:
        """Query learned patterns for completion suggestions"""
        matches = []
        
        for pattern_key, pattern in self.learned_patterns.items():
            if pattern_key.startswith(partial_pattern):
                if max_depth is None or pattern.depth <= max_depth:
                    matches.append(pattern)
                    
        # Sort by confidence and frequency
        matches.sort(key=lambda p: (p.confidence, p.frequency), reverse=True)
        return matches
    
    def get_pattern_context(self, text: str, position: int) -> PatternContext:
        """Parse pattern context from cursor position - key for IntelliSense flow"""
        lines = text.split('\n')
        line_start = 0
        current_line = 0
        
        # Find current line and column
        for i, line in enumerate(lines):
            if line_start + len(line) >= position:
                current_line = i
                column = position - line_start
                break
            line_start += len(line) + 1
        else:
            current_line = len(lines) - 1
            column = len(lines[-1]) if lines else 0
            
        # Extract current pattern context
        current_line_text = lines[current_line] if current_line < len(lines) else ""
        before_cursor = current_line_text[:column]
        
        # Parse YAML hierarchy from indentation
        depth = self._calculate_depth(before_cursor)
        current_pattern = self._extract_current_pattern(before_cursor)
        parent_patterns = self._extract_parent_patterns(lines[:current_line])
        
        return PatternContext(
            depth=depth,
            current_pattern=current_pattern,
            parent_patterns=parent_patterns,
            position=(current_line, column)
        )
    
    def _calculate_depth(self, text: str) -> int:
        """Calculate YAML nesting depth from indentation"""
        stripped = text.lstrip()
        indent_chars = len(text) - len(stripped)
        return indent_chars // 2  # Assuming 2-space indentation
    
    def _extract_current_pattern(self, text: str) -> str:
        """Extract the current pattern being typed"""
        # Look for YAML key pattern
        match = re.search(r'(\w+)\.?$', text.strip())
        return match.group(1) if match else ""
    
    def _extract_parent_patterns(self, lines: List[str]) -> List[str]:
        """Extract parent patterns from previous lines"""
        parents = []
        current_indent = float('inf')
        
        for line in reversed(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            line_indent = len(line) - len(line.lstrip())
            
            if line_indent < current_indent:
                # Found a parent level
                key_match = re.search(r'^(\w+):', stripped)
                if key_match:
                    parents.insert(0, key_match.group(1))
                    current_indent = line_indent
                    
        return parents