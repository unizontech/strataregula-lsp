# Contributing

- PR は小さく、1 PR = 1 目的。
- `docs/run/*.md` に記録する Runログの Summary は必ず非空にしてください。
- CI must be green before merging.

Thank you for your interest in contributing to StrataRegula Language Server Protocol implementation!

## Development Setup

### Prerequisites
- Python 3.8+ (LSP server compatibility)
- Git
- Knowledge of Language Server Protocol specification
- Optional: VS Code or other LSP-capable editor for testing

### Setup
```bash
git clone https://github.com/strataregula/strataregula-lsp.git
cd strataregula-lsp
pip install -e ".[dev]"
```

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow LSP protocol specifications
   - Implement handlers in `strataregula_lsp/handlers/`
   - Update analyzers in `strataregula_lsp/analyzer/`
   - Add provider logic in `strataregula_lsp/providers/`

3. **Test Changes**
   ```bash
   # Unit tests
   pytest tests/
   
   # Run with coverage
   pytest --cov=strataregula_lsp
   
   # Type checking
   mypy strataregula_lsp/
   
   # Code formatting
   black strataregula_lsp/ tests/
   ruff check strataregula_lsp/ tests/
   ```

4. **Manual Testing**
   ```bash
   # Start LSP server manually
   python -m strataregula_lsp.server
   
   # Test with VS Code extension
   # Test with other LSP clients (vim, emacs, etc.)
   ```

5. **Submit Pull Request**

## Code Style

- **Python**: Black formatting + ruff linting
- **Type Hints**: Full type annotation required
- **Async/Await**: Proper async patterns for LSP operations
- **Protocol Compliance**: Strict adherence to LSP specification

## LSP Architecture

### Core Components
- **`server.py`**: Main LSP server implementation using pygls
- **`handlers/`**: LSP method handlers (completion, hover, diagnostics, etc.)
- **`analyzer/`**: YAML pattern analysis and tokenization
- **`providers/`**: Data providers for LSP features

### LSP Method Implementations

#### Text Document Methods
- **`textDocument/completion`**: Pattern-aware auto-completion
- **`textDocument/hover`**: Documentation and help text
- **`textDocument/definition`**: Go-to-definition for patterns
- **`textDocument/references`**: Find all pattern references
- **`textDocument/formatting`**: YAML formatting
- **`textDocument/diagnostics`**: Validation and error reporting

#### Workspace Methods
- **`workspace/symbol`**: Workspace-wide symbol search
- **`workspace/didChangeConfiguration`**: Configuration updates

### Pattern Analysis Engine

The LSP server provides intelligent YAML analysis:
- **Pattern Recognition**: Identify StrataRegula-specific patterns
- **Context Awareness**: Understand hierarchical YAML structure
- **Validation**: Real-time syntax and semantic validation
- **Completion**: Smart auto-completion based on context

## Testing

### Unit Tests
```bash
# Run all tests
pytest

# Test specific handler
pytest tests/handlers/test_completion.py

# Test with coverage
pytest --cov=strataregula_lsp --cov-report=html
```

### Integration Testing
- Test with actual LSP clients (VS Code, vim, emacs)
- Verify protocol compliance using LSP testing tools
- Test with various YAML configuration patterns

### Manual Testing Scenarios
- [ ] Start server and connect from LSP client
- [ ] Auto-completion works in YAML files
- [ ] Hover provides helpful documentation
- [ ] Diagnostics show validation errors
- [ ] Go-to-definition works for pattern references
- [ ] Formatting preserves YAML structure

## LSP Protocol Compliance

### Capabilities
The server advertises these capabilities:
- **Completion**: Context-aware suggestions
- **Hover**: Documentation on demand
- **Definition**: Pattern definition lookup
- **References**: Find pattern usage
- **Formatting**: YAML structure preservation
- **Diagnostics**: Real-time validation

### Message Handling
- Proper JSON-RPC 2.0 message handling
- Error responses with appropriate codes
- Progress reporting for long operations
- Cancellation support for async operations

## Performance Considerations

### Optimization Guidelines
- **Async Operations**: Non-blocking LSP message handling
- **Incremental Updates**: Process only changed text regions
- **Caching**: Cache parsed YAML structures and analysis
- **Memory Management**: Efficient pattern storage and lookup

### Performance Testing
```bash
# Profile LSP server performance
python -m cProfile -o lsp_profile.prof -m strataregula_lsp.server

# Analyze memory usage
python -m memory_profiler strataregula_lsp/server.py
```

## Advanced Development

### Pattern Provider System
- **Dynamic Pattern Loading**: Load patterns from StrataRegula core
- **Context Sensitivity**: Provide relevant completions based on YAML context
- **Schema Validation**: Integrate with StrataRegula schema validation

### Error Handling
- **Graceful Degradation**: Handle malformed YAML gracefully
- **Error Recovery**: Continue operation despite parsing errors
- **Client Communication**: Proper error reporting to LSP clients

## Quality Standards

- **Protocol Compliance**: 100% LSP specification adherence
- **Type Safety**: Complete type annotation with mypy
- **Test Coverage**: ≥90% code coverage
- **Performance**: Response times <100ms for common operations
- **Reliability**: Robust error handling and recovery

## Documentation

Link to detailed developer documentation: [docs/README_FOR_DEVELOPERS.md](docs/README_FOR_DEVELOPERS.md)

### LSP Implementation Notes
- Based on `pygls` (Python Generic Language Server)
- Integrates with `strataregula` core for pattern analysis
- Supports both VS Code extension and standalone LSP clients

## License

By contributing, you agree that your contributions will be licensed under MIT License.