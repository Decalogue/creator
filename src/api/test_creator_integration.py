"""
主路径集成测试：POST /api/creator/run (mode=create) 的 API 与任务轮询、产出目录校验。

不调用真实 LLM，通过 mock creator_run 使后台任务立即完成并写入 minimal novel_plan.json，
校验：1) 接口返回 task_id；2) 轮询得到 status=done、code=0；3) outputs/<project_id>/novel_plan.json 存在。

运行方式（在 src 目录下）：conda activate seeme && python -m pytest api/test_creator_integration.py -v
或在项目根目录：conda activate seeme && cd src && python -m pytest api/test_creator_integration.py -v
"""

import json
import shutil
import time
from pathlib import Path
from unittest.mock import patch

import pytest

***REMOVED*** 确保从 src 根可导入
_BASE = Path(__file__).resolve().parent.parent
_OUTPUTS = _BASE / "task" / "novel" / "outputs"
_TEST_PROJECT_ID = "test_e2e_integration"


def _mock_run_create(
    mode,
    raw_input,
    project_id=None,
    previous_project_id=None,
    start_chapter=None,
    target_chapters=None,
    on_event=None,
):
    """模拟 run(mode='create')：写入 minimal novel_plan.json 并返回成功。"""
    if mode != "create":
        return 1, "仅支持 create 模式", None
    pid = (project_id or _TEST_PROJECT_ID).strip() or _TEST_PROJECT_ID
    root = _OUTPUTS / pid
    root.mkdir(parents=True, exist_ok=True)
    plan_path = root / "novel_plan.json"
    minimal_plan = {
        "overall": {"title": pid, "genre": "测试"},
        "chapter_outline": [{"chapter_number": 1, "title": "第一章", "summary": "测试摘要"}],
    }
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(minimal_plan, f, ensure_ascii=False, indent=2)
    return 0, "创作成功", {"content": "测试大纲摘要", "mode": "create", "project_id": pid}


@pytest.fixture(autouse=True)
def _cleanup_test_project():
    yield
    if _OUTPUTS.exists():
        test_root = _OUTPUTS / _TEST_PROJECT_ID
        if test_root.exists():
            shutil.rmtree(test_root, ignore_errors=True)


def test_creator_run_create_contract_and_outputs():
    """主路径：POST /api/creator/run mode=create -> 轮询 task -> 校验 code=0 与 novel_plan.json 存在。"""
    try:
        from api_flask import app, _CREATOR_MEMORY_AVAILABLE
    except Exception as e:
        pytest.skip(f"api_flask 或 creator/memory 未就绪: {e}")
    if not _CREATOR_MEMORY_AVAILABLE:
        pytest.skip("创作/记忆服务未就绪（_CREATOR_MEMORY_AVAILABLE=False）")

    try:
        client = app.test_client()
    except Exception as e:
        pytest.skip(f"Flask test_client 不可用（如 werkzeug 版本）: {e}")

    with patch("api_flask.creator_run", side_effect=_mock_run_create):
        ***REMOVED*** 1) POST /api/creator/run
        rv = client.post(
            "/api/creator/run",
            json={"mode": "create", "input": "测试主题"},
            content_type="application/json",
        )
        assert rv.status_code == 200
        data = rv.get_json()
        assert data.get("code") == 0
        task_id = data.get("task_id")
        assert task_id

        ***REMOVED*** 2) 轮询 GET /api/creator/task/<task_id>
        for _ in range(30):
            tr = client.get(f"/api/creator/task/{task_id}")
            assert tr.status_code == 200
            out = tr.get_json()
            status = out.get("status")
            if status == "done":
                assert out.get("code") == 0
                assert out.get("project_id") == _TEST_PROJECT_ID
                break
            if status == "failed":
                pytest.fail(f"Task failed: {out.get('error')}")
            time.sleep(0.2)
        else:
            pytest.fail("Task did not complete within timeout")

        ***REMOVED*** 3) 校验 outputs/<project_id>/novel_plan.json 存在
        plan_path = _OUTPUTS / _TEST_PROJECT_ID / "novel_plan.json"
        assert plan_path.exists()
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
        assert "chapter_outline" in plan
