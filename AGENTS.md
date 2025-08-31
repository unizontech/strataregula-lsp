# AGENTS

自動化エージェントの責務・手順・Runログ様式を定義します。

## 共通原則
- **1 PR = 1 目的**
- **Runログは必ず作成**（Summary は非空、JSTで保存）

## Run Log Agent
- 目的: コマンド実行結果を `docs/run/*.md` に記録して可観測性を高める
- 優先度:
  1) `scripts/new_run_log.py` がある場合（例: world-simulation）
  2) 無ければ `tools/runlog.py`（軽量版）
  3) さらに無ければ `tools/runlog.sh`

### 使い方
```bash
# Python (軽量版)
python tools/runlog.py \
  --label smoke \
  --summary "smoke for cli/tests" \
  --intent "verify unified env works"

# シェル版（最短）
./tools/runlog.sh smoke "smoke for cli/tests" "verify unified env works"
```

## LSP Protocol Agent
- 目的: Language Server Protocol準拠の自動化とプロトコル検証
- プロトコル検証: LSP仕様への完全準拠チェック
- クライアント互換性: VS Code、Neovim、Emacs等との動作確認

### 使い方
```bash
# LSPサーバー起動
python -m strataregula_lsp --stdio

# プロトコル準拠テスト
python -m strataregula_lsp.test --protocol-compliance

# クライアント互換性テスト
python -m strataregula_lsp.test --client vscode --client neovim
```

## Language Server Performance Agent
- 目的: 言語サーバーのレスポンス時間とメモリ使用量の監視
- パフォーマンス測定: リアルタイム応答性とリソース効率
- 最適化提案: ボトルネック特定と改善案提示

### 使い方
```bash
# パフォーマンス測定
python -m strataregula_lsp.bench --measure-latency --measure-memory

# ボトルネック分析
python -m strataregula_lsp.profiler --trace-requests --output profile.json

# 最適化検証
python -m strataregula_lsp.bench --compare-baseline --threshold 10ms
```

## ログサンプル（JST）

```markdown
# Run Log - lsp-protocol-test
- When: 2025-08-30T20-00JST
- Repo: strataregula-lsp
- Summary: LSP protocol compliance and performance validation

## Intent
ensure LSP server meets protocol standards and performance requirements

## Commands
python -m strataregula_lsp.test --protocol-compliance --verbose
python -m strataregula_lsp.bench --measure-all --baseline v1.0.0

## Results
- LSP protocol compliance: 98% (2 minor warnings)
- average response time: 15ms (target: <20ms)
- memory usage: 45MB (stable over 1000 requests)
- VS Code integration: ✓ all features working

## Next actions
- address LSP protocol warnings
- optimize completion request handling  
- add performance regression tests
```

**タグ**: #automation #agents #runlog #lsp #protocol #performance
