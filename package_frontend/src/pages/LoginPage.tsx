import React, { useState } from 'react';
import './LoginPage.css';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../config';


const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    console.log('🔐 开始登录...', { username, password });
    console.log('🌐 API地址:', `${API_BASE}/api/token/`);

    try {
      // ✅ 第一步：获取 JWT Token
      console.log('📡 正在获取token...');
      const response = await fetch(`${API_BASE}/api/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      console.log('📡 Token响应状态:', response.status);
      console.log('📡 Token响应头:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Token获取失败:', errorText);
        throw new Error(`用户名或密码错误 (${response.status})`);
      }

      const data = await response.json();
      console.log('✅ Token获取成功:', data);
      
      const accessToken = data.access;
      const refreshToken = data.refresh;

      localStorage.setItem('token', accessToken);
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);

      // ✅ 第二步：调用 /api/users/me/ 获取当前用户信息
      console.log('📡 正在获取用户信息...');
      const meRes = await fetch(`${API_BASE}/api/users/me/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      console.log('📡 用户信息响应状态:', meRes.status);

      if (!meRes.ok) {
        const errorText = await meRes.text();
        console.error('❌ 用户信息获取失败:', errorText);
        throw new Error(`无法获取用户信息 (${meRes.status})`);
      }

      const userInfo = await meRes.json();
      console.log('✅ 用户信息获取成功:', userInfo);

      // ✅ 保存到 localStorage，供后续使用
      localStorage.setItem('user_id', userInfo.id);
      localStorage.setItem('username', userInfo.username);
      localStorage.setItem('email', userInfo.email);

      console.log('✅ 登录成功，准备跳转...');
      
      // ✅ 跳转首页
      navigate('/home');
    } catch (err: any) {
      console.error('❌ 登录错误:', err);
      setError(err.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="logo">📦 CulverBot</div>
        <h2>Welcome back</h2>
        <p className="subtitle">Enter your credentials to access your account</p>

        <form onSubmit={handleLogin}>
          <label>Username</label>
          <input
            type="text"
            placeholder="please enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <div className="password-row">
            <label>Password</label>
            <span className="link">Forgot password?</span>
          </div>
          <input
            type="password"
            placeholder="please enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? '登录中...' : 'Log in'}
          </button>
        </form>

        <p className="footer">
          Don't have an account? <span className="link" onClick={() => navigate("/register")}>Register</span>
        </p>
        
        {/* 调试信息 */}
        <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', fontSize: '12px' }}>
          <p><strong>调试信息:</strong></p>
          <p>API地址: {API_BASE}</p>
          <p>用户名: {username}</p>
          <p>密码长度: {password.length}</p>
          <p>请打开浏览器控制台(F12)查看详细日志</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
