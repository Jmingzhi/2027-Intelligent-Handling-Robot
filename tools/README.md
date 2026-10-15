# 工具脚本

> 本目录存放与竞赛直接相关的辅助脚本。**不是一次性脚本，而是要长期维护的工具。**

## 现有工具

| 脚本 | 用途 | 用法 |
|---|---|---|
| `check_anonymity.py` | ★匿名性检查（对应竞赛"0 分"红线） | `python check_anonymity.py --path release/submission --strict` |
| `anonymity_wordlist.json` | 敏感词库（可编辑） | 由上面的脚本自动加载 |

## `check_anonymity.py` 用法

```bash
# 检查默认路径 release/submission
python tools/check_anonymity.py

# 指定路径（可多次）
python tools/check_anonymity.py --path release/submission --path docs/00-规则与命题

# 严格模式：发现命中则返回非 0 退出码（用于 CI 拦截）
python tools/check_anonymity.py --path release/submission --strict

# 列出当前生效的敏感词库
python tools/check_anonymity.py --list

# 指定自定义词库
python tools/check_anonymity.py --config 自定义词库.json
```

**为什么要这个工具**：规则明确「文档中出现校名、姓名、队名、地名、单位名、电话号码以及各种与文档内容无关的特殊符号 → 文档成绩 0 分」。
靠人眼检查 15 页文档容易漏，**脚本 + 人工复核**才可靠。

**⚠️ 脚本不能覆盖全部情况**：队名、地名、自定义标记等仍需人工复核。
脚本是"防漏网"，不是"替代人"。

## 词库维护

编辑 `anonymity_wordlist.json`，分类：

| 分类 | 含义 | 置信度 |
|---|---|---|
| `school` | 校名关键词 | 高（命中即高危） |
| `identity` | 姓名、队名标记词 | 高 |
| `contact` | 电话、邮箱、QQ | 高 |
| `marker` | 装饰性特殊符号 | 中 |
| `weak` | 宽泛词（如"大学""学院"） | 低（仅警告） |

**新增规则后请重新测试**，避免误报过多导致工具被忽略。

## 计划中的工具

| 脚本 | 用途 | 优先级 |
|---|---|---|
| `check_compliance.py` | 校验 BOM 的"来源"列是否齐全、是否与 compliance 台账对应 | 🟡 |
| `verify_lfs.py` | 检查是否有大文件被当作普通文件提交 | 🟡 |
| `check_doc_format.py` | 检查文档排版规范（竞赛占 25 分） | 🟡 |
| `timing_analyze.py` | 解析运行日志，输出时间剖面（找节拍瓶颈） | 🔴 |
| `calib_verify.py` | 校验标定文件的有效性与残差 | 🟡 |
| `log_plot.py` | 把结构化日志画成时间线图 | 🟢 |

> 💡 **`timing_analyze.py` 优先级最高**：本赛项 3 分钟节拍是最紧的约束，
> 需要工具把日志转成"每个阶段耗时多少"，才能快速定位瓶颈。

## 编写约定

| 项 | 要求 |
|---|---|
| 语言 | **Python 3**（与视觉代码统一），或用 PowerShell（`.ps1`）用于 Windows 环境操作 |
| 依赖 | **尽量只用标准库**，避免引入第三方依赖（CI 环境干净） |
| 编码 | UTF-8，换行 LF |
| 参数 | 用 `argparse`，提供 `--help` |
| 输出 | 中文输出，结论明确（成功/失败） |
| 退出码 | 0 = 通过，非 0 = 失败（供 CI 使用） |
| 测试 | 关键脚本要有自测（含边界与异常用例） |
| 文档 | 文件顶部注释说明用途与对应规则条款 |

## 变更记录

| 日期 | 变更 | 变更人 |
|---|---|---|
| 建仓日 | 目录建立，加入 `check_anonymity.py` | A |