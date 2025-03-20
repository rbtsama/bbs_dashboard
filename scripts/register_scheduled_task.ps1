# 定时任务注册脚本
# 此脚本用于注册自动更新数据库的Windows计划任务
# 设定为每天凌晨3点（加州时间/PDT）执行

# 需要以管理员权限运行此脚本

# 检查是否以管理员权限运行
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "此脚本需要管理员权限运行。请以管理员身份重新运行。" -ForegroundColor Red
    exit 1
}

# 获取项目目录的绝对路径
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$scriptPath = Join-Path -Path $projectRoot -ChildPath "scripts\auto_update_db.ps1"

# 确保脚本存在
if (-not (Test-Path $scriptPath)) {
    Write-Host "自动更新脚本不存在: $scriptPath" -ForegroundColor Red
    exit 1
}

# 任务名称
$taskName = "BBS数据库每日更新"

# 任务描述
$taskDescription = "每天凌晨3点（加州时间）自动执行BBS数据库更新"

# 创建动作对象 - 运行PowerShell脚本
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -WorkingDirectory $projectRoot

# 创建触发器对象 - 每天凌晨3点（PDT，即UTC-7）
# Windows计划任务使用本地时间，需要根据当前时区进行调整
# 如果系统时区不是PDT（UTC-7），需要调整时间
$currentTimeZone = (Get-TimeZone).Id
$PDTOffset = -7 # PDT的UTC偏移量为-7小时

# 获取当前时区的UTC偏移量（小时）
$currentOffset = (Get-TimeZone).BaseUtcOffset.TotalHours

# 计算时差（小时）
$hourDifference = $PDTOffset - $currentOffset

# 计算本地对应的时间（加州凌晨3点）
$localHour = (3 - $hourDifference) % 24
if ($localHour -lt 0) {
    $localHour += 24
}

# 创建每天执行的触发器
$trigger = New-ScheduledTaskTrigger -Daily -At "$($localHour):00"

# 设置任务选项
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew

# 创建任务主体对象，使用系统账户运行
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# 检查任务是否已存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    # 如果任务已存在，则更新它
    Write-Host "更新已存在的任务: $taskName" -ForegroundColor Yellow
    Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
} else {
    # 如果任务不存在，则创建新任务
    Write-Host "创建新任务: $taskName" -ForegroundColor Green
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
}

# 显示本地执行时间和PDT执行时间的对应关系
Write-Host "任务设置完成！" -ForegroundColor Green
Write-Host "任务将在每天本地时间 $($localHour):00 执行，对应加州时间（PDT）凌晨3:00" -ForegroundColor Cyan
Write-Host "当前本地时区: $currentTimeZone (UTC$($currentOffset -ge 0 ? '+' : '')$currentOffset)" -ForegroundColor Cyan
Write-Host "目标时区: 太平洋夏令时间 (UTC-7)" -ForegroundColor Cyan

# 显示任务详情
Get-ScheduledTask -TaskName $taskName | Format-List 