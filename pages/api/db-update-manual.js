/**
 * @fileoverview 手动数据库更新API端点
 * 
 * 此API用于手动触发数据库更新流程，使用web界面而不是CRON触发
 * 主要用于管理员手动更新数据库
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

// 验证密钥
const ADMIN_KEY = process.env.NEXT_PUBLIC_ADMIN_KEY || 'admin123';

// 更新锁文件路径
const LOCK_FILE = path.join(process.cwd(), 'tmp', 'db_update.lock');
// 最新状态文件路径
const STATUS_FILE = path.join(process.cwd(), 'tmp', 'db_update_status.json');

// 存储当前运行的进程
let currentProcess = null;

/**
 * 检查更新是否正在进行中
 */
function isUpdateRunning() {
  try {
    return fs.existsSync(LOCK_FILE);
  } catch (error) {
    console.error('检查锁文件失败:', error);
    return false;
  }
}

/**
 * 创建更新锁
 */
function createLock() {
  try {
    fs.writeFileSync(LOCK_FILE, new Date().toISOString());
  } catch (error) {
    console.error('创建锁文件失败:', error);
  }
}

/**
 * 释放更新锁
 */
function releaseLock() {
  try {
    if (fs.existsSync(LOCK_FILE)) {
      fs.unlinkSync(LOCK_FILE);
    }
  } catch (error) {
    console.error('释放锁文件失败:', error);
  }
}

/**
 * 保存更新状态
 */
function saveStatus(status) {
  try {
    fs.writeFileSync(STATUS_FILE, JSON.stringify(status, null, 2));
  } catch (error) {
    console.error('保存状态文件失败:', error);
  }
}

/**
 * 获取最新更新状态
 */
function getStatus() {
  try {
    if (fs.existsSync(STATUS_FILE)) {
      return JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
    }
    return { status: 'never_run', last_run: null, message: '从未执行过更新' };
  } catch (error) {
    console.error('读取状态文件失败:', error);
    return { status: 'error', message: '读取状态文件失败' };
  }
}

/**
 * 执行命令
 */
function executeCommand(cmd, args, extraArgs = []) {
  return new Promise((resolve, reject) => {
    // 处理路径和参数
    let scriptPath;
    let allArgs = [];
    
    if (args && args.length > 0) {
      scriptPath = path.join(process.cwd(), ...args);
      allArgs.push(scriptPath);
    }
    
    // 添加额外参数
    if (extraArgs && extraArgs.length > 0) {
      allArgs = allArgs.concat(extraArgs);
    }
    
    console.log(`执行命令: ${cmd} ${allArgs.join(' ')}`);
    
    const process1 = spawn(cmd, allArgs, {
      cwd: process.cwd(),
      env: { 
        ...process.env, 
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1',
        PYTHONUTF8: '1'
      }
    });

    // 存储当前进程
    currentProcess = process1;

    let output = '';
    let errorOutput = '';

    process1.stdout.on('data', (data) => {
      const text = data.toString('utf-8');
      output += text;
      console.log(`输出: ${text}`);
    });

    process1.stderr.on('data', (data) => {
      const text = data.toString('utf-8');
      errorOutput += text;
      console.error(`错误: ${text}`);
    });

    process1.on('close', (code) => {
      if (currentProcess === process1) {
        currentProcess = null;
      }
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`命令执行失败 (${code}): ${errorOutput || output}`));
      }
    });

    process1.on('error', (err) => {
      if (currentProcess === process1) {
        currentProcess = null;
      }
      reject(new Error(`启动命令失败: ${err.message}`));
    });
  });
}

/**
 * 执行更新步骤
 */
async function executeStep(stepName, commands) {
  console.log(`开始执行步骤: ${stepName}`);
  for (const command of commands) {
    try {
      await executeCommand(command.cmd, command.args, command.extraArgs);
    } catch (error) {
      console.error(`步骤 ${stepName} 执行失败:`, error);
      throw error;
    }
  }
}

/**
 * 停止更新进程
 */
function stopUpdate() {
  try {
    // 终止当前运行的进程
    if (currentProcess) {
      try {
        process.kill(-currentProcess.pid);
      } catch (e) {
        try {
          currentProcess.kill();
        } catch (e2) {
          console.error('终止进程失败:', e2);
        }
      }
      currentProcess = null;
    }

    // 更新状态
    const status = getStatus();
    if (status) {
      status.status = 'stopped';
      status.end_time = new Date().toISOString();
      status.message = '更新已手动停止';
      
      Object.keys(status.steps).forEach(step => {
        if (status.steps[step].status === '执行中' || status.steps[step].status === '等待中') {
          status.steps[step].status = '已停止';
          status.steps[step].end_time = new Date().toISOString();
        }
      });
      
      saveStatus(status);
    }
    
    releaseLock();
    return true;
  } catch (error) {
    console.error('停止更新失败:', error);
    return false;
  }
}

/**
 * 执行数据库更新
 */
async function runDatabaseUpdate(res) {
  if (isUpdateRunning()) {
    return res.status(409).json({
      success: false,
      message: '更新已在进行中',
      status: getStatus()
    });
  }

  createLock();
  
  const startTime = new Date();
  const status = {
    status: 'running',
    start_time: startTime.toISOString(),
    message: '更新进行中',
    steps: {
      '数据预处理': { status: '等待中' },
      '数据分析': { status: '等待中' },
      '数据导入': { status: '等待中' },
      '词云生成': { status: '等待中' },
      '数据备份': { status: '等待中' }
    }
  };
  saveStatus(status);

  res.status(202).json({
    success: true,
    message: '更新流程已启动',
    status: status
  });

  try {
    // 步骤1: 数据预处理
    status.steps['数据预处理'].status = '执行中';
    status.steps['数据预处理'].start_time = new Date().toISOString();
    saveStatus(status);
    
    try {
      await executeStep('数据预处理', [
        { cmd: 'python', args: ['py/post.py'] },
        { cmd: 'python', args: ['py/update.py'] },
        { cmd: 'python', args: ['py/detail.py'] },
        { cmd: 'python', args: ['py/action.py'] },
        { cmd: 'python', args: ['py/car_info.py'] }
      ]);
      status.steps['数据预处理'].status = '完成';
    } catch (error) {
      status.steps['数据预处理'].status = '失败';
      status.steps['数据预处理'].error = error.message;
      // 非关键步骤失败，继续执行
    }
    status.steps['数据预处理'].end_time = new Date().toISOString();
    saveStatus(status);

    // 步骤2: 数据分析
    status.steps['数据分析'].status = '执行中';
    status.steps['数据分析'].start_time = new Date().toISOString();
    saveStatus(status);
    
    try {
      await executeStep('数据分析', [
        { cmd: 'python', args: ['py/analysis.py'] },
        { cmd: 'python', args: ['py/test_data_quality.py'] }
      ]);
      status.steps['数据分析'].status = '完成';
    } catch (error) {
      status.steps['数据分析'].status = '失败';
      status.steps['数据分析'].error = error.message;
      // 非关键步骤失败，继续执行
    }
    status.steps['数据分析'].end_time = new Date().toISOString();
    saveStatus(status);

    // 步骤3: 数据导入 (关键步骤)
    status.steps['数据导入'].status = '执行中';
    status.steps['数据导入'].start_time = new Date().toISOString();
    saveStatus(status);
    
    try {
      // 数据库备份 (提前备份以便回滚)
      await executeStep('数据库备份', [
        { cmd: 'python', args: ['py/backup_db.py'], extraArgs: ['--before-update'] }
      ]);
      
      await executeStep('数据导入', [
        { cmd: 'python', args: ['py/update_db.py'] },
        { cmd: 'python', args: ['py/check_db_structure.py'] }
      ]);
      status.steps['数据导入'].status = '完成';
    } catch (error) {
      status.steps['数据导入'].status = '失败';
      status.steps['数据导入'].error = error.message;
      
      // 关键步骤失败，尝试回滚
      try {
        await executeStep('数据回滚', [
          { cmd: 'python', args: ['py/rollback_db.py'] }
        ]);
        status.steps['数据导入'].rollback = '成功';
      } catch (rollbackError) {
        status.steps['数据导入'].rollback = `失败: ${rollbackError.message}`;
      }
      
      // 关键步骤失败，中止后续步骤
      status.steps['数据导入'].end_time = new Date().toISOString();
      status.end_time = new Date().toISOString();
      status.status = 'failed';
      status.message = `数据导入失败: ${error.message}`;
      saveStatus(status);
      throw error; // 中断流程
    }
    status.steps['数据导入'].end_time = new Date().toISOString();
    saveStatus(status);

    // 步骤4: 词云生成
    status.steps['词云生成'].status = '执行中';
    status.steps['词云生成'].start_time = new Date().toISOString();
    saveStatus(status);
    
    try {
      await executeStep('词云生成', [
        { cmd: 'python', args: ['py/generate_wordcloud.py'] }
      ]);
      status.steps['词云生成'].status = '完成';
    } catch (error) {
      status.steps['词云生成'].status = '失败';
      status.steps['词云生成'].error = error.message;
      // 非关键步骤失败，继续执行
    }
    status.steps['词云生成'].end_time = new Date().toISOString();
    saveStatus(status);

    // 步骤5: 数据备份
    status.steps['数据备份'].status = '执行中';
    status.steps['数据备份'].start_time = new Date().toISOString();
    saveStatus(status);
    
    try {
      await executeStep('数据备份', [
        { cmd: 'python', args: ['py/backup_db.py'] }
      ]);
      status.steps['数据备份'].status = '完成';
    } catch (error) {
      status.steps['数据备份'].status = '失败';
      status.steps['数据备份'].error = error.message;
      // 非关键步骤失败，不影响整体状态
    }
    status.steps['数据备份'].end_time = new Date().toISOString();
    saveStatus(status);

    // 更新最终状态
    const failedSteps = Object.keys(status.steps).filter(step => 
      status.steps[step].status === '失败'
    );
    
    status.end_time = new Date().toISOString();
    if (failedSteps.length === 0) {
      status.status = 'success';
      status.message = '更新成功完成';
    } else {
      status.status = 'partial_success';
      status.message = `更新部分成功，${failedSteps.length}个步骤失败: ${failedSteps.join(', ')}`;
    }
    
    saveStatus(status);
  } catch (error) {
    // 更新失败处理
    status.status = 'failed';
    status.end_time = new Date().toISOString();
    status.message = `更新失败: ${error.message}`;
    saveStatus(status);
  } finally {
    releaseLock();
  }
}

/**
 * API处理函数
 */
export default async function handler(req, res) {
  try {
    if (!fs.existsSync(path.join(process.cwd(), 'tmp'))) {
      fs.mkdirSync(path.join(process.cwd(), 'tmp'), { recursive: true });
    }
    
    if (!fs.existsSync(path.join(process.cwd(), 'logs'))) {
      fs.mkdirSync(path.join(process.cwd(), 'logs'), { recursive: true });
    }
  } catch (error) {
    return res.status(500).json({ 
      success: false, 
      message: '无法创建所需目录',
      error: error.message
    });
  }

  switch (req.method) {
    case 'GET':
      return res.status(200).json({
        success: true,
        is_running: isUpdateRunning(),
        status: getStatus()
      });
      
    case 'POST':
      const providedKey = req.headers['x-admin-key'] || req.body?.adminKey;
      if (providedKey !== ADMIN_KEY) {
        return res.status(401).json({
          success: false,
          message: '管理员密钥无效'
        });
      }
      
      if (req.query.action === 'stop') {
        const stopped = stopUpdate();
        return res.status(200).json({
          success: stopped,
          message: stopped ? '更新已停止' : '停止更新失败'
        });
      }
      
      return await runDatabaseUpdate(res);
      
    default:
      return res.status(405).json({
        success: false,
        message: '方法不允许'
      });
  }
} 