import { useState, useEffect } from 'react';
import Head from 'next/head';

/**
 * 数据库更新管理页面
 * 用于手动触发数据库更新和查看更新状态
 */
export default function DbUpdatePage() {
  // 状态管理
  const [isLoading, setIsLoading] = useState(true);
  const [updateStatus, setUpdateStatus] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState(null);
  const [adminKey, setAdminKey] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // 加载状态
  useEffect(() => {
    fetchStatus();
    // 每10秒自动刷新一次状态
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  // 获取更新状态
  const fetchStatus = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/db-update-manual');
      const data = await response.json();
      
      if (data.success) {
        setUpdateStatus(data.status);
        setIsRunning(data.is_running);
        setLogs(data.last_logs);
      } else {
        setErrorMessage(`获取状态失败: ${data.message}`);
      }
    } catch (error) {
      setErrorMessage(`获取状态错误: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 触发更新
  const triggerUpdate = async (e) => {
    e.preventDefault();
    
    if (!adminKey.trim()) {
      setErrorMessage('请输入管理员密钥');
      return;
    }
    
    try {
      setIsLoading(true);
      setErrorMessage('');
      setSuccessMessage('');
      
      const response = await fetch('/api/db-update-manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-key': adminKey
        },
        body: JSON.stringify({ adminKey })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccessMessage('数据库更新已成功触发');
        setAdminKey(''); // 清空密钥
        // 立即获取最新状态
        fetchStatus();
      } else {
        setErrorMessage(`触发更新失败: ${data.message}`);
      }
    } catch (error) {
      setErrorMessage(`触发更新错误: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 停止更新
  const stopUpdate = async () => {
    try {
      setIsLoading(true);
      setErrorMessage('');
      setSuccessMessage('');
      
      const response = await fetch('/api/db-update-manual?action=stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-key': adminKey
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccessMessage('更新已成功停止');
        // 立即获取最新状态
        fetchStatus();
      } else {
        setErrorMessage(`停止更新失败: ${data.message}`);
      }
    } catch (error) {
      setErrorMessage(`停止更新错误: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 格式化状态显示
  const formatStatus = (status) => {
    if (!status) return '未知';
    
    const statusMap = {
      'never_run': '从未运行',
      'running': '正在运行',
      'success': '成功完成',
      'partial_success': '部分成功',
      'failed': '失败'
    };
    
    return statusMap[status.status] || status.status;
  };

  // 格式化步骤状态显示
  const formatStepStatus = (status) => {
    if (!status) return '未知';
    
    const statusMap = {
      '等待中': 'bg-gray-200 text-gray-700',
      '执行中': 'bg-blue-200 text-blue-700',
      '完成': 'bg-green-200 text-green-700',
      '失败': 'bg-red-200 text-red-700',
      '警告': 'bg-yellow-200 text-yellow-700'
    };
    
    return (
      <span className={`px-2 py-1 rounded ${statusMap[status] || 'bg-gray-200 text-gray-700'}`}>
        {status}
      </span>
    );
  };

  // 计算运行时间
  const calculateRunTime = (step) => {
    if (!step || !step.start_time || !step.end_time) return '未知';
    
    const start = new Date(step.start_time);
    const end = new Date(step.end_time);
    const diff = (end - start) / 1000; // 秒
    
    if (diff < 60) {
      return `${diff.toFixed(1)}秒`;
    } else {
      const minutes = Math.floor(diff / 60);
      const seconds = Math.floor(diff % 60);
      return `${minutes}分${seconds}秒`;
    }
  };

  // 计算整体状态
  const getOverallStatus = () => {
    if (!updateStatus) return '未知';
    if (isRunning) return '正在运行';
    
    // 如果更新持续进行并完成了关键步骤（数据导入），即使有失败的步骤，也视为成功
    if (updateStatus.steps && 
        updateStatus.steps['数据导入'] && 
        updateStatus.steps['数据导入'].status === '完成') {
      return '成功完成';
    }
    
    return formatStatus(updateStatus);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Head>
        <title>数据库更新管理</title>
        <meta name="description" content="数据库更新管理页面" />
      </Head>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">数据库更新管理</h1>
        
        {/* 状态卡片 */}
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">更新状态</h2>
          
          {isLoading && <p className="text-gray-500">加载中...</p>}
          
          {!isLoading && updateStatus && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-gray-600 mb-1">当前状态:</p>
                  <p className={`font-semibold ${isRunning ? 'text-blue-600' : updateStatus.status === 'success' ? 'text-green-600' : updateStatus.status === 'failed' ? 'text-red-600' : 'text-gray-800'}`}>
                    {isRunning ? '正在运行' : getOverallStatus()}
                  </p>
                </div>
                
                {updateStatus.start_time && (
                  <div>
                    <p className="text-gray-600 mb-1">开始时间:</p>
                    <p className="font-semibold">{new Date(updateStatus.start_time).toLocaleString()}</p>
                  </div>
                )}
                
                {updateStatus.end_time && (
                  <div>
                    <p className="text-gray-600 mb-1">结束时间:</p>
                    <p className="font-semibold">{new Date(updateStatus.end_time).toLocaleString()}</p>
                  </div>
                )}
                
                {updateStatus.message && (
                  <div>
                    <p className="text-gray-600 mb-1">消息:</p>
                    <p className="font-semibold">{updateStatus.message}</p>
                  </div>
                )}
              </div>
              
              {/* 步骤详情 */}
              {updateStatus.steps && (
                <div className="mt-6">
                  <h2 className="text-xl font-bold mb-4">更新步骤</h2>
                  <div className="space-y-4">
                    {Object.entries(updateStatus.steps).map(([stepName, stepInfo]) => (
                      <div key={stepName} className="border p-4 rounded">
                        <div className="flex justify-between items-center">
                          <h3 className="font-semibold">{stepName}</h3>
                          {formatStepStatus(stepInfo.status)}
                        </div>
                        {stepInfo.startTime && (
                          <p className="text-sm text-gray-600 mt-1">
                            开始时间: {new Date(stepInfo.startTime).toLocaleString()}
                          </p>
                        )}
                        {stepInfo.endTime && (
                          <p className="text-sm text-gray-600">
                            结束时间: {new Date(stepInfo.endTime).toLocaleString()}
                          </p>
                        )}
                        {stepInfo.warning && (
                          <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                            <p className="font-semibold text-yellow-800">警告:</p>
                            <p className="text-yellow-700">{stepInfo.warning}</p>
                          </div>
                        )}
                        {stepInfo.error && (
                          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm">
                            <p className="font-semibold text-red-800">错误:</p>
                            <p className="text-red-700">{stepInfo.error}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {!isLoading && !updateStatus && (
            <p className="text-gray-500">无状态信息可用</p>
          )}
          
          <div className="mt-4 flex justify-end space-x-4">
            <button
              onClick={fetchStatus}
              disabled={isLoading}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded disabled:bg-blue-300"
            >
              {isLoading ? '刷新中...' : '刷新状态'}
            </button>
            
            {isRunning && (
              <button
                onClick={stopUpdate}
                disabled={isLoading}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded disabled:bg-red-300"
              >
                {isLoading ? '停止中...' : '停止更新'}
              </button>
            )}
          </div>
        </div>
        
        {/* 手动触发更新 */}
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">手动触发更新</h2>
          
          {errorMessage && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
              <p>{errorMessage}</p>
            </div>
          )}
          
          {successMessage && (
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4">
              <p>{successMessage}</p>
            </div>
          )}
          
          <form onSubmit={triggerUpdate}>
            <div className="mb-4">
              <label htmlFor="adminKey" className="block text-gray-700 mb-2">管理员密钥</label>
              <input
                type="password"
                id="adminKey"
                value={adminKey}
                onChange={(e) => setAdminKey(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="输入管理员密钥"
                required
              />
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isLoading || isRunning}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded disabled:bg-green-300"
              >
                {isLoading ? '处理中...' : isRunning ? '更新正在进行' : '触发数据库更新'}
              </button>
            </div>
          </form>
        </div>
        
        {/* 最新日志 */}
        {logs && (
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">最新日志</h2>
            
            {logs.error ? (
              <p className="text-red-500">{logs.error}</p>
            ) : logs.message ? (
              <p className="text-gray-500">{logs.message}</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">文件: {logs.file}</p>
                <p className="text-gray-600 mb-2">时间: {new Date(logs.timestamp).toLocaleString()}</p>
                <div className="bg-gray-800 text-gray-200 p-4 rounded overflow-x-auto">
                  <pre className="whitespace-pre-wrap">{logs.content}</pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 