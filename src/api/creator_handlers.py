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
_OUTPUTS = _BASE / "task" / "novel" / "outputs"


def _project_dir(project_id: str) -> Path:
    pid = (project_id or "完美之墙").strip() or "完美之墙"
    return _OUTPUTS / pid


def list_projects() -> list:
    """返回已创作小说列表：outputs 下存在 novel_plan.json 的目录名（project_id）。"""
    if not _OUTPUTS.exists():
        return []
    out = []
    for p in _OUTPUTS.iterdir():
        if p.is_dir() and (p / "novel_plan.json").exists():
            out.append(p.name)
    return sorted(out)


def get_project_chapters(project_id: Optional[str] = None) -> Tuple[int, Optional[list]]:
    """
    返回当前作品的章节列表（含标题、是否已写）。
    Returns: (code, None) 表示无大纲；(0, [ { number, title, summary?, has_file }, ... ]) 表示成功。
    """
    pid = (project_id or "完美之墙").strip() or "完美之墙"
    root = _project_dir(pid)
    plan_file = root / "novel_plan.json"
    chapters_dir = root / "chapters"
    if not plan_file.exists():
        return 1, None
    try:
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        logger.warning("get_project_chapters load plan failed: %s", e)
        return 1, None
    co = plan.get("chapter_outline") or (plan.get("plan") or {}).get("chapter_outline")
    if not isinstance(co, list):
        return 0, []
    existing_files = set()
    if chapters_dir.exists():
        for f in chapters_dir.glob("chapter_*.txt"):
            try:
                suffix = f.stem.replace("chapter_", "").strip()
                if suffix.isdigit():
                    existing_files.add(int(suffix))
            except Exception:
                pass
    out = []
    for i, ch in enumerate(co):
        if not isinstance(ch, dict):
            continue
        num = ch.get("chapter_number", i + 1)
        title = ch.get("title") or f"第{num}章"
        summary = ch.get("summary") or ""
        out.append({
            "number": num,
            "title": title,
            "summary": summary[:200] if summary else "",
            "has_file": num in existing_files,
        })
    return 0, out


def _default_llm():
    """创作（规划/续写/润色/对话）使用的 LLM，由 config.NOVEL_LLM_MODEL 决定，默认 kimi-k2-5。"""
    from config import NOVEL_LLM_MODEL
    from llm.chat import CHAT_MODELS, chat_model_key
    key = chat_model_key(NOVEL_LLM_MODEL)
    if key in CHAT_MODELS:
        return CHAT_MODELS[key][0]
    from llm.deepseek import deepseek_v3_2
    logger.warning("NOVEL_LLM_MODEL=%s 未注册，回退到 deepseek_v3_2", NOVEL_LLM_MODEL)
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


def _load_previous_volume_context(previous_project_id: str) -> Optional[Dict[str, Any]]:
    """
    加载前卷项目的接续上下文，供第二卷大纲生成使用。
    包含：背景、人物、主线、结尾摘要、未解决伏笔、最后几章内容摘要。
    """
    root = _project_dir(previous_project_id.strip())
    plan_file = root / "novel_plan.json"
    chapters_dir = root / "chapters"
    mesh_file = root / "semantic_mesh" / "mesh.json"
    if not plan_file.exists():
        logger.warning("前卷 novel_plan.json 不存在: %s", plan_file)
        return None
    try:
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        logger.warning("读取前卷大纲失败: %s", e)
        return None
    co = plan.get("chapter_outline") or (plan.get("plan") or {}).get("chapter_outline")
    if not isinstance(co, list):
        co = []
    overall = plan.get("overall") or {}
    # 最后几章大纲摘要（用于接续）
    last_n = min(5, len(co))
    last_outline_summaries = []
    for i in range(-last_n, 0):
        if i + len(co) >= 0:
            ch = co[i]
            if isinstance(ch, dict):
                num = ch.get("chapter_number", len(co) + i + 1)
                title = ch.get("title") or f"第{num}章"
                summary = (ch.get("summary") or "")[:300]
                last_outline_summaries.append(f"第{num}章《{title}》：{summary}")
    # 若存在章节文件，取最后 2 章正文前段作为「当前状态」
    end_state_snippets = []
    if chapters_dir.exists():
        existing = sorted(
            [f for f in chapters_dir.glob("chapter_*.txt") if f.stem.replace("chapter_", "").strip().isdigit()],
            key=lambda f: int(f.stem.replace("chapter_", "").strip()),
        )
        for f in existing[-2:]:
            try:
                text = f.read_text(encoding="utf-8")[:500].strip()
                if text:
                    end_state_snippets.append(text)
            except Exception as e:
                logger.debug("读取前卷章节片段失败 %s: %s", f.name, e)
    # 语义网格关键实体（简要）
    mesh_summary = ""
    if mesh_file.exists():
        try:
            with open(mesh_file, "r", encoding="utf-8") as f:
                mesh_data = json.load(f)
            nodes = mesh_data.get("nodes") or mesh_data.get("entities") or []
            names = [n.get("name") or n.get("label") or str(n) for n in nodes[:30] if isinstance(n, dict)]
            if names:
                mesh_summary = "关键实体（前卷）：" + "、".join(names[:20])
        except Exception as e:
            logger.debug("读取前卷 semantic_mesh 失败: %s", e)
    return {
        "previous_project_id": previous_project_id.strip(),
        "background": plan.get("background") or overall.get("background", ""),
        "characters": plan.get("characters") or overall.get("characters", []),
        "main_plot": plan.get("main_plot") or overall.get("main_plot", ""),
        "key_plot_points": plan.get("key_plot_points", []),
        "ending_direction": plan.get("ending_direction") or overall.get("ending_direction", ""),
        "last_chapters_outline": "\n".join(last_outline_summaries) if last_outline_summaries else "",
        "end_state_snippets": "\n\n".join(end_state_snippets) if end_state_snippets else "",
        "semantic_mesh_summary": mesh_summary,
    }


def run_create(
    mode: str,
    raw_input: str,
    project_id: Optional[str] = None,
    previous_project_id: Optional[str] = None,
    start_chapter: Optional[int] = None,
    target_chapters: Optional[int] = None,
    on_event: Optional[Any] = None,
) -> Tuple[int, str, Optional[Dict]]:
    """
    执行「大纲」：创建小说大纲。
    - 若未接续前卷：根据输入用 LLM 解析书名作为 project_id，target_chapters 默认 20。
    - 若接续前卷：previous_project_id 必填；project_id 为本卷作品名（如 完美之墙_第二卷）；
      start_chapter 为本卷起始章号（如 101），target_chapters 为本卷章数（如 100）。
    Returns: (code, message, extra)
    """
    _ensure_sys_path()
    genre = "科幻"
    theme = raw_input.strip() or "完美之墙"
    m = re.search(r"主题[：:]\s*([^\n]+)", theme)
    if m:
        theme = m.group(1).strip()
    if not theme:
        theme = "完美之墙"

    is_continuation = bool(previous_project_id and previous_project_id.strip())
    if is_continuation:
        # 接续前卷：本卷作品名必填或从前卷推导
        new_id = (project_id or "").strip()
        if not new_id:
            new_id = _sanitize_project_id(previous_project_id.strip() + "_第二卷", max_len=24)
        project_id = new_id
        start_ch = 1 if start_chapter is None else max(1, int(start_chapter))
        target_ch = 100 if target_chapters is None else max(1, int(target_chapters))
        prev_ctx = _load_previous_volume_context(previous_project_id)
        if not prev_ctx:
            return 1, "加载前卷失败，请确认前卷作品存在且包含 novel_plan.json", None
        logger.info("run_create 接续前卷: previous=%r, project_id=%r, start_chapter=%s, target_chapters=%s",
                    previous_project_id, project_id, start_ch, target_ch)
    else:
        # 新作：LLM 解析书名
        llm = _default_llm()
        project_id = _extract_novel_title(theme, llm)
        start_ch = 1
        target_ch = 20 if target_chapters is None else max(1, int(target_chapters))
        prev_ctx = None
        logger.info("run_create: theme=%r -> project_id=%r", theme[:80], project_id)

    try:
        from task.novel.react_novel_creator import ReactNovelCreator

        llm = _default_llm()
        creator = ReactNovelCreator(
            novel_title=project_id,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_quality_check=False,
            llm_client=llm,
        )
        extra_memory = ""
        try:
            from api.memory_handlers import recall_from_evermemos
            items = recall_from_evermemos(
                project_id,
                "风格 主题 类型 过往创作 大纲",
                top_k=5,
                memory_types=["episodic_memory"],
            )
            if items:
                extra_memory = "\n".join((x.get("content") or "").strip() for x in items if x.get("content"))
        except Exception as ex:
            logger.debug("EverMemOS recall for plan skipped: %s", ex)
        plan = creator.create_novel_plan(
            genre=genre,
            theme=theme,
            target_chapters=target_ch,
            words_per_chapter=2048,
            previous_volume_context=prev_ctx,
            start_chapter=start_ch,
            on_event=on_event,
            extra_memory_context=extra_memory or None,
        )
        # 生成简短摘要供前端展示
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
        try:
            from api.memory_handlers import retain_plan_to_unimem
            retain_plan_to_unimem(project_id, content)
        except Exception as ex:
            logger.warning("UniMem retain plan failed: %s", ex)
        try:
            from api.memory_handlers import retain_plan_to_evermemos
            retain_plan_to_evermemos(project_id, content)
        except Exception as ex:
            logger.warning("EverMemOS retain plan failed: %s", ex)
        return 0, "创作成功", {"content": content, "mode": "create", "project_id": project_id}
    except Exception as e:
        logger.exception("run_create failed")
        return 1, f"创作失败：{str(e)}", None


def run_continue(mode: str, raw_input: str, project_id: Optional[str] = None, on_event: Optional[Any] = None) -> Tuple[int, str, Optional[Dict]]:
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
    existing_nums = []
    for f in existing:
        try:
            suffix = f.stem.replace("chapter_", "").strip()
            if suffix.isdigit():
                existing_nums.append(int(suffix))
        except Exception:
            pass
    start_chapter = plan.get("start_chapter", 1)
    # 下一章号：有文件则 max+1，否则用 start_chapter（多卷时为本卷起始章，如 101）
    next_num = (max(existing_nums) + 1) if existing_nums else start_chapter
    # 大纲索引：本卷内第几章（0-based），多卷时 co 仅含本卷 100 章
    outline_index = next_num - start_chapter
    if outline_index < 0 or outline_index >= len(co):
        return 1, "已写完所有大纲章节", None

    ch = co[outline_index]
    if not isinstance(ch, dict):
        return 1, "大纲章节格式异常", None
    # 使用大纲中的章节号（多卷时为 101、102…），用于正文与文件名
    chapter_number = ch.get("chapter_number", next_num)
    title = ch.get("title") or f"第{chapter_number}章"
    summary = ch.get("summary") or ""

    prev_summary = ""
    if outline_index > 0 and isinstance(co[outline_index - 1], dict):
        prev_summary = co[outline_index - 1].get("summary") or ""

    try:
        from task.novel.react_novel_creator import ReactNovelCreator

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
                from context import SemanticMeshMemory
                with open(mesh_file, "r", encoding="utf-8") as f:
                    mesh_data = json.load(f)
                mesh = SemanticMeshMemory()
                mesh.from_dict(mesh_data)
                creator.semantic_mesh = mesh
            except Exception as ex:
                logger.warning("Could not load semantic mesh for continue: %s", ex)

        extra_memory = ""
        try:
            from api.memory_handlers import recall_from_evermemos
            items = recall_from_evermemos(
                project_id,
                "前文 情节 人物 大纲 本章摘要 角色",
                top_k=5,
                memory_types=["episodic_memory"],
            )
            if items:
                extra_memory = "\n".join((x.get("content") or "").strip() for x in items if x.get("content"))
        except Exception as ex:
            logger.debug("EverMemOS recall for continue skipped: %s", ex)
        chapter = creator.create_chapter(
            chapter_number=chapter_number,
            chapter_title=title,
            chapter_summary=summary,
            previous_chapters_summary=prev_summary or None,
            target_words=2048,
            on_event=on_event,
            extra_memory_context=extra_memory or None,
        )
        content = (chapter.content or "").strip()
        try:
            from api.memory_handlers import retain_chapter_to_unimem
            retain_chapter_to_unimem(project_id, chapter_number, content)
        except Exception as ex:
            logger.warning("UniMem retain chapter failed: %s", ex)
        try:
            from api.memory_handlers import retain_chapter_to_evermemos
            retain_chapter_to_evermemos(project_id, chapter_number, content)
        except Exception as ex:
            logger.warning("EverMemOS retain chapter failed: %s", ex)
        return 0, "续写成功", {"content": content, "mode": "continue", "project_id": project_id, "chapter_number": chapter_number}
    except Exception as e:
        logger.exception("run_continue failed")
        return 1, f"续写失败：{str(e)}", None


def run_polish(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """
    润色用户输入片段。若提供 project_id，会注入该项目云端记忆（风格/润色偏好）以保持一致。
    """
    _ensure_sys_path()
    text = raw_input.strip()
    if not text:
        return 1, "请输入要润色的内容", None

    sys_msg = "你负责润色用户给出的片段，提升可读性与文采，保持原意不变。只输出润色后的正文，不要解释。"
    pid = (project_id or "").strip()
    if pid:
        try:
            from api.memory_handlers import recall_from_evermemos
            items = recall_from_evermemos(pid, "风格 语气 润色偏好 用词", top_k=5)
            if items:
                extra = "\n".join((x.get("content") or "").strip() for x in items if x.get("content"))
                if extra:
                    sys_msg += f"\n\n参考本项目过往风格与润色偏好：\n{extra[:1500]}"
        except Exception as ex:
            logger.debug("EverMemOS recall for polish skipped: %s", ex)
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": text}]
    try:
        llm = _default_llm()
        _, content = llm(messages, max_new_tokens=4096)
        content = (content or "").strip()
        if pid and content:
            try:
                from api.memory_handlers import retain_polish_to_evermemos
                retain_polish_to_evermemos(pid, text, content)
            except Exception as ex:
                logger.warning("EverMemOS retain polish failed: %s", ex)
        return 0, "润色成功", {"content": content, "mode": "polish"}
    except Exception as e:
        logger.exception("run_polish failed")
        return 1, f"润色失败：{str(e)}", None


def run_chat(mode: str, raw_input: str, project_id: Optional[str] = None) -> Tuple[int, str, Optional[Dict]]:
    """
    创作助手对话。若提供 project_id，会注入该项目云端记忆（设定/偏好/大纲/人物）以增强回复相关性。
    """
    _ensure_sys_path()
    text = raw_input.strip()
    if not text:
        return 1, "请输入内容", None

    sys_msg = "你是一位多智能体协作的创作助手，可讨论大纲、人物、情节与写作技巧。简洁专业。"
    pid = (project_id or "").strip()
    if pid:
        try:
            from api.memory_handlers import recall_from_evermemos
            items = recall_from_evermemos(pid, "对话 偏好 设定 大纲 人物", top_k=5)
            if items:
                extra = "\n".join((x.get("content") or "").strip() for x in items if x.get("content"))
                if extra:
                    sys_msg += f"\n\n当前项目相关记忆（供参考）：\n{extra[:1500]}"
        except Exception as ex:
            logger.debug("EverMemOS recall for chat skipped: %s", ex)
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": text}]
    try:
        llm = _default_llm()
        _, content = llm(messages, max_new_tokens=2048)
        content = (content or "").strip()
        if pid and content:
            try:
                from api.memory_handlers import retain_chat_to_evermemos
                retain_chat_to_evermemos(pid, text, content)
            except Exception as ex:
                logger.warning("EverMemOS retain chat failed: %s", ex)
        return 0, "回复成功", {"content": content, "mode": "chat"}
    except Exception as e:
        logger.exception("run_chat failed")
        return 1, f"对话失败：{str(e)}", None


def run(
    mode: str,
    raw_input: str,
    project_id: Optional[str] = None,
    previous_project_id: Optional[str] = None,
    start_chapter: Optional[int] = None,
    target_chapters: Optional[int] = None,
    on_event: Optional[Any] = None,
) -> Tuple[int, str, Optional[Dict]]:
    """统一入口。create 模式可传 previous_project_id、start_chapter、target_chapters 用于接续前卷。on_event 用于 P1 编排事件推送。"""
    mode_key = (mode or "").strip().lower()
    if mode_key == "create":
        return run_create(
            mode, raw_input, project_id=project_id,
            previous_project_id=previous_project_id,
            start_chapter=start_chapter,
            target_chapters=target_chapters,
            on_event=on_event,
        )
    if mode_key in ("continue", "polish", "chat"):
        h = {"continue": run_continue, "polish": run_polish, "chat": run_chat}[mode_key]
        if mode_key == "continue":
            return run_continue(mode, raw_input, project_id, on_event=on_event)
        return h(mode, raw_input, project_id)
    return 1, f"不支持的 mode：{mode}", None
