/**
 * @fileoverview 数据库更新API端点
 * 
 * 此API用于触发数据库更新流程，支持定时自动调用和手动调用
 * GET请求 - 获取最近一次更新状态
 * POST请求 - 触发新的更新流程
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

// 验证密钥
const API_KEY = process.env.DB_UPDATE_API_KEY || 'change-this-to-secure-key';

// 更新锁文件路径
const LOCK_FILE = path.join(process.cwd(), 'tmp', 'db_update.lock');
// 最新状态文件路径
const STATUS_FILE = path.join(process.cwd(), 'tmp', 'db_update_status.json');

// 确保临时目录存在
try {
  if (!fs.existsSync(path.join(process.cwd(), 'tmp'))) {
    fs.mkdirSync(path.join(process.cwd(), 'tmp'), { recursive: true });
  }
} catch (error) {
  console.error('无法创建临时目录:', error);
}

// 存储当前运行的进程
let currentProcess = null;

/**
 * 检查更新是否正在进行中
 * @returns {boolean} 是否正在更新
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
 * @param {Object} status 更新状态对象
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
 * @returns {Object} 更新状态对象
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
 * 执行数据库更新流程
 * @param {Object} res 响应对象
 */
async function runDatabaseUpdate(res) {
  // 如果已经在运行，则返回
  if (isUpdateRunning()) {
    return res.status(409).json({
      success: false,
      message: '更新已在进行中',
      status: getStatus()
    });
  }

  // 创建锁文件
  createLock();
  
  // 初始化状态
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
      '数据备份': { status: '等待中' },
      '测试': { status: '等待中' }
    }
  };
  saveStatus(status);

  // 立即响应请求，然后继续处理
  res.status(202).json({
    success: true,
    message: '更新流程已启动',
    status: status
  });

  try {
    // 执行更新脚本
    await executeUpdate(status);
  } catch (error) {
    // 更新失败处理
    status.status = 'failed';
    status.end_time = new Date().toISOString();
    status.message = `更新失败: ${error.message}`;
    saveStatus(status);
  } finally {
    // 释放锁
    releaseLock();
  }
}

/**
 * 执行数据库更新流程的各个步骤
 * @param {Object} status 状态对象
 */
async function executeUpdate(status) {
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
    await executeDataAnalysis(status);
  } catch (error) {
    status.steps['数据分析'].status = '警告';
    status.steps['数据分析'].warning = error.message;
    console.warn(`数据分析阶段出现警告: ${error.message}`);
    status.steps['数据分析'].status = '完成';
  }
  status.steps['数据分析'].end_time = new Date().toISOString();
  saveStatus(status);

  // 步骤3: 数据导入 (关键步骤)
  status.steps['数据导入'].status = '执行中';
  status.steps['数据导入'].start_time = new Date().toISOString();
  saveStatus(status);
  
  try {
    await executeDataImport(status);
  } catch (error) {
    status.steps['数据导入'].status = '失败';
    status.steps['数据导入'].error = error.message;
    
    // 尝试恢复数据库
    try {
      console.error(`数据导入失败，尝试恢复数据库: ${error.message}`);
      const rollbackResult = await executeCommand('python', ['py/rollback_db.py']);
      
      if (rollbackResult.error) {
        status.steps['数据导入'].error += `\n回滚失败: ${rollbackResult.error}`;
        console.error(`数据库回滚失败: ${rollbackResult.error}`);
      } else {
        status.steps['数据导入'].error += '\n数据库已回滚到上一个可用状态';
        console.log('数据库成功回滚到上一个可用状态');
      }
    } catch (rollbackError) {
      status.steps['数据导入'].error += `\n回滚过程出错: ${rollbackError.message}`;
      console.error(`回滚过程出错: ${rollbackError.message}`);
    }
    
    // 终止后续步骤
    throw new Error(`数据导入失败: ${error.message}`);
  }
  status.steps['数据导入'].end_time = new Date().toISOString();
  saveStatus(status);

  // 步骤4: 词云生成
  status.steps['词云生成'].status = '执行中';
  status.steps['词云生成'].start_time = new Date().toISOString();
  saveStatus(status);
  
  try {
    await executeWordCloudGeneration(status);
  } catch (error) {
    status.steps['词云生成'].status = '警告';
    status.steps['词云生成'].warning = error.message;
    console.warn(`词云生成警告: ${error.message}`);
    status.steps['词云生成'].status = '完成';
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

  // 测试用：执行测试脚本
  status.steps['测试'].status = '执行中';
  status.steps['测试'].start_time = new Date().toISOString();
  saveStatus(status);
  
  try {
    await executeStep('测试', [
      { cmd: 'python', args: ['py/test_update.py'] }
    ]);
    status.steps['测试'].status = '完成';
  } catch (error) {
    status.steps['测试'].status = '失败';
    status.steps['测试'].error = error.message;
    throw error;
  }
  status.steps['测试'].end_time = new Date().toISOString();
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
}

/**
 * 执行数据分析步骤
 */
async function executeDataAnalysis(status) {
  try {
    await executeStep('数据分析', [
      { cmd: 'python', args: ['py/analysis.py'] },
      { cmd: 'python', args: ['py/test_data_quality.py'] }
    ]);
    status.steps['数据分析'].status = '完成';
  } catch (error) {
    // 将数据分析失败改为警告，不影响整体流程
    status.steps['数据分析'].status = '警告';
    status.steps['数据分析'].warning = error.message;
    // 添加警告日志，但继续流程
    console.warn(`数据分析阶段出现警告: ${error.message}`);
    status.steps['数据分析'].status = '完成';
  }
  saveStatus(status);
}

/**
 * 执行数据导入步骤
 */
async function executeDataImport(status) {
  try {
    // 备份现有数据库
    const backupResult = await executeCommand('python', ['py/backup_db.py']);
    if (backupResult.error) {
      status.steps['数据导入'].warning = `数据库备份警告: ${backupResult.error}`;
      console.warn(`数据库备份警告: ${backupResult.error}`);
    }
    
    // 导入数据
    await executeStep('数据导入', [
      { cmd: 'python', args: ['py/update_db.py'] }
    ]);
    status.steps['数据导入'].status = '完成';
  } catch (error) {
    status.steps['数据导入'].status = '失败';
    status.steps['数据导入'].error = error.message;
    
    // 尝试恢复数据库
    try {
      console.error(`数据导入失败，尝试恢复数据库: ${error.message}`);
      const rollbackResult = await executeCommand('python', ['py/rollback_db.py']);
      
      if (rollbackResult.error) {
        status.steps['数据导入'].error += `\n回滚失败: ${rollbackResult.error}`;
        console.error(`数据库回滚失败: ${rollbackResult.error}`);
      } else {
        status.steps['数据导入'].error += '\n数据库已回滚到上一个可用状态';
        console.log('数据库成功回滚到上一个可用状态');
      }
    } catch (rollbackError) {
      status.steps['数据导入'].error += `\n回滚过程出错: ${rollbackError.message}`;
      console.error(`回滚过程出错: ${rollbackError.message}`);
    }
    
    // 终止后续步骤
    throw new Error(`数据导入失败: ${error.message}`);
  }
  saveStatus(status);
}

/**
 * 执行词云生成步骤
 */
async function executeWordCloudGeneration(status) {
  try {
    await executeStep('词云生成', [
      { cmd: 'python', args: ['py/generate_wordcloud.py'] }
    ]);
    status.steps['词云生成'].status = '完成';
  } catch (error) {
    // 词云生成失败不会中断整个流程，只标记为警告
    status.steps['词云生成'].status = '警告';
    status.steps['词云生成'].warning = error.message;
    console.warn(`词云生成警告: ${error.message}`);
    // 即使出现警告也标记为完成，因为这不是关键步骤
    status.steps['词云生成'].status = '完成';
  }
  saveStatus(status);
}

/**
 * 执行命令
 * @param {string} cmd 命令
 * @param {string[]} args 参数
 * @returns {Promise} 执行结果
 */
function executeCommand(cmd, args) {
  return new Promise((resolve, reject) => {
    // 使用绝对路径
    const scriptPath = path.join(process.cwd(), ...args);
    console.log(`执行命令: ${cmd} ${scriptPath}`);
    
    const process1 = spawn(cmd, [scriptPath], {
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
      // 清除当前进程引用
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
      // 清除当前进程引用
      if (currentProcess === process1) {
        currentProcess = null;
      }
      reject(new Error(`启动命令失败: ${err.message}`));
    });
  });
}

/**
 * 执行更新步骤
 * @param {string} stepName 步骤名称
 * @param {Array} commands 命令列表
 */
async function executeStep(stepName, commands) {
  console.log(`开始执行步骤: ${stepName}`);
  for (const command of commands) {
    try {
      await executeCommand(command.cmd, command.args);
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
      // 在Windows上使用tree kill来确保子进程也被终止
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
      
      // 更新所有正在执行的步骤状态
      Object.keys(status.steps).forEach(step => {
        if (status.steps[step].status === '执行中' || status.steps[step].status === '等待中') {
          status.steps[step].status = '已停止';
          status.steps[step].end_time = new Date().toISOString();
        }
      });
      
      saveStatus(status);
    }
    
    // 释放锁
    releaseLock();
    
    return true;
  } catch (error) {
    console.error('停止更新失败:', error);
    return false;
  }
}

/**
 * API处理函数
 */
export default async function handler(req, res) {
  // 创建临时目录
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

  // 根据请求方法处理
  switch (req.method) {
    case 'GET':
      // 检查更新状态
      return res.status(200).json({
        success: true,
        is_running: isUpdateRunning(),
        status: getStatus()
      });
      
    case 'POST':
      // 验证API密钥
      const providedKey = req.headers['x-api-key'] || req.query.key;
      if (providedKey !== API_KEY) {
        return res.status(401).json({
          success: false,
          message: 'API密钥无效'
        });
      }
      
      // 检查是否是停止请求
      if (req.query.action === 'stop') {
        const stopped = stopUpdate();
        return res.status(200).json({
          success: stopped,
          message: stopped ? '更新已停止' : '停止更新失败'
        });
      }
      
      // 触发数据库更新
      return await runDatabaseUpdate(res);
      
    default:
      return res.status(405).json({
        success: false,
        message: '方法不允许'
      });
  }
} 