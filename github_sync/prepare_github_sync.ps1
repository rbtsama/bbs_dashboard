# 准备GitHub同步文件列表脚本
# 这个脚本将生成两个文件列表：
# 1. github_files_to_sync.txt - 需要同步到GitHub的文件列表
# 2. github_files_to_ignore.txt - 不需要同步到GitHub的文件列表

# 设置日志文件
$logFile = "github_sync/sync_preparation.log"
$filesListToSync = "github_sync/github_files_to_sync.txt"
$filesListToIgnore = "github_sync/github_files_to_ignore.txt"

# 清空现有文件
"" | Out-File -FilePath $logFile
"" | Out-File -FilePath $filesListToSync
"" | Out-File -FilePath $filesListToIgnore

function Write-Log {
    param (
        [string]$message
    )
    $timeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timeStamp - $message" | Out-File -FilePath $logFile -Append
    Write-Host $message
}

Write-Log "Starting GitHub sync preparation..."

# 需要同步的文件夹
$foldersToSync = @(
    "backend",
    "py",
    "sql",
    "docs",
    "frontend",
    "pages",
    "styles",
    "data",
    "scripts"
)

# 需要同步的根目录文件类型
$filesToSync = @(
    "*.py",
    "*.md",
    "*.js",
    "*.json",
    "*.sh",
    "*.bat",
    "*.css",
    "*.html",
    "*.txt",
    ".env.local",
    ".gitignore",
    "requirements.txt"
)

# 不同步的文件夹
$foldersToIgnore = @(
    "node_modules",
    "__pycache__",
    ".next",
    ".vscode",
    ".git",
    ".cursor",
    "tmp",
    "logs"
)

# 不同步的文件类型
$filesToIgnore = @(
    "*.pyc",
    "*.pyo",
    "*.db",
    "*.sqlite3",
    "*.log",
    "*.bak",
    "*.bak_*",
    "*.to_delete",
    "*.temp_*"
)

# 特殊规则：data目录下的Excel和CSV文件也需要同步
$dataFilesToSync = @(
    "data/*.xlsx",
    "data/*.csv",
    "data/processed/*.xlsx",
    "data/processed/*.csv",
    "data/raw/*.xlsx",
    "data/raw/*.csv",
    "data/config/*.*"
)

Write-Log "Collecting files to sync..."

# 收集需要同步的文件
foreach ($folder in $foldersToSync) {
    if (Test-Path $folder) {
        Get-ChildItem -Path $folder -Recurse -File | ForEach-Object {
            # 检查文件是否在忽略列表中
            $shouldIgnore = $false
            foreach ($ignoreFolder in $foldersToIgnore) {
                if ($_.FullName -like "*\$ignoreFolder\*") {
                    $shouldIgnore = $true
                    break
                }
            }
            
            foreach ($ignoreExt in $filesToIgnore) {
                if ($_.Name -like $ignoreExt) {
                    $shouldIgnore = $true
                    break
                }
            }
            
            if (-not $shouldIgnore) {
                $relativePath = $_.FullName.Substring($PWD.Path.Length + 1)
                $relativePath | Out-File -FilePath $filesListToSync -Append
            }
            else {
                $relativePath = $_.FullName.Substring($PWD.Path.Length + 1)
                $relativePath | Out-File -FilePath $filesListToIgnore -Append
            }
        }
    }
    else {
        Write-Log "Warning: Folder '$folder' does not exist, skipped"
    }
}

# 收集根目录需要同步的文件
foreach ($filePattern in $filesToSync) {
    Get-ChildItem -Path $filePattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        $relativePath = $_.FullName.Substring($PWD.Path.Length + 1)
        $relativePath | Out-File -FilePath $filesListToSync -Append
    }
}

# 特殊处理：data目录下的Excel和CSV文件
foreach ($dataFilePattern in $dataFilesToSync) {
    Get-ChildItem -Path $dataFilePattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        $relativePath = $_.FullName.Substring($PWD.Path.Length + 1)
        $relativePath | Out-File -FilePath $filesListToSync -Append
        # 从忽略列表中移除这个文件（如果存在）
        $content = Get-Content $filesListToIgnore -ErrorAction SilentlyContinue
        if ($content -contains $relativePath) {
            $content = $content | Where-Object { $_ -ne $relativePath }
            $content | Out-File -FilePath $filesListToIgnore
        }
    }
}

# 统计结果
$syncCount = (Get-Content $filesListToSync | Measure-Object -Line).Lines
$ignoreCount = (Get-Content $filesListToIgnore | Measure-Object -Line).Lines

Write-Log "Found $syncCount files to sync"
Write-Log "Found $ignoreCount files to ignore"

# 生成摘要报告
$summaryFile = "github_sync/sync_summary.md"
"# GitHub Sync Preparation Report" | Out-File -FilePath $summaryFile
"" | Out-File -FilePath $summaryFile -Append
"## Sync Statistics" | Out-File -FilePath $summaryFile -Append
"" | Out-File -FilePath $summaryFile -Append
"- Files to sync: $syncCount" | Out-File -FilePath $summaryFile -Append
"- Files to ignore: $ignoreCount" | Out-File -FilePath $summaryFile -Append
"" | Out-File -FilePath $summaryFile -Append

"## Folders to Sync" | Out-File -FilePath $summaryFile -Append
"" | Out-File -FilePath $summaryFile -Append
foreach ($folder in $foldersToSync) {
    "- $folder/" | Out-File -FilePath $summaryFile -Append
}
"" | Out-File -FilePath $summaryFile -Append

"## Special Notes" | Out-File -FilePath $summaryFile -Append
"" | Out-File -FilePath $summaryFile -Append
"- Excel and CSV files in data directory will be synced, which is important for Vercel deployment" | Out-File -FilePath $summaryFile -Append
"- All Python source code files (.py) will be synced" | Out-File -FilePath $summaryFile -Append
"- Configuration files like package.json, requirements.txt will be synced" | Out-File -FilePath $summaryFile -Append
"- Temporary files, cache files and compiled files will be ignored" | Out-File -FilePath $summaryFile -Append
"" | Out-File -FilePath $summaryFile -Append

"## Files and Directories to Ignore" | Out-File -FilePath $summaryFile -Append
"" | Out-File -FilePath $summaryFile -Append
foreach ($folder in $foldersToIgnore) {
    "- $folder/" | Out-File -FilePath $summaryFile -Append
}
"" | Out-File -FilePath $summaryFile -Append
"File Types:" | Out-File -FilePath $summaryFile -Append
foreach ($fileType in $filesToIgnore) {
    "- $fileType" | Out-File -FilePath $summaryFile -Append
}

Write-Log "Summary report generated: $summaryFile"
Write-Log "Preparation completed!" 