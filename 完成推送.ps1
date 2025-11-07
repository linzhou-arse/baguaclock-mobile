# 设置Git编辑器为非交互式
$env:GIT_EDITOR = "echo"
$env:EDITOR = "echo"

# 配置Git编辑器
git config core.editor echo

# 完成合并提交（如果有合并）
if (Test-Path ".git/MERGE_HEAD") {
    Write-Host "检测到合并状态，正在完成合并..."
    git commit --no-edit -m "Merge remote changes"
}

# 推送到GitHub
Write-Host "正在推送到GitHub..."
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 推送成功！" -ForegroundColor Green
} else {
    Write-Host "❌ 推送失败，请检查错误信息" -ForegroundColor Red
}

