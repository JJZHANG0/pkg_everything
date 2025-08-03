import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/NetworkMonitorPage.css';

interface NetworkLog {
  id: number;
  timestamp: string;
  level: string;
  log_type: string;
  message: string;
  user: {
    id: number;
    username: string;
  } | null;
  data: any;
}

interface NetworkStats {
  total_requests: number;
  total_responses: number;
  total_errors: number;
}

interface ActiveConnection {
  client_ip: string;
  username: string;
  last_activity: string;
}

const NetworkMonitorPage: React.FC = () => {
  const [logs, setLogs] = useState<NetworkLog[]>([]);
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [activeConnections, setActiveConnections] = useState<ActiveConnection[]>([]);
  const [recentUsers, setRecentUsers] = useState<any[]>([]);
  const [recentIPs, setRecentIPs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filterType, setFilterType] = useState<string>('');
  const [filterIP, setFilterIP] = useState<string>('');
  const [filterUser, setFilterUser] = useState<string>('');

  // 获取认证token
  const getAuthToken = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/token/', {
        username: 'root',
        password: 'test123456'
      });
      return response.data.access;
    } catch (error) {
      console.error('认证失败:', error);
      return null;
    }
  };

  // 获取网络监控数据
  const fetchNetworkData = async () => {
    try {
      const token = await getAuthToken();
      if (!token) return;

      const headers = { Authorization: `Bearer ${token}` };
      
      // 构建查询参数
      const params = new URLSearchParams();
      if (filterType) params.append('log_type', filterType);
      if (filterIP) params.append('client_ip', filterIP);
      if (filterUser) params.append('user_id', filterUser);
      params.append('limit', '100');

      const response = await axios.get(`http://localhost:8000/api/network-monitor/?${params}`, { headers });
      
      // 去重处理：按IP、路径、方法组合去重，只保留最新的
      const uniqueLogs = response.data.logs.reduce((acc: NetworkLog[], current: NetworkLog) => {
        const key = `${current.data?.client_ip || 'unknown'}-${current.data?.path || 'unknown'}-${current.data?.method || 'unknown'}`;
        const existingIndex = acc.findIndex(log => {
          const existingKey = `${log.data?.client_ip || 'unknown'}-${log.data?.path || 'unknown'}-${log.data?.method || 'unknown'}`;
          return existingKey === key;
        });
        
        if (existingIndex === -1) {
          // 新的唯一记录
          acc.push(current);
        } else {
          // 更新现有记录（保留最新的）
          const existing = acc[existingIndex];
          if (new Date(current.timestamp) > new Date(existing.timestamp)) {
            acc[existingIndex] = current;
          }
        }
        
        return acc;
      }, []);
      
      setLogs(uniqueLogs);
      setStats(response.data.statistics);
      setRecentUsers(response.data.recent_users);
      setRecentIPs(response.data.recent_ips);
      setLoading(false);
    } catch (error) {
      console.error('获取网络监控数据失败:', error);
      setLoading(false);
    }
  };

  // 获取活跃连接
  const fetchActiveConnections = async () => {
    try {
      const token = await getAuthToken();
      if (!token) return;

      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get('http://localhost:8000/api/network-monitor/connections/', { headers });
      
      // 去重活跃连接：按IP去重
      const uniqueConnections = response.data.active_connections.reduce((acc: ActiveConnection[], current: ActiveConnection) => {
        const existingIndex = acc.findIndex(conn => conn.client_ip === current.client_ip);
        
        if (existingIndex === -1) {
          // 新的唯一连接
          acc.push(current);
        } else {
          // 更新现有连接（保留最新的活动时间）
          const existing = acc[existingIndex];
          if (new Date(current.last_activity) > new Date(existing.last_activity)) {
            acc[existingIndex] = current;
          }
        }
        
        return acc;
      }, []);
      
      setActiveConnections(uniqueConnections);
    } catch (error) {
      console.error('获取活跃连接失败:', error);
    }
  };

  // 实时刷新
  useEffect(() => {
    fetchNetworkData();
    fetchActiveConnections();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchNetworkData();
        fetchActiveConnections();
      }, 3000); // 每3秒刷新一次

      return () => clearInterval(interval);
    }
  }, [autoRefresh, filterType, filterIP, filterUser]);

  // 格式化时间
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };

  // 获取日志类型图标
  const getLogTypeIcon = (logType: string) => {
    switch (logType) {
      case 'NETWORK_REQUEST':
        return '🌐';
      case 'NETWORK_RESPONSE':
        return '📤';
      case 'NETWORK_ERROR':
        return '❌';
      case 'WEBSOCKET_CONNECTION':
        return '🔌';
      default:
        return '📝';
    }
  };

  // 获取日志级别颜色
  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return '#ff4444';
      case 'WARNING':
        return '#ff8800';
      case 'SUCCESS':
        return '#00aa00';
      default:
        return '#0088ff';
    }
  };

  // 清空过滤器
  const clearFilters = () => {
    setFilterType('');
    setFilterIP('');
    setFilterUser('');
  };

  if (loading) {
    return (
      <div className="network-monitor-page">
        <div className="loading">加载中...</div>
      </div>
    );
  }

  return (
    <div className="network-monitor-page">
      <div className="monitor-header">
        <h1>🌐 网络监控中心</h1>
        <div className="controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            自动刷新
          </label>
          <button onClick={fetchNetworkData}>刷新数据</button>
          <button onClick={clearFilters}>清空过滤器</button>
        </div>
      </div>

      {/* 统计信息 */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.total_requests}</div>
            <div className="stat-label">总请求数</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_responses}</div>
            <div className="stat-label">总响应数</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_errors}</div>
            <div className="stat-label">错误数</div>
          </div>

        </div>
      )}

      {/* 活跃连接 */}
      <div className="active-connections">
        <h3>🔌 活跃连接 ({activeConnections.length})</h3>
        <div className="connections-grid">
          {activeConnections.map((conn, index) => (
            <div key={index} className="connection-card">
              <div className="connection-ip">{conn.client_ip}</div>
              <div className="connection-user">{conn.username}</div>
              <div className="connection-time">{formatTime(conn.last_activity)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 过滤器 */}
      <div className="filters">
        <h3>🔍 过滤器</h3>
        <div className="filter-controls">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">所有类型</option>
            <option value="NETWORK_REQUEST">网络请求</option>
            <option value="NETWORK_RESPONSE">网络响应</option>
            <option value="NETWORK_ERROR">网络错误</option>
            <option value="WEBSOCKET_CONNECTION">WebSocket连接</option>
          </select>

          <select
            value={filterIP}
            onChange={(e) => setFilterIP(e.target.value)}
          >
            <option value="">所有IP</option>
            {recentIPs.map((ip, index) => (
              <option key={index} value={ip}>{ip}</option>
            ))}
          </select>

          <select
            value={filterUser}
            onChange={(e) => setFilterUser(e.target.value)}
          >
            <option value="">所有用户</option>
            {recentUsers.map((user, index) => (
              <option key={index} value={user.user__id}>{user.user__username}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 日志列表 */}
      <div className="logs-section">
        <h3>📋 网络活动日志 ({logs.length})</h3>
        <div className="logs-container">
          {logs.map((log) => (
            <div key={log.id} className="log-item">
              <div className="log-header">
                <span className="log-icon">{getLogTypeIcon(log.log_type)}</span>
                <span 
                  className="log-level"
                  style={{ color: getLogLevelColor(log.level) }}
                >
                  {log.level}
                </span>
                <span className="log-type">{log.log_type}</span>
                <span className="log-time">{formatTime(log.timestamp)}</span>
              </div>
              
              <div className="log-message">{log.message}</div>
              
              <div className="log-details">
                <div className="log-user">
                  用户: {log.user ? log.user.username : 'Anonymous'}
                </div>
                <div className="log-ip">
                  IP: {log.data?.client_ip || 'Unknown'}
                </div>
                {log.data?.method && (
                  <div className="log-method">
                    方法: {log.data.method} {log.data.path}
                  </div>
                )}
                {log.data?.processing_time && (
                  <div className="log-time-taken">
                    处理时间: {log.data.processing_time}s
                  </div>
                )}
                {log.data?.status_code && (
                  <div className="log-status">
                    状态码: {log.data.status_code}
                  </div>
                )}
              </div>

              {/* 显示请求/响应数据 */}
              {log.data?.request_body && Object.keys(log.data.request_body).length > 0 && (
                <div className="log-data">
                  <strong>请求数据:</strong>
                  <pre>{JSON.stringify(log.data.request_body, null, 2)}</pre>
                </div>
              )}
              
              {log.data?.response_body && Object.keys(log.data.response_body).length > 0 && (
                <div className="log-data">
                  <strong>响应数据:</strong>
                  <pre>{JSON.stringify(log.data.response_body, null, 2)}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NetworkMonitorPage; 