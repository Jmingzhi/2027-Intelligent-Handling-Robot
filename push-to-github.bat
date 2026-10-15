@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
title 2027智能搬运 - 推送到GitHub

echo ============================================================
echo   2027 工创赛智能搬运赛项 - 推送到 GitHub
echo ============================================================
echo.

rem ---------- 切到脚本所在目录 ----------
cd /d "%~dp0"
echo [信息] 仓库目录: %CD%
echo.

rem ---------- 1. 检查 git ----------
where git >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 git。请先安装 Git: https://git-scm.com
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('git --version') do set "GITVER=%%v"
echo [通过] !GITVER!

rem ---------- 2. 检查 Git LFS ----------
where git-lfs >nul 2>nul
if errorlevel 1 (
    echo [警告] 未检测到 Git LFS。
    echo        本仓库的 CAD / PCB / 模型 / 视频 / PDF 设计为走 LFS。
    echo        没装 LFS 也能推送，但大文件会直接进 git 历史，后面很难清理。
    echo        建议先安装: winget install GitHub.GitLFS
    echo.
    set /p LFSOK="仍要继续吗? (y/N): "
    if /i not "!LFSOK!"=="y" (
        echo 已取消。
        pause
        exit /b 0
    )
) else (
    echo [通过] Git LFS 已安装
)

rem ---------- 3. 检查是否已是 git 仓库 ----------
if not exist ".git" (
    echo [错误] 当前目录不是 git 仓库（找不到 .git 目录）。
    echo        请确认本脚本放在仓库根目录下。
    echo.
    pause
    exit /b 1
)

rem ---------- 4. 检查是否已有提交 ----------
git rev-parse --verify HEAD >nul 2>nul
if errorlevel 1 (
    echo [错误] 仓库还没有任何提交，无法推送。
    echo.
    pause
    exit /b 1
)

rem ---------- 5. 检查远程 ----------
set "HASORIGIN="
for /f "delims=" %%r in ('git remote') do (
    if /i "%%r"=="origin" set "HASORIGIN=1"
)

if defined HASORIGIN (
    echo.
    echo [信息] 已存在远程 origin:
    git remote -v
    echo.
    set /p REDO="要修改远程地址吗? (y/N): "
    if /i "!REDO!"=="y" (
        set /p NEWURL="请输入新的仓库地址: "
        git remote set-url origin "!NEWURL!"
        echo [完成] 远程地址已更新
    )
) else (
    echo.
    echo ------------------------------------------------------------
    echo   下一步需要在 GitHub 上创建一个【空的】仓库
    echo ------------------------------------------------------------
    echo.
    echo   1. 浏览器打开:  https://github.com/new
    echo   2. Repository name 填:  2027-Intelligent-Handling-Robot
    echo   3. Visibility 建议选:   Private
    echo   4. 重要: 不要勾选 Add a README file
    echo            不要选 .gitignore 模板
    echo            不要选 license
    echo   5. 点 Create repository
    echo   6. 复制页面上显示的仓库地址
    echo.
    echo   （如果勾了 README 等，远程会多一个提交，推送时会冲突）
    echo.
    pause
    echo.
    set /p REPOURL="请粘贴仓库地址 (形如 https://github.com/用户名/仓库名.git): "
    if "!REPOURL!"=="" (
        echo [错误] 未输入地址，已取消。
        pause
        exit /b 1
    )
    git remote add origin "!REPOURL!"
    if errorlevel 1 (
        echo [错误] 添加远程失败，请检查地址是否正确。
        pause
        exit /b 1
    )
    echo [完成] 已关联远程 origin
)

echo.
echo ============================================================
echo   开始推送
echo ============================================================
echo.
echo [提示] 首次推送会弹出登录窗口，请用浏览器登录 GitHub 账号。
echo        登录一次后凭据会被 Windows 记住，后续无需重复登录。
echo.
pause

rem ---------- 6. 推送 main ----------
echo.
echo [1/3] 推送 main 分支...
git push -u origin main
if errorlevel 1 (
    echo.
    echo [错误] main 分支推送失败。常见原因:
    echo        - 远程仓库不是空的（建仓库时勾了 README / license）
    echo          解决: git pull --rebase origin main  然后重试
    echo        - 地址错误或没有访问权限
    echo        - 网络问题
    echo.
    pause
    exit /b 1
)
echo [完成] main 已推送

rem ---------- 7. 推送 develop ----------
echo.
echo [2/3] 推送 develop 分支...
git push -u origin develop
if errorlevel 1 (
    echo [警告] develop 分支推送失败，请检查。
) else (
    echo [完成] develop 已推送
)

rem ---------- 8. 推送标签 ----------
echo.
echo [3/3] 推送标签...
git push --tags 2>nul
echo [完成] 标签处理完毕（若没有标签则跳过）

echo.
echo ============================================================
echo   推送完成！
echo ============================================================
echo.
echo   接下来建议在 GitHub 网页上做这些设置:
echo     1. Settings - General - Default branch 改为 develop
echo     2. Settings - Branches 给 main 加分支保护
echo     3. Settings - Collaborators 把队友加进来（Write 权限）
echo     4. Actions 标签页确认 CI 已启用
echo.
echo   详细说明见: GITHUB_SETUP.md 第 5 节
echo.
pause
exit /b 0
