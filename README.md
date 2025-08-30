> **開発者へ**: 作業開始前に必ず [docs/README_FOR_DEVELOPERS.md](docs/README_FOR_DEVELOPERS.md) を確認してください。

# StrataRegula Language Server Protocol (LSP)

Language Server Protocol implementation for StrataRegula YAML configuration pattern compiler.

## 🎯 Features

### Core LSP Capabilities
- **Document Synchronization**: Real-time tracking of document changes
- **Diagnostics**: Pattern validation and error reporting
- **Completion**: IntelliSense for wildcard patterns and configuration keys
- **Hover**: Documentation tooltips for patterns and values
- **Go to Definition**: Navigate to pattern definitions
- **Find References**: Locate all uses of a pattern
- **Document Symbols**: Outline view of configuration structure
- **Rename**: Safe refactoring of pattern names
- **Formatting**: Auto-format YAML configurations

### StrataRegula-Specific Features
- **Pattern Validation**: Real-time validation of wildcard patterns (`*`, `**`)
- **Pattern Expansion**: Preview expanded patterns in hover tooltips
- **Configuration Analysis**: Hierarchy conflict detection
- **Performance Hints**: Optimization suggestions for patterns
- **Live Compilation**: Real-time preview of compiled output

## 📦 Installation

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install StrataRegula CLI
pip install strataregula

# Verify installation
strataregula --version
```

### Install LSP Server
```bash
# From PyPI
pip install strataregula-lsp

# From source
git clone https://github.com/strataregula/strataregula-lsp
cd strataregula-lsp
pip install -e .
```

## 🚀 Usage

### Start LSP Server

#### Standard IO Mode (VS Code)
```bash
strataregula-lsp --stdio
```

#### TCP Mode (General Editors)
```bash
strataregula-lsp --tcp --port 8765
```

#### WebSocket Mode (Web-based Editors)
```bash
strataregula-lsp --ws --port 8765
```

### Configuration

Create `.strataregula.yaml` in your project root:

```yaml
lsp:
  # Validation settings
  validation:
    enabled: true
    on_save: true
    on_change: false  # Set to true for real-time validation
    
  # Completion settings
  completion:
    enabled: true
    include_snippets: true
    show_documentation: true
    
  # Formatting settings
  formatting:
    indent_size: 2
    quote_style: single  # single, double, or preserve
    
  # Performance settings
  performance:
    max_file_size: 10485760  # 10MB
    pattern_cache_size: 1000
    compilation_timeout: 5000  # ms
```

## 🔌 Editor Integration

### VS Code
Install the [StrataRegula VS Code Extension](https://github.com/strataregula/strataregula-vscode) which includes built-in LSP client configuration.

### Neovim
```lua
-- Using nvim-lspconfig
require'lspconfig'.strataregula_lsp.setup{
  cmd = {'strataregula-lsp', '--stdio'},
  filetypes = {'yaml', 'yml'},
  root_dir = require'lspconfig'.util.root_pattern('.strataregula.yaml', '.git'),
  settings = {
    strataregula = {
      validation = { enabled = true },
      completion = { enabled = true }
    }
  }
}
```

### Sublime Text
Install LSP package, then add to LSP settings:
```json
{
  "clients": {
    "strataregula-lsp": {
      "enabled": true,
      "command": ["strataregula-lsp", "--stdio"],
      "languages": [{
        "languageId": "yaml",
        "scopes": ["source.yaml"],
        "syntaxes": ["Packages/YAML/YAML.sublime-syntax"]
      }]
    }
  }
}
```

### Vim (with coc.nvim)
Add to `coc-settings.json`:
```json
{
  "languageserver": {
    "strataregula": {
      "command": "strataregula-lsp",
      "args": ["--stdio"],
      "filetypes": ["yaml"],
      "initializationOptions": {
        "validation": { "enabled": true },
        "completion": { "enabled": true }
      }
    }
  }
}
```

## 📊 Protocol Support

### LSP Version
- **Specification**: 3.17.0
- **Protocol**: JSON-RPC 2.0

### Supported Methods

#### Lifecycle
- ✅ `initialize`
- ✅ `initialized`
- ✅ `shutdown`
- ✅ `exit`

#### Document Synchronization
- ✅ `textDocument/didOpen`
- ✅ `textDocument/didChange`
- ✅ `textDocument/didSave`
- ✅ `textDocument/didClose`

#### Language Features
- ✅ `textDocument/completion`
- ✅ `textDocument/hover`
- ✅ `textDocument/definition`
- ✅ `textDocument/references`
- ✅ `textDocument/documentSymbol`
- ✅ `textDocument/rename`
- ✅ `textDocument/formatting`
- ✅ `textDocument/rangeFormatting`
- ✅ `textDocument/publishDiagnostics`
- 🚧 `textDocument/codeAction` (planned)
- 🚧 `textDocument/codeLens` (planned)

## 🛠️ Development

### Project Structure
```
strataregula-lsp/
├── strataregula_lsp/
│   ├── __init__.py
│   ├── server.py           # Main LSP server
│   ├── handlers/           # Request handlers
│   │   ├── __init__.py
│   │   ├── completion.py
│   │   ├── hover.py
│   │   ├── diagnostics.py
│   │   └── ...
│   ├── analyzer/           # YAML pattern analyzer
│   │   ├── __init__.py
│   │   ├── pattern.py
│   │   ├── validator.py
│   │   └── hierarchy.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
├── tests/
├── pyproject.toml
└── README.md
```

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/strataregula/strataregula-lsp
cd strataregula-lsp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Running Tests
```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# With coverage
pytest --cov=strataregula_lsp --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [StrataRegula](https://github.com/strataregula/strataregula) - Main YAML configuration compiler
- [StrataRegula VS Code](https://github.com/strataregula/strataregula-vscode) - VS Code extension

## 📚 Resources

- [Language Server Protocol Specification](https://microsoft.github.io/language-server-protocol/)
- [StrataRegula Documentation](https://github.com/strataregula/strataregula/docs)
- [Python LSP Libraries](https://github.com/openlawlibrary/pygls)

---

**StrataRegula LSP v0.1.0** - Intelligent YAML configuration pattern analysis and validation