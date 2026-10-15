# GitHub 远程仓库关联与推送说明

> 本文件说明如何把这个本地仓库推送到 GitHub。
> **如果你只想快点搞定，直接看第 3 节的"最简单方式"。**

---

## 1. 当前状态

| 项 | 状态 |
|---|---|
| 本地仓库 | ✅ 已建好（`main` + `develop` 两个分支，已有初始提交） |
| 远程仓库 | ⬜ 尚未创建 |
| 远程关联 | ⬜ 尚未关联 |

---

## 2. 前置条件

| 项 | 要求 | 检查命令 |
|---|---|---|
| Git | 已安装（建议 ≥ 2.30） | `git --version` |
| Git LFS | 建议安装 | `git lfs version` |
| GitHub 账号 | 有 | — |
| 网络 | 能访问 github.com | — |

**安装 Git LFS（若未安装）：**

```powershell
winget install GitHub.GitLFS
```

装完后执行一次：

```bash
git lfs install
```

> ⚠️ **本仓库的 CAD/PCB/模型/视频/PDF 走 Git LFS。**
> 没装 LFS 也能推送，但大文件会直接进 git 历史，**后面很难清理**。建议先装。

---

## 3. 最简单方式：运行脚本

在仓库目录下**双击运行 `push-to-github.bat`**，或在终端里执行：

```powershell
.\push-to-github.bat
```

脚本会：

1. 检查 git 与 Git LFS
2. 检查是否已有远程关联
3. **提示你在浏览器里创建空仓库**（因为创建远程仓库需要 GitHub 网页操作或 API 权限）
4. 让你输入仓库地址
5. 自动关联远程、推送 `main` 和 `develop`、推送标签

**关于登录**：第一次推送时，Windows 的 **Git Credential Manager** 会弹出窗口让你登录 GitHub。
登录一次之后凭据会被记住，后续无需重复登录。

> ✅ **不需要手动生成 token，不需要安装 `gh` CLI。**

---

## 4. 手动方式（分步说明）

### 4.1 在 GitHub 上创建空仓库

1. 打开 https://github.com/new
2. 填写：
   - **Repository name**：`2027-Intelligent-Handling-Robot`
   - **Description**（可选）：`2027 工创赛智能搬运赛项备赛仓库`
   - **Visibility**：建议选 **Private**
     > 💡 **为什么建议 Private**：赛前方案不公开，避免被对手看到技术路线。
     > 比赛结束后可以一键改成 Public（Settings → 最下方 Danger Zone → Change visibility）。
   - ⚠️ **不要勾选** "Add a README file"
   - ⚠️ **不要选** .gitignore 模板
   - ⚠️ **不要选** license
3. 点 **Create repository**
4. 复制页面上显示的仓库地址，形如：
   ```
   https://github.com/你的用户名/2027-Intelligent-Handling-Robot.git
   ```

> ⚠️ **第 2 步的三个"不要"很重要**：如果 GitHub 帮你生成了 README/LICENSE，
> 远程就有一个本地没有的提交，推送时会产生冲突，需要额外处理。

### 4.2 关联远程并推送

在仓库目录下执行：

```bash
# 关联远程（把 <地址> 换成你复制的地址）
git remote add origin <地址>

# 确认关联成功
git remote -v

# 推送 main 分支
git push -u origin main

# 推送 develop 分支
git push -u origin develop

# 推送标签（如果有）
git push --tags
```

### 4.3 如果已经有 origin 了

```bash
# 修改远程地址
git remote set-url origin <新地址>

# 或删除后重新添加
git remote remove origin
git remote add origin <地址>
```

---

## 5. 推送后建议做的配置

登录 GitHub 网页，在仓库里完成以下设置：

### 5.1 设置默认分支

`Settings` → `General` → `Default branch` → 改为 **`develop`**

> 💡 日常开发都在 `develop`，设为默认更顺手。

### 5.2 启用分支保护

`Settings` → `Branches` → `Add branch protection rule`

**对 `main` 分支：**

| 选项 | 建议 |
|---|---|
| Branch name pattern | `main` |
| Require a pull request before merging | ✅ 勾选 |
| Require approvals | ✅ 1 人 |
| Dismiss stale pull request approvals | ✅ 勾选 |
| Require conversation resolution | ✅ 勾选 |
| Do not allow bypassing the above settings | ✅ 勾选 |

**对 `develop` 分支：**

| 选项 | 建议 |
|---|---|
| Branch name pattern | `develop` |
| Require a pull request before merging | ✅ 勾选 |
| Require approvals | ⬜ 可不勾（三人队日常集成，太严会影响效率） |
| Require conversation resolution | ✅ 勾选 |

> ⚠️ **注意**：保护规则生效后，**自己也不能直接往 `main`/`develop` 推**。
> 这是有意的（见 [CONTRIBUTING.md](CONTRIBUTING.md)）。
> 如果三人队觉得太严，可以先只保护 `main`。

### 5.3 启用 Issues 与 Projects

`Settings` → `General` → `Features`

- ✅ **Issues**（必须，规则要求"所有技术问题必须 Issue 化"）
- ✅ **Projects**（推荐，用于看板管理）
- ⬜ Wiki（不需要，文档都在 `docs/` 里）
- ⬜ Discussions（可选）

### 5.4 添加协作者

`Settings` → `Collaborators` → `Add people`

把 B 和 C 的 GitHub 账号加进来，权限选 **Write**。

> 💡 不要给 **Admin**，除非确实需要改仓库设置。

### 5.5 检查 Actions 是否启用

`Actions` 标签页 → 如果提示需要启用，点 **Enable**

首次推送后，4 个工作流会自动跑一次：
- `lint-docs.yml`
- `anonymity-check.yml`
- `ci-firmware.yml`（没有 `platformio.ini` 时会优雅跳过）
- `ci-python.yml`

> 💡 **首次运行可能显示"失败"或"警告"，这通常是正常的**（因为代码目录还是空的）。
> 检查一下具体原因，确认是"因为没内容而跳过"而不是真的报错。

### 5.6 创建标签（Labels）

`Issues` → `Labels`，建议添加：

| 标签 | 颜色 | 用途 |
|---|---|---|
| `bug` | 红 | 缺陷 |
| `task` | 蓝 | 任务 |
| `experiment` | 紫 | 实验 |
| `decision` | 黄 | 待决策 |
| `hardware` | 绿 | 机械/硬件 |
| `embedded` | 青 | 电控/固件 |
| `vision` | 橙 | 视觉 |
| `algorithm` | 棕 | 算法 |
| `docs` | 灰 | 文档 |
| `blocked` | 深红 | 被阻塞 |
| `urgent` | 亮红 | 紧急 |

---

## 6. 常见问题

### 6.1 push 报 `rejected` / `non-fast-forward`

**原因**：远程有本地没有的提交（通常是建仓库时勾了 README）。

**解决**：

```bash
git pull --rebase origin main
git push -u origin main
```

### 6.2 push 报认证失败 / 反复要密码

**原因**：GitHub 已不支持账号密码认证。

**解决**：

| 方式 | 操作 |
|---|---|
| **Git Credential Manager（推荐）** | 装了 Git for Windows 就自带。首次 push 会弹浏览器登录窗口 |
| Personal Access Token | GitHub → Settings → Developer settings → Personal access tokens → 生成，**勾选 `repo`**，作为密码输入 |
| SSH 密钥 | 配置 SSH key 后把远程地址改为 `git@github.com:...` |

### 6.3 push 很慢 / 卡住

**原因**：可能在传大文件（PDF、模型）。

**检查**：

```bash
git lfs ls-files          # 确认大文件是否走 LFS
git count-objects -vH     # 看仓库体积
```

**若 PDF 等大文件未走 LFS**：确认 `.gitattributes` 生效：

```bash
git check-attr -a docs/00-规则与命题/附件2-1_智能+赛道命题与运行.pdf
# 应显示 filter: lfs
```

### 6.4 报 `remote: Repository not found`

**原因**：地址错误，或没有该仓库的访问权限（Private 仓库需要先被加为协作者）。

**解决**：核对地址；确认仓库可见性和协作者权限。

### 6.5 推送后 CAD 文件显示为几行文字

**原因**：LFS 指针被当成文件本身显示。

**解决**：

```bash
git lfs install
git lfs pull
```

### 6.6 不小心推送了不该推的东西

**不要自己重写历史**。先停下，参考 [仓库管理手册.md](仓库管理手册.md) 第 11.7 节，开 Issue 讨论。

### 6.7 想把 Private 改成 Public

`Settings` → 拉到底部 `Danger Zone` → `Change repository visibility` → `Change to public`

> ⚠️ 改成 Public 前**务必**确认仓库里没有：
> - 密码、密钥、WiFi 配置
> - 个人信息（电话号码、邮箱列表）
> - 竞赛提交物的敏感内容

---

## 7. 仓库地址记录（推送后填写）

| 项 | 值 |
|---|---|
| 远程地址 | 待填 |
| 默认分支 | `develop`（建议） |
| 可见性 | Private |
| 协作者 | 待填 |
| 首次推送日期 | 待填 |

---

## 8. 参考

- Git 官方文档：https://git-scm.com/doc
- Git LFS：https://git-lfs.com
- GitHub 分支保护：https://docs.github.com/cn/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches

---

**相关文档**：[仓库管理手册.md](仓库管理手册.md) · [CONTRIBUTING.md](CONTRIBUTING.md)
