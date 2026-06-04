import json
from pathlib import Path


SUBMISSION_NOTEBOOKS = [
    Path("notebooks/02_agent_submission.ipynb"),
    Path("kaggle/submission/02_agent_submission.ipynb"),
]


def test_submission_notebooks_compile_and_define_cfg_before_use():
    for path in SUBMISSION_NOTEBOOKS:
        nb = json.loads(path.read_text())
        setup_source = "".join(nb["cells"][2]["source"])

        assert 'CFG = {' in setup_source
        assert setup_source.index("CFG = {") < setup_source.index("\nAGENT_VERSION =")
        assert 'EMBEDDED_AGENT_VERSION = \'roi_reserve_v3\'' in setup_source
        assert '"agent_version": "roi_reserve_v3"' in setup_source

        for index, cell in enumerate(nb["cells"], start=1):
            if cell.get("cell_type") != "code":
                continue
            compile("".join(cell.get("source", [])), f"{path}:cell-{index}", "exec")
