import importlib, importlib.metadata as md

def test_can_import_top_level():
    pkg = importlib.import_module("strataregula_lsp")
    assert pkg is not None

def test_version_metadata_present_or_absent_but_safe():
    # 配布名/モジュール名どちらも試す。無くてもテストは通す（存在すれば文字列であることを確認）
    for name in ("strataregula-lsp", "strataregula_lsp"):
        try:
            v = md.version(name)
            assert isinstance(v, str)
            return
        except Exception:
            pass
    pkg = importlib.import_module("strataregula_lsp")
    v = getattr(pkg, "__version__", None)
    assert v is None or isinstance(v, str)
