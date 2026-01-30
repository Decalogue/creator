"""
创作 API 逻辑：create / continue / polish / chat

- create: create_novel_plan，返回大纲摘要
- continue: 根据已有 project 续写下一章，返回章节正文
- polish: LLM 润色用户输入
- chat: 创作助手对话（通用 LLM）
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import json
import logging
import re

logger = logging.getLogger(__name__)

_BASE = Path(__file__).resolve().parent.parent
_OUTPUTS = _BASE / "novel_creation" / "outputs"


def _project_dir(project_id: str) -> Path:
    pid = (project_id or "完美之墙").strip() or "完美之墙"
    return _OUTPUTS / pid


def _default_llm():
    from llm.deepseek import deepseek_v3_2
    return deepseek_v3_2


def _sanitize_project_id(name: str, max_len: int = 20) -> str:
    """将 LLM 返回的书名整理为可作目录名的 project_id。"""
    if not name or not isinstance(name, str):
        return "未命名小说"
    s = name.strip().strip('"\'「」『』').replace("\n", " ").replace("\r", "")
    for c in '/\\:*?"<>|':
        s = s.replace(c, "_")
    s = s[:max_len].strip() or "未命名小说"
    return s


def _extract_novel_title(theme: str, llm) -> str:
    """
    使用 LLM 根据创作意图解析出小说书名（用于 project_id）。
    只输出书名，2–12 字，便于做目录名。
    """
    if not theme or not theme.strip():
        return "未命名小说"
    prompt = (
        "根据以下创作意图，提取或生成一个简短的小说书名（2–12 个字，仅用于项目标识）。"
        "只输出书名，不要引号、不要解释、不要换行。\n\n创作意图：\n"
    ) + theme.strip()[:500]
    try:
        _, content = llm(
            [{"role": "user", "content": prompt}],
            max_new_tokens=64,
        )
        return _sanitize_project_id((content or "").strip())
    except Exception as e:
        logger.warning("LLM 解析书名失败，使用主题前段: %s", e)
    fallback = theme.strip()[:20].strip()
    for c in '/\\:*?"<>|':
        fallback = fallback.replace(c, "_")
    return fallback[:20] or "未命名小说"


def _ensure_sys_path():
    import sys
    base = _BASE
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))


def run_create(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """
    执行「大纲」：创建小说大纲。
    若未传 project_id，则用 LLM 根据输入解析出小说书名作为 project_id。
    Returns: (code, message, extra)
    """
    _ensure_sys_path()
    genre = "科幻"
    theme = raw_input.strip() or "完美之墙"
    ***REMOVED*** 简单解析：主题：XXX
    m = re.search(r"主题[：:]\s*([^\n]+)", theme)
    if m:
        theme = m.group(1).strip()
    if not theme:
        theme = "完美之墙"

    ***REMOVED*** 大纲模式始终根据用户输入用 LLM 解析书名，忽略传入的 project_id
    llm = _default_llm()
    project_id = _extract_novel_title(theme, llm)
    logger.info("run_create: theme=%r -> project_id=%r", theme[:80], project_id)

    try:
        from novel_creation.react_novel_creator import ReactNovelCreator

        llm = _default_llm()
        creator = ReactNovelCreator(
            novel_title=project_id,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_quality_check=False,
            llm_client=llm,
        )
        plan = creator.create_novel_plan(
            genre=genre,
            theme=theme,
            target_chapters=20,
            words_per_chapter=2048,
        )
        ***REMOVED*** 生成简短摘要供前端展示
        lines = []
        if isinstance(plan, dict):
            bg = plan.get("background") or plan.get("overall", {}).get("background") if isinstance(plan.get("overall"), dict) else None
            if bg:
                lines.append(f"背景：{str(bg)[:200]}…")
            co = plan.get("chapter_outline") or (plan.get("plan") or {}).get("chapter_outline") if isinstance(plan.get("plan"), dict) else []
            if isinstance(co, list) and co:
                for i, ch in enumerate(co[:5]):
                    if isinstance(ch, dict):
                        t = ch.get("title") or ch.get("summary", "")[:30]
                        lines.append(f"第{ch.get('chapter_number', i+1)}章：{t}")
        content = "\n".join(lines) if lines else json.dumps(plan, ensure_ascii=False)[:1500]
        return 0, "创作成功", {"content": content, "mode": "create", "project_id": project_id}
    except Exception as e:
        logger.exception("run_create failed")
        return 1, f"创作失败：{str(e)}", None


def run_continue(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """
    执行「续写」：写下一章。
    Returns: (code, message, extra)
    """
    _ensure_sys_path()
    project_id = (project_id or "完美之墙").strip() or "完美之墙"
    root = _project_dir(project_id)
    plan_file = root / "novel_plan.json"
    metadata_file = root / "metadata.json"
    mesh_file = root / "semantic_mesh" / "mesh.json"
    chapters_dir = root / "chapters"

    if not plan_file.exists():
        return 1, "尚未创建大纲，请先使用「创作」生成大纲", None

    try:
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        return 1, f"读取大纲失败：{e}", None

    co = plan.get("chapter_outline") or (plan.get("plan") or {}).get("chapter_outline")
    if not isinstance(co, list):
        return 1, "大纲中无章节信息", None

    existing = list(chapters_dir.glob("chapter_*.txt")) if chapters_dir.exists() else []
    next_num = len(existing) + 1
    if next_num > len(co):
        return 1, "已写完所有大纲章节", None

    ch = co[next_num - 1]
    if not isinstance(ch, dict):
        return 1, "大纲章节格式异常", None
    title = ch.get("title") or f"第{next_num}章"
    summary = ch.get("summary") or ""

    prev_summary = ""
    if next_num > 1 and isinstance(co[next_num - 2], dict):
        prev_summary = co[next_num - 2].get("summary") or ""

    try:
        from novel_creation.react_novel_creator import ReactNovelCreator

        llm = _default_llm()
        creator = ReactNovelCreator(
            novel_title=project_id,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_quality_check=False,
            llm_client=llm,
        )
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                creator.metadata = json.load(f)
        if not creator.metadata.get("plan"):
            creator.metadata["plan"] = plan
        if mesh_file.exists():
            try:
                from creative_context import SemanticMeshMemory
                with open(mesh_file, "r", encoding="utf-8") as f:
                    mesh_data = json.load(f)
                mesh = SemanticMeshMemory()
                mesh.from_dict(mesh_data)
                creator.semantic_mesh = mesh
            except Exception as ex:
                logger.warning("Could not load semantic mesh for continue: %s", ex)

        chapter = creator.create_chapter(
            chapter_number=next_num,
            chapter_title=title,
            chapter_summary=summary,
            previous_chapters_summary=prev_summary or None,
            target_words=2048,
        )
        content = (chapter.content or "").strip()
        return 0, "续写成功", {"content": content, "mode": "continue", "project_id": project_id, "chapter_number": next_num}
    except Exception as e:
        logger.exception("run_continue failed")
        return 1, f"续写失败：{str(e)}", None


def run_polish(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """
    润色用户输入片段。
    """
    _ensure_sys_path()
    text = raw_input.strip()
    if not text:
        return 1, "请输入要润色的内容", None

    sys_msg = "你负责润色用户给出的片段，提升可读性与文采，保持原意不变。只输出润色后的正文，不要解释。"
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": text}]
    try:
        llm = _default_llm()
        _, content = llm(messages, max_new_tokens=4096)
        content = (content or "").strip()
        return 0, "润色成功", {"content": content, "mode": "polish"}
    except Exception as e:
        logger.exception("run_polish failed")
        return 1, f"润色失败：{str(e)}", None


def run_chat(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """
    创作助手对话。
    """
    _ensure_sys_path()
    text = raw_input.strip()
    if not text:
        return 1, "请输入内容", None

    sys_msg = "你是一位多智能体协作的创作助手，可讨论大纲、人物、情节与写作技巧。简洁专业。"
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": text}]
    try:
        llm = _default_llm()
        _, content = llm(messages, max_new_tokens=2048)
        content = (content or "").strip()
        return 0, "回复成功", {"content": content, "mode": "chat"}
    except Exception as e:
        logger.exception("run_chat failed")
        return 1, f"对话失败：{str(e)}", None


def run(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """统一入口."""
    handlers = {"create": run_create, "continue": run_continue, "polish": run_polish, "chat": run_chat}
    h = handlers.get((mode or "").strip().lower())
    if not h:
        return 1, f"不支持的 mode：{mode}", None
    return h(mode, raw_input, project_id)
