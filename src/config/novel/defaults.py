"""
小说创作默认配置：字数、节奏、对话占比、token 限制等。

供 task.novel 使用，集中管理便于调整与复用。
"""

# 默认字数
DEFAULT_TARGET_WORDS = 3000
DEFAULT_WORDS_PER_CHAPTER = 3000

# Token 限制（生成时至少保留）
MIN_TOKEN_LIMIT = 2048
TOKEN_WORDS_FACTOR = 1.5  # base_max_tokens = max(MIN_TOKEN_LIMIT, int(target_words * TOKEN_WORDS_FACTOR))

# 章节位置字数调整（节奏优化）
POSITION_ADJUSTMENTS = {
    "opening": 0.95,  # 开头稍短
    "development": 1.0,
    "climax": 1.15,  # 高潮可更长
    "ending": 0.90,  # 结尾稍短
}

# 节奏调整允许范围（相对基础字数）
WORD_RANGE_MIN = 0.8
WORD_RANGE_MAX = 1.2

# 目标字数容忍范围（创作/重写时的理想范围）
WORD_TARGET_TOLERANCE_MIN = 0.9
WORD_TARGET_TOLERANCE_MAX = 1.1

# 对话占比（质量要求）
DIALOGUE_RATIO_MIN = 0.20  # 20%
DIALOGUE_RATIO_MAX = 0.40  # 40%

# 字数超限时的截断策略
STRICT_CUTOFF_FACTOR = 1.20  # 超过目标*1.2 触发截断
TRUNCATE_AFTER_FACTOR = 1.15  # 截断到目标*1.15
MIN_ACCEPTABLE_WORDS_FACTOR = 0.5  # 最少接受目标*0.5，否则重试
# 每章字数截断上限（超过此字数将智能截断；创作目标与 prompt 不变）
CHAPTER_TRUNCATE_MAX_WORDS = 4096
