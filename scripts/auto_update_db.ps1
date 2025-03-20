# 数据库自动更新脚本
# 此脚本执行完整的数据库更新流程，从原始数据处理到最终数据库更新
# 设计为在每天凌晨3点（加州时间）自动运行

# 设置错误处理
$ErrorActionPreference = "Stop"

# 配置日志记录
$logFolder = "$PSScriptRoot\..\logs"
$logFile = "$logFolder\auto_update_db_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 确保日志目录存在
if (!(Test-Path $logFolder)) {
    New-Item -ItemType Directory -Path $logFolder -Force | Out-Null
}

# 日志记录函数
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    Write-Host $logEntry
}

# 设置工作目录为项目根目录
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot
Write-Log "设置工作目录: $projectRoot"

# 创建一个用于记录每个步骤状态的对象
$processStatus = @{
    "数据预处理" = @{
        "开始时间" = $null
        "结束时间" = $null
        "状态" = "等待中"
        "详情" = ""
    }
    "数据分析" = @{
        "开始时间" = $null
        "结束时间" = $null
        "状态" = "等待中"
        "详情" = ""
    }
    "数据导入" = @{
        "开始时间" = $null
        "结束时间" = $null
        "状态" = "等待中"
        "详情" = ""
    }
    "词云生成" = @{
        "开始时间" = $null
        "结束时间" = $null
        "状态" = "等待中"
        "详情" = ""
    }
    "数据备份" = @{
        "开始时间" = $null
        "结束时间" = $null
        "状态" = "等待中"
        "详情" = ""
    }
}

# 步骤执行函数
function Execute-Step {
    param (
        [string]$StepName,
        [scriptblock]$ScriptBlock
    )
    
    Write-Log "开始执行步骤: $StepName" "INFO"
    $processStatus[$StepName]["开始时间"] = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $processStatus[$StepName]["状态"] = "执行中"
    
    try {
        & $ScriptBlock
        $processStatus[$StepName]["状态"] = "完成"
        $processStatus[$StepName]["结束时间"] = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Write-Log "步骤 '$StepName' 成功完成" "INFO"
        return $true
    }
    catch {
        $errorMessage = $_.Exception.Message
        $processStatus[$StepName]["状态"] = "失败"
        $processStatus[$StepName]["详情"] = $errorMessage
        $processStatus[$StepName]["结束时间"] = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Write-Log "步骤 '$StepName' 执行失败: $errorMessage" "ERROR"
        return $false
    }
}

# 第1步：数据预处理
$result = Execute-Step "数据预处理" {
    # 处理新发帖数据
    Write-Log "执行post.py - 处理新发帖数据" "INFO"
    python py/post.py
    if ($LASTEXITCODE -ne 0) { throw "处理新发帖数据失败，退出代码: $LASTEXITCODE" }
    
    # 处理帖子更新数据
    Write-Log "执行update.py - 处理帖子更新数据" "INFO"
    python py/update.py
    if ($LASTEXITCODE -ne 0) { throw "处理帖子更新数据失败，退出代码: $LASTEXITCODE" }
    
    # 处理帖子详情数据
    Write-Log "执行detail.py - 处理帖子详情数据" "INFO"
    python py/detail.py
    if ($LASTEXITCODE -ne 0) { throw "处理帖子详情数据失败，退出代码: $LASTEXITCODE" }
    
    # 生成帖子动态记录
    Write-Log "执行action.py - 生成帖子动态记录" "INFO"
    python py/action.py
    if ($LASTEXITCODE -ne 0) { throw "生成帖子动态记录失败，退出代码: $LASTEXITCODE" }
    
    # 处理车辆信息数据
    Write-Log "执行car_info.py - 处理车辆信息数据" "INFO"
    python py/car_info.py
    if ($LASTEXITCODE -ne 0) { throw "处理车辆信息数据失败，退出代码: $LASTEXITCODE" }
}

# 如果前一步失败，记录但继续执行下一步
if (!$result) {
    Write-Log "数据预处理步骤失败，但将继续执行后续步骤" "WARNING"
}

# 第2步：数据分析
$result = Execute-Step "数据分析" {
    # 执行数据分析脚本
    Write-Log "执行analysis.py - 数据分析" "INFO"
    python py/analysis.py
    if ($LASTEXITCODE -ne 0) { throw "数据分析失败，退出代码: $LASTEXITCODE" }
    
    # 执行数据质量测试
    Write-Log "执行test_data_quality.py - 数据质量测试" "INFO"
    python py/test_data_quality.py
    if ($LASTEXITCODE -ne 0) { throw "数据质量测试失败，退出代码: $LASTEXITCODE" }
}

# 如果前一步失败，记录但继续执行下一步
if (!$result) {
    Write-Log "数据分析步骤失败，但将继续执行后续步骤" "WARNING"
}

# 第3步：数据导入
$result = Execute-Step "数据导入" {
    # 执行数据库更新脚本
    Write-Log "执行update_db.py - 数据库更新" "INFO"
    python py/update_db.py
    if ($LASTEXITCODE -ne 0) { throw "数据库更新失败，退出代码: $LASTEXITCODE" }
    
    # 检查数据库结构
    Write-Log "执行check_db_structure.py - 检查数据库结构" "INFO"
    python py/check_db_structure.py
    if ($LASTEXITCODE -ne 0) { throw "数据库结构检查失败，退出代码: $LASTEXITCODE" }
}

# 如果数据导入失败，停止后续步骤
if (!$result) {
    Write-Log "数据导入步骤失败，停止后续步骤" "ERROR"
    Exit 1
}

# 第4步：词云生成
$result = Execute-Step "词云生成" {
    # 生成词云
    Write-Log "执行generate_wordcloud.py - 生成词云" "INFO"
    python py/generate_wordcloud.py
    if ($LASTEXITCODE -ne 0) { throw "词云生成失败，退出代码: $LASTEXITCODE" }
}

# 如果前一步失败，记录但继续执行下一步
if (!$result) {
    Write-Log "词云生成步骤失败，但将继续执行后续步骤" "WARNING"
}

# 第5步：数据备份
$result = Execute-Step "数据备份" {
    # 创建数据库备份
    Write-Log "执行backup_db.py - 创建数据库备份" "INFO"
    python py/backup_db.py
    if ($LASTEXITCODE -ne 0) { throw "数据库备份失败，退出代码: $LASTEXITCODE" }
}

# 如果前一步失败，记录但继续
if (!$result) {
    Write-Log "数据备份步骤失败" "WARNING"
}

# 生成最终状态报告
Write-Log "==================== 执行状态报告 ====================" "INFO"
foreach ($step in $processStatus.Keys) {
    $status = $processStatus[$step]
    $duration = "N/A"
    if ($status["开始时间"] -and $status["结束时间"]) {
        $start = [DateTime]::ParseExact($status["开始时间"], "yyyy-MM-dd HH:mm:ss", $null)
        $end = [DateTime]::ParseExact($status["结束时间"], "yyyy-MM-dd HH:mm:ss", $null)
        $duration = "{0:hh\:mm\:ss}" -f ($end - $start)
    }
    
    Write-Log "$step - 状态: $($status["状态"]), 耗时: $duration" "INFO"
    if ($status["详情"]) {
        Write-Log "  详情: $($status["详情"])" "INFO"
    }
}
Write-Log "=====================================================" "INFO"

# 返回最终执行状态
$failedSteps = $processStatus.Keys | Where-Object { $processStatus[$_]["状态"] -eq "失败" }
if ($failedSteps.Count -gt 0) {
    Write-Log "自动更新过程中有 $($failedSteps.Count) 个步骤失败" "ERROR"
    Exit 1
} else {
    Write-Log "自动更新过程全部完成" "INFO"
    Exit 0
} 