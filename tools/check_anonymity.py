#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""匿名性（去标识化）检查工具 —— 竞赛命题文档提交前的自检脚本。

竞赛规则依据
------------
《2027 年第十届中国大学生工程实践与创新能力大赛 · 智能 + 工程创新赛道 ·
智能搬运赛项》命题文档评审要求中明确规定：

    任务命题文档中出现校名、姓名、队名、电话号码、邮箱，以及与文档内容
    无关的特殊符号的，该队文档成绩为 0 分。

即：提交材料必须完成"去标识化"。本脚本在提交前扫描 ``release/submission``
（以及规则 / 命题文档目录）中的纯文本材料，自动检出上述五类风险：

==================  ==================================================  ==========
类别                 检出方式                                            严重级别
==================  ==================================================  ==========
``school``          校名关键词（含英文缩写、校园域名），词库可配置        高危
``identity``        姓名 / 队名 / 队长 / 组员等标记词 + 真实姓名列表     高危
``contact``         手机号、邮箱、QQ 号（正则）                          高危
``marker``          装饰性特殊符号（★☆●◆■▲▼※→← 等）成组出现          高危
``weak``            过于宽泛的弱关键词（"大学""学院"等）               仅提示
==================  ==================================================  ==========

``weak`` 类别置信度低、误报率高，因此只提示、永不判定失败；其余类别在
``--strict`` 模式下会产生退出码 1，可直接作为 CI 门禁。

词库维护
--------
默认词库为脚本同目录下的 ``anonymity_wordlist.json``。JSON 不支持注释，故以
下划线开头的键存放使用说明，脚本会自动忽略。可直接编辑该文件增删条目，或用
``--config`` 指向另一份词库；某个类别留空（空数组 / 空对象）表示沿用内置默认值。
请务必把本队学校关键词、指导教师与队员姓名补入 ``school`` 与
``identity.names``，否则这些信息无法被检出。

用法示例
--------
    python tools/check_anonymity.py --list
    python tools/check_anonymity.py --path release/submission --strict
    python tools/check_anonymity.py --path "docs/00-规则与命题"
    python tools/check_anonymity.py --path a.md --config my_wordlist.json

退出码
------
    0   未发现高危命中，或未开启 ``--strict``
    1   开启 ``--strict`` 且发现高危命中
    2   命令行参数或配置文件错误

仅依赖 Python 标准库（3.9+），无任何第三方依赖。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

__version__ = "1.0.0"

# --------------------------------------------------------------------------- #
# 常量与内置默认词库
# --------------------------------------------------------------------------- #

SCRIPT_DIR: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = SCRIPT_DIR.parent
DEFAULT_CONFIG_PATH: Path = SCRIPT_DIR / "anonymity_wordlist.json"
DEFAULT_SCAN_PATH: str = "release/submission"

#: 参与扫描的纯文本扩展名（其余类型按二进制处理并跳过）
SCAN_SUFFIXES: frozenset[str] = frozenset(
    {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".html", ".tex"}
)

#: 文件名黑名单：这些文件按定义就是"用来描述违规词"的，扫描它们必然误报。
#: 例：anonymity_wordlist.json 本身装满校名与关键字；tools/README.md 会举例说明。
SKIP_FILE_NAMES: frozenset[str] = frozenset(
    {
        "anonymity_wordlist.json",
        "check_anonymity.py",
    }
)

#: 目录级排除：本仓库中 tools/ 与 release/ 属于"描述提交规则"的区域，
#: 其文本天然包含规则原文（含"姓名""手机号"等词），扫描它们必然误报。
#: ⚠️ 真正的提交物放在 release/submission/ 下 —— 该子目录不在此列，
#:    必须被严格扫描（默认扫描目标就是它）。
SKIP_FILE_PARENTS: frozenset[str] = frozenset(
    {
        "tools",
        "release",
    }
)

#: 遍历时直接跳过的目录名
SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".github",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)

#: 单文件扫描上限，超过则跳过，避免误读大体积二进制素材
MAX_FILE_BYTES: int = 4 * 1024 * 1024

#: 命中行预览的截断长度
LINE_PREVIEW_LIMIT: int = 80

#: 类别 -> 中文标签
CATEGORY_LABELS: dict[str, str] = {
    "school": "校名",
    "identity": "姓名/队名",
    "contact": "联系方式",
    "marker": "特殊符号",
    "weak": "低置信度",
}

#: 类别 -> 严重级别；weak 只提示，不判定失败
SEVERITY_BY_CATEGORY: dict[str, str] = {
    "school": "high",
    "identity": "high",
    "contact": "high",
    "marker": "high",
    "weak": "low",
}

#: 装饰性特殊符号集合（单个出现可能是正常排版，成组出现才告警）
DEFAULT_MARKER_CHARS: str = "★☆●◆■▲▼※→←"

#: 兜底联系方式正则；正常情况下由 JSON 词库提供
DEFAULT_CONTACT_PATTERNS: dict[str, str] = {
    "phone_pattern": r"(?<!\d)1[3-9]\d{9}(?!\d)",
    "email_pattern": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+",
    "qq_pattern": r"(?i)(?:\bQQ\b\s*[:：]?\s*[1-9]\d{4,10}|[1-9]\d{4,10}@qq\.com)",
}

#: 内置默认词库。/tools/anonymity_wordlist.json 缺失或损坏时作为兜底使用。
DEFAULT_WORDLIST: dict[str, object] = {
    "version": 1,
    "school": [
        "华南理工大学",
        "华南理工",
        "SCUT",
        "scut.edu.cn",
        "华中科技大学",
        "哈尔滨工业大学",
        "北京航空航天大学",
        "西安交通大学",
        "浙江大学",
        "清华大学",
        "北京大学",
    ],
    "identity": {
        "markers": [
            "姓名",
            "队名",
            "队长",
            "组员",
            "成员",
            "队员",
            "指导教师",
            "指导老师",
            "参赛队伍",
        ],
        "names": [],
    },
    "contact": dict(DEFAULT_CONTACT_PATTERNS),
    "marker": list(DEFAULT_MARKER_CHARS),
    "weak": ["大学", "学院", "学校", "职业技术"],
}


# --------------------------------------------------------------------------- #
# 数据结构
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Rule:
    """一条匿名性检测规则。

    :param category: 所属类别，取值为 ``school`` / ``identity`` / ``contact`` /
        ``marker`` / ``weak``。
    :param kind: 规则种类，``keyword``（关键词子串）、``regex``（正则）或
        ``marker``（装饰符号成组检测）。
    :param severity: 严重级别，``high``（高危，strict 下判失败）或 ``low``
        （仅提示）。
    :param pattern: 已编译的正则；``marker`` 规则为 ``None``。
    :param keyword: 原始关键词或符号集合，用于 ``--list`` 展示与排错。
    :param description: 人类可读的规则说明。
    """

    category: str
    kind: str
    severity: str
    pattern: re.Pattern[str] | None = None
    keyword: str = ""
    description: str = ""

    @property
    def label(self) -> str:
        """返回该规则类别的中文标签。"""
        return CATEGORY_LABELS.get(self.category, self.category)

    @property
    def is_high(self) -> bool:
        """该规则命中后是否属于高危。"""
        return self.severity == "high"


@dataclass
class Hit:
    """单条命中记录。"""

    path: Path
    lineno: int
    category: str
    matched: str
    line: str
    severity: str

    @property
    def is_high(self) -> bool:
        """该命中是否为高危。"""
        return self.severity == "high"

    def preview(self, limit: int = LINE_PREVIEW_LIMIT) -> str:
        """返回截断后的所在行内容。"""
        text = " ".join(self.line.split())
        if len(text) <= limit:
            return text
        return text[:limit] + "…"


@dataclass
class Wordlist:
    """生效中的敏感词库。"""

    school: list[str] = field(default_factory=list)
    identity_markers: list[str] = field(default_factory=list)
    identity_names: list[str] = field(default_factory=list)
    weak: list[str] = field(default_factory=list)
    marker_chars: str = DEFAULT_MARKER_CHARS
    contact_patterns: dict[str, str] = field(
        default_factory=lambda: dict(DEFAULT_CONTACT_PATTERNS)
    )
    source: str = "<内置默认词库>"

    def describe(self) -> Iterator[str]:
        """逐行产出词库内容，供 ``--list`` 打印。"""
        yield f"词库来源            : {self.source}"
        yield f"校名 school         : {len(self.school)} 条 -> {', '.join(self.school) or '（空）'}"
        yield (
            f"身份标记 identity   : {len(self.identity_markers)} 条 -> "
            f"{', '.join(self.identity_markers) or '（空）'}"
        )
        yield (
            f"真实姓名 names      : {len(self.identity_names)} 条 -> "
            f"{', '.join(self.identity_names) or '（空，建议填入已知姓名以便自查）'}"
        )
        yield f"联系方式正则 contact: {len(self.contact_patterns)} 条"
        for name, pattern in self.contact_patterns.items():
            yield f"    - {name}: {pattern}"
        yield f"特殊符号 marker     : {self.marker_chars or '（空）'}"
        yield f"弱关键词 weak       : {len(self.weak)} 条 -> {', '.join(self.weak) or '（空）'}"


# --------------------------------------------------------------------------- #
# 词库加载
# --------------------------------------------------------------------------- #


def _as_str_list(value: object) -> list[str]:
    """把配置中的标量 / 列表统一转换为去空字符串列表。"""
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple, set)):
        result: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
        return result
    return []


def _overlay(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    """用配置文件覆盖内置默认值（按类别整体覆盖，空值视为未配置）。"""
    merged: dict[str, object] = dict(base)
    for key, value in override.items():
        if key.startswith("_") or key == "version":
            continue
        if value is None or value == [] or value == {} or value == "":
            continue
        merged[key] = value
    return merged


def _wordlist_from_mapping(mapping: dict[str, object], source: str) -> Wordlist:
    """将 JSON 映射转换为 :class:`Wordlist`。"""
    identity = mapping.get("identity")
    if isinstance(identity, dict):
        markers = _as_str_list(identity.get("markers"))
        names = _as_str_list(identity.get("names"))
    else:
        # 允许简写：identity 直接写成字符串列表，视为标记词
        markers = _as_str_list(identity)
        names = []

    contact_patterns = dict(DEFAULT_CONTACT_PATTERNS)
    contact = mapping.get("contact")
    if isinstance(contact, dict):
        for key in DEFAULT_CONTACT_PATTERNS:
            value = contact.get(key)
            if isinstance(value, str) and value.strip():
                contact_patterns[key] = value.strip()

    marker_chars = "".join(_as_str_list(mapping.get("marker"))) or DEFAULT_MARKER_CHARS

    return Wordlist(
        school=_as_str_list(mapping.get("school")),
        identity_markers=markers,
        identity_names=names,
        weak=_as_str_list(mapping.get("weak")),
        marker_chars=marker_chars,
        contact_patterns=contact_patterns,
        source=source,
    )


def load_wordlist(config_path: Path | None) -> tuple[Wordlist, list[str]]:
    """加载词库。

    :param config_path: 显式指定的 JSON 词库路径；``None`` 表示使用脚本同目录
        下的 ``anonymity_wordlist.json``。
    :returns: ``(词库, 警告列表)``。
    :raises FileNotFoundError: 当用户通过 ``--config`` 显式指定的文件不存在。
    :raises ValueError: 当用户通过 ``--config`` 显式指定的文件不是合法 JSON。
    """
    warnings: list[str] = []
    explicit = config_path is not None
    path = Path(config_path) if explicit else DEFAULT_CONFIG_PATH

    if not path.is_file():
        if explicit:
            raise FileNotFoundError(f"指定的词库文件不存在：{path}")
        warnings.append(f"未找到默认词库 {path}，已回退到内置默认词库。")
        return _wordlist_from_mapping(dict(DEFAULT_WORDLIST), "<内置默认词库>"), warnings

    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        if explicit:
            raise ValueError(f"词库文件无法解析：{path}（{exc}）") from exc
        warnings.append(f"默认词库 {path} 无法解析（{exc}），已回退到内置默认词库。")
        return _wordlist_from_mapping(dict(DEFAULT_WORDLIST), "<内置默认词库>"), warnings

    if not isinstance(raw, dict):
        message = f"词库文件顶层必须是 JSON 对象：{path}"
        if explicit:
            raise ValueError(message)
        warnings.append(message + "，已回退到内置默认词库。")
        return _wordlist_from_mapping(dict(DEFAULT_WORDLIST), "<内置默认词库>"), warnings

    version = raw.get("version")
    if version is not None and version != DEFAULT_WORDLIST["version"]:
        warnings.append(
            f"词库版本为 {version!r}，本脚本内置版本为 "
            f"{DEFAULT_WORDLIST['version']!r}，字段结构可能不一致。"
        )

    merged = _overlay(dict(DEFAULT_WORDLIST), raw)
    return _wordlist_from_mapping(merged, str(path)), warnings


# --------------------------------------------------------------------------- #
# 规则构建
# --------------------------------------------------------------------------- #


def build_rules(wordlist: Wordlist) -> tuple[list[Rule], list[str]]:
    """根据词库构建检测规则。

    :returns: ``(规则列表, 警告列表)``。
    """
    rules: list[Rule] = []
    warnings: list[str] = []

    def add_keywords(items: Iterable[str], category: str, description: str) -> None:
        for keyword in items:
            if not keyword.strip():
                continue
            rules.append(
                Rule(
                    category=category,
                    kind="keyword",
                    severity=SEVERITY_BY_CATEGORY[category],
                    pattern=re.compile(re.escape(keyword), re.IGNORECASE),
                    keyword=keyword,
                    description=description,
                )
            )

    add_keywords(wordlist.school, "school", "校名 / 校园域名关键词")
    add_keywords(wordlist.identity_markers, "identity", "姓名、队名等身份标记词")
    add_keywords(wordlist.identity_names, "identity", "配置中登记的真实姓名")
    add_keywords(wordlist.weak, "weak", "过于宽泛的弱关键词，仅提示")

    for name, pattern_text in wordlist.contact_patterns.items():
        try:
            compiled = re.compile(pattern_text)
        except re.error as exc:
            warnings.append(f"联系方式规则 {name} 正则非法，已跳过：{exc}")
            continue
        rules.append(
            Rule(
                category="contact",
                kind="regex",
                severity=SEVERITY_BY_CATEGORY["contact"],
                pattern=compiled,
                keyword=name,
                description=f"联系方式正则：{name}",
            )
        )

    if wordlist.marker_chars:
        rules.append(
            Rule(
                category="marker",
                kind="marker",
                severity=SEVERITY_BY_CATEGORY["marker"],
                pattern=None,
                keyword=wordlist.marker_chars,
                description="装饰性特殊符号的连续或成组出现",
            )
        )

    return rules, warnings


# --------------------------------------------------------------------------- #
# 文件遍历与读取
# --------------------------------------------------------------------------- #


def resolve_target(raw: str) -> Path:
    """把命令行给出的路径解析为绝对路径。

    相对路径优先按当前工作目录解析，若不存在则退回到仓库根目录，便于在任意
    目录下调用本脚本。
    """
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate
    if candidate.exists():
        return candidate.resolve()
    from_repo = REPO_ROOT / candidate
    if from_repo.exists():
        return from_repo.resolve()
    return (Path.cwd() / candidate).resolve()


def is_binary(data: bytes) -> bool:
    """按内容粗略判断是否为二进制数据。"""
    if not data:
        return False
    sample = data[:8192]
    if b"\x00" in sample:
        return True
    allowed = bytes(range(0x20, 0x7F)) + b"\n\r\t\x0c\x1b"
    non_text = sum(1 for byte in sample if byte < 0x80 and byte not in allowed)
    return non_text / len(sample) > 0.30


def iter_target_files(targets: Sequence[Path]) -> tuple[list[Path], list[Path]]:
    """展开扫描目标。

    :returns: ``(待扫描文件列表, 不存在的目标列表)``。
    """
    files: list[Path] = []
    missing: list[Path] = []
    seen: set[Path] = set()

    for target in targets:
        if target.is_dir():
            target_root = target.resolve()
            for root, dirnames, filenames in os.walk(target_root):
                dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIR_NAMES)
                root_path = Path(root)
                # 相对扫描起点的路径 + 起点自身的名字，用于判断是否落在
                # "描述规则"的目录内（tools/、release/ 的说明性文档天然含敏感词）。
                try:
                    rel_parts_current = (
                        target_root.name,
                        *root_path.resolve().relative_to(target_root).parts,
                    )
                except ValueError:
                    rel_parts_current = (target_root.name,)
                for filename in sorted(filenames):
                    path = root_path / filename
                    if path.suffix.lower() not in SCAN_SUFFIXES:
                        continue
                    if filename in SKIP_FILE_NAMES:
                        continue
                    # 规则：只要"路径中任一层"是 SKIP_FILE_PARENTS 里的名字就跳过。
                    # 这样 `--path release` 会跳过 release/README.md（描述性文档），
                    # 但仍会进入 release/submission/ 扫描真正的提交物。
                    if any(p in SKIP_FILE_PARENTS for p in rel_parts_current):
                        continue
                    resolved = path.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        files.append(path)
        elif target.is_file():
            # 显式指定某个文件时一律扫描 —— 用户已经明确要检查它，
            # 不套用"描述规则目录"的排除（如手动检查 release/README.md）。
            resolved = target.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(target)
        else:
            missing.append(target)

    files.sort(key=lambda p: str(p).lower())
    return files, missing


def read_text(path: Path) -> str | None:
    """读取文本文件内容；二进制、超大或不可读的文件返回 ``None``。"""
    try:
        data = path.read_bytes()
    except OSError as exc:
        annotate("warning", f"无法读取文件：{exc}", path)
        return None
    if len(data) > MAX_FILE_BYTES:
        annotate(
            "notice",
            f"文件超过 {MAX_FILE_BYTES // (1024 * 1024)} MiB，已跳过。",
            path,
        )
        return None
    if is_binary(data):
        return None
    return data.decode("utf-8-sig", errors="replace")


# --------------------------------------------------------------------------- #
# 扫描逻辑
# --------------------------------------------------------------------------- #


def _dedupe_overlaps(
    candidates: Sequence[tuple[int, int, Rule, str]],
) -> list[tuple[int, int, Rule, str]]:
    """去除区间重叠的命中，同一起点保留最长匹配。

    这样 ``华南理工大学`` 只会按校名报告一次，而不会被更短的 ``大学``
    （弱关键词）重复报告。
    """
    accepted: list[tuple[int, int, Rule, str]] = []
    for start, end, rule, text in sorted(
        candidates, key=lambda item: (item[0], -(item[1] - item[0]))
    ):
        if any(start < a_end and end > a_start for a_start, a_end, _, _ in accepted):
            continue
        accepted.append((start, end, rule, text))
    return accepted


def _scan_markers(path: Path, lineno: int, line: str, rule: Rule) -> list[Hit]:
    """检测装饰性特殊符号：同一符号连续出现 2 次以上，或单行合计 3 个以上。"""
    chars = rule.keyword
    if not chars:
        return []

    run_pattern = re.compile("([" + re.escape(chars) + r"])\1+")
    runs = list(run_pattern.finditer(line))
    if runs:
        return [
            Hit(path, lineno, rule.category, m.group(0), line, rule.severity)
            for m in runs
        ]

    found = [ch for ch in line if ch in set(chars)]
    if len(found) >= 3:
        grouped = "".join(dict.fromkeys(found))
        return [Hit(path, lineno, rule.category, grouped, line, rule.severity)]
    return []


def scan_file(path: Path, rules: Sequence[Rule]) -> list[Hit]:
    """扫描单个文件并返回全部命中。"""
    text = read_text(path)
    if text is None:
        return []

    keyword_and_regex = [r for r in rules if r.kind in ("keyword", "regex")]
    marker_rules = [r for r in rules if r.kind == "marker"]
    hits: list[Hit] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        candidates: list[tuple[int, int, Rule, str]] = []
        for rule in keyword_and_regex:
            if rule.pattern is None:
                continue
            for match in rule.pattern.finditer(line):
                matched = match.group(0)
                if not matched.strip():
                    continue
                candidates.append((match.start(), match.end(), rule, matched))

        for _, _, rule, matched in _dedupe_overlaps(candidates):
            hits.append(Hit(path, lineno, rule.category, matched, line, rule.severity))

        for rule in marker_rules:
            hits.extend(_scan_markers(path, lineno, line, rule))

    return hits


# --------------------------------------------------------------------------- #
# 输出
# --------------------------------------------------------------------------- #


def annotate(level: str, message: str, path: Path | None = None, lineno: int | None = None) -> None:
    """在 GitHub Actions 环境下输出注解；本地运行时静默。"""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    location = ""
    if path is not None:
        location = f" file={path}"
        if lineno is not None:
            location += f",line={lineno}"
    print(f"::{level}{location}::{message}")


def configure_stdout() -> None:
    """确保标准输出可以打印中文与 ✅ / ❌ 符号。"""
    stream = sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        "✅❌".encode(encoding)
    except (UnicodeEncodeError, LookupError):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def print_wordlist(wordlist: Wordlist, rules: Sequence[Rule], warnings: Sequence[str]) -> None:
    """打印当前生效的敏感词库。"""
    print(f"匿名性检查词库清单（check_anonymity {__version__}）")
    print("=" * 62)
    for line in wordlist.describe():
        print(line)
    print("-" * 62)
    high = sum(1 for rule in rules if rule.is_high)
    print(f"已编译检测规则      : {len(rules)} 条（高危 {high} 条，低置信度 {len(rules) - high} 条）")
    for warning in warnings:
        print(f"[提示] {warning}")


def print_report(
    hits: Sequence[Hit],
    files_scanned: int,
    wordlist: Wordlist,
    warnings: Sequence[str],
    strict: bool,
) -> None:
    """打印扫描报告与最终结论。"""
    high_hits = [hit for hit in hits if hit.is_high]
    low_hits = [hit for hit in hits if not hit.is_high]

    print(f"匿名性检查报告（check_anonymity {__version__}）")
    print("=" * 62)
    print(f"词库来源      : {wordlist.source}")
    print(f"扫描文件数    : {files_scanned}")
    print(f"总命中数      : {len(hits)}（高危 {len(high_hits)}，低置信度 {len(low_hits)}）")

    for warning in warnings:
        print(f"[提示] {warning}")

    if hits:
        print("-" * 62)
        current: Path | None = None
        for hit in sorted(hits, key=lambda h: (str(h.path).lower(), h.lineno)):
            if current is None or hit.path != current:
                current = hit.path
                print(f"\n{hit.path}")
            print(
                f"  {hit.path.name}:{hit.lineno}  "
                f"[{CATEGORY_LABELS.get(hit.category, hit.category)}]  "
                f"{hit.matched}  → {hit.preview()}"
            )

    print("=" * 62)
    if not hits:
        print("✅ 未发现标识化风险")
    else:
        print(f"❌ 发现 {len(hits)} 处风险，其中 {len(high_hits)} 处为高危")
        if not strict:
            print("提示：未开启 --strict，本次退出码为 0；正式提交前请使用 --strict 复核。")
        elif high_hits:
            print("严格模式：高危命中将导致退出码 1，请先完成去标识化处理。")


# --------------------------------------------------------------------------- #
# 入口
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="check_anonymity.py",
        description=(
            "竞赛命题文档匿名性（去标识化）自检工具：检出校名、姓名/队名、"
            "电话号码、邮箱与无关特殊符号。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python tools/check_anonymity.py --list\n"
            "  python tools/check_anonymity.py --path release/submission --strict\n"
            "  python tools/check_anonymity.py --path docs/00-规则与命题\n"
        ),
    )
    parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        metavar="DIR_OR_FILE",
        help=(
            "待扫描的目录或文件，可重复指定；指定后覆盖默认路径 "
            f"（默认 {DEFAULT_SCAN_PATH}）。"
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="发现高危命中时以退出码 1 结束；不加则仅报告并以 0 结束。",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        type=Path,
        default=None,
        help=f"指定 JSON 词库文件（默认 {DEFAULT_CONFIG_PATH}）。",
    )
    parser.add_argument(
        "--list",
        dest="list_wordlist",
        action="store_true",
        help="列出当前生效的敏感词库后退出。",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"check_anonymity {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """脚本主入口，返回进程退出码。"""
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        wordlist, load_warnings = load_wordlist(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    rules, rule_warnings = build_rules(wordlist)
    warnings = load_warnings + rule_warnings

    if args.list_wordlist:
        print_wordlist(wordlist, rules, warnings)
        return 0

    raw_targets = args.paths or [DEFAULT_SCAN_PATH]
    targets = [resolve_target(raw) for raw in raw_targets]
    files, missing = iter_target_files(targets)

    for path in missing:
        print(f"[跳过] 路径不存在或不可访问：{path}")
        annotate("notice", f"路径不存在，已跳过：{path}")
    if not files:
        print("[跳过] 没有可扫描的纯文本文件（目录为空或仅含二进制文件）。")

    hits: list[Hit] = []
    for path in files:
        hits.extend(scan_file(path, rules))

    print_report(hits, len(files), wordlist, warnings, args.strict)

    for hit in hits:
        if hit.is_high:
            annotate("warning", f"[{CATEGORY_LABELS.get(hit.category, hit.category)}] {hit.matched}", hit.path, hit.lineno)

    if args.strict and any(hit.is_high for hit in hits):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
