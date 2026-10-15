# 更新日志

本文件记录本项目的重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

**版本语义（本项目约定）**

| 版本段 | 含义 |
|---|---|
| 主版本 | 重大架构变更 / 比赛冻结版本 |
| 次版本 | 新增功能或重要文档 |
| 修订号 | 修复问题、文档补充 |

**变更类型**

`新增` / `变更` / `弃用` / `移除` / `修复` / `安全`

---

## [未发布]

### 新增

- 待填

### 变更

- 待填

### 修复

- 待填

---

## [0.1.0] - 建仓日

### 新增

**仓库基础设施**

- 完整的项目目录结构（`docs/`、`hardware/`、`embedded/`、`vision/`、`algorithm/`、`simulation/`、`test/`、`tools/`、`release/`）
- [README.md](README.md) 中文主入口文档，含赛项核心约束速查、成绩构成、时间线、团队分工
- [README.en.md](README.en.md) 英文版
- [仓库管理手册.md](仓库管理手册.md) —— 面向队友的上手文档，覆盖仓库组成、使用、更新、增添
- [CONTRIBUTING.md](CONTRIBUTING.md) 协作规范（分支/提交/Issue/PR/评审/接口变更流程）
- [GITHUB_SETUP.md](GITHUB_SETUP.md) 远程仓库关联与推送说明
- [push-to-github.bat](push-to-github.bat) 一键推送脚本
- [LICENSE](LICENSE) MIT 许可证

**Git 配置**

- `.gitattributes` —— Git LFS 规则，覆盖 CAD（`.SLDPRT`/`.step`/`.f3d`）、3D 打印（`.stl`/`.3mf`）、PCB（`.epro`/`.kicad_pcb`）、AI 模型（`.onnx`/`.pt`）、视频、ROS bag、压缩包、Office 文档
- `.gitignore` —— 忽略编译产物、嵌入式工具链输出、Python 缓存、IDE 个人配置、CAD 临时文件、数据集、模型权重、**凭据与密钥**

**自动化（GitHub Actions）**

- `.github/workflows/lint-docs.yml` —— 文档占位符残留、空文件、失效相对链接检查
- `.github/workflows/anonymity-check.yml` —— 提交物匿名性检查（对应竞赛"0 分"红线）
- `.github/workflows/ci-firmware.yml` —— 固件编译（存在 `platformio.ini` 时触发）
- `.github/workflows/ci-python.yml` —— Python lint 与测试
- `.github/ISSUE_TEMPLATE/` —— `bug.yml` / `task.yml` / `experiment.yml` / `decision.yml`
- `.github/PULL_REQUEST_TEMPLATE.md` —— 含"怎么验证的"与"是否影响接口"必填项
- `.github/CODEOWNERS` —— 按目录指定审核人

**规则与命题（`docs/00-规则与命题/`）**

- 归档官方规则原文三份（附件2-1 命题与运行、附件2-2 评分与规则、命题解析）
- [规则解读.md](docs/00-规则与命题/规则解读.md) —— 结构化提炼官方规则，含全部硬性约束、场地与物料参数、任务码结构、计分细则、时间账、**从规则推导出的工程约束**、以及 20 条易误读项核对表
- [合规检查表.md](docs/00-规则与命题/合规检查表.md) —— 八部分逐条自查表，覆盖采购与自制合规、外形尺寸、电控与电源、运行行为、提交文档匿名性、创意评分准备

**场地与标定（`docs/05-场地与标定/`）**

- [场地尺寸实测绘.md](docs/05-场地与标定/场地尺寸实测绘.md) —— 实测记录表与偏差分析
- [圆环尺寸表.csv](docs/05-场地与标定/圆环尺寸表.csv) —— 圆环外径递推公式、评分对照、参考算例
- [转盘节拍测试.md](docs/05-场地与标定/转盘节拍测试.md) —— 转盘转速与停位误差实测方法、抓取时序分析

**接口契约（`docs/10-接口契约/`）**

- [ICD-机械电气接口.md](docs/10-接口契约/ICD-机械电气接口.md) —— 系统架构、模块划分、机械接口、电气接口、软件接口、任务状态机
- [通信协议.md](docs/10-接口契约/通信协议.md) —— 帧格式、CRC-16/CCITT、命令集、交互时序、错误码、调试通道约束
- [坐标系与标定约定.md](docs/10-接口契约/坐标系与标定约定.md) —— 六个坐标系定义、变换链、场地元素坐标登记、**现场 3 分钟调试内的标定流程**
- [任务码定义.md](docs/10-接口契约/任务码定义.md) —— 四组三位数结构、颜色与位置编码、官方样例逐位解析、解析伪代码、单元测试用例

**工具（`tools/`）**

- `check_anonymity.py` —— 匿名性检查脚本，检测校名、姓名、队名、地名、电话、邮箱、特殊符号
- `anonymity_wordlist.json` —— 可配置敏感词库

**骨架目录**

- `hardware/{cad,pcb,bom,drawings,compliance}` —— 含 `compliance/` 购件合规台账目录（本赛项特有）
- `embedded/shared/` —— 通信协议共享定义（避免固件与 Python 各自复制粘贴）
- `vision/{calibration,dataset,models,src}`
- `algorithm/`、`simulation/`
- `test/{bench,field,acceptance}` —— 含 `acceptance/` 验收测试
- `release/submission/` —— 匿名提交版

### 说明

- 本版本为**方案与规范搭建阶段**，硬件选型与技术路线尚未确定，相关字段统一标记为 `TBD`
- 待确定信息登记于 `docs/60-项目管理/待确认清单.md`

---

<!--
版本对比链接（仓库地址确定后替换 <OWNER>/<REPO>）

[未发布]: https://github.com/<OWNER>/<REPO>/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/<OWNER>/<REPO>/releases/tag/v0.1.0
-->
