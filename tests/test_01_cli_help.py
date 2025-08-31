import importlib.util, subprocess, sys, pytest

spec = importlib.util.find_spec("strataregula_lsp.__main__")

@pytest.mark.skipif(spec is None, reason="no __main__ module")
def test_module_help_runs():
    p = subprocess.run(
        [sys.executable, "-m", "strataregula_lsp", "--help"],
        capture_output=True, text=True, timeout=15
    )
    # argparseなら --help は通常 0 終了
    assert p.returncode == 0
