import os, re, types, pathlib, pkgutil, importlib

# 万一の起動系副作用を止めるためのおまじない（コード側で見ていなくても無害）
os.environ.setdefault("STRATAREGULA_TESTING", "1")
os.environ.setdefault("SR_NO_STARTUP", "1")

SKIP_PAT = re.compile(r"\b(__main__|cli|bin|server|app|run)\b")

def iter_submodules():
    import strataregula_lsp as pkg
    pkg_dir = pathlib.Path(pkg.__file__).parent
    for mod in pkgutil.walk_packages([str(pkg_dir)], prefix=pkg.__name__ + "."):
        if SKIP_PAT.search(mod.name):
            continue
        yield mod.name

def test_import_all_submodules():
    for name in iter_submodules():
        m = importlib.import_module(name)
        assert isinstance(m, types.ModuleType)
