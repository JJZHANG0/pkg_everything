import React, { useState } from 'react';
import './LoginPage.css'; // 复用原样式
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../config';



const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirmPassword) {
      setError('两次密码输入不一致');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || '注册失败');
      }

      setSuccess('注册成功，跳转中...');
      setTimeout(() => {
        navigate('/'); // 跳回登录页
      }, 1500);
    } catch (err: any) {
      setError(err.message || '请求失败');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="logo">📦 CulverBot</div>
        <h2>Create your account</h2>
        <p className="subtitle">Sign up to get started</p>

        <form onSubmit={handleRegister}>
          <label>用户名</label>
          <input
            type="text"
            placeholder="yourname"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label>密码</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <label>确认密码</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          {error && <p className="error">{error}</p>}
          {success && <p style={{ color: 'green' }}>{success}</p>}

          <button type="submit">注册</button>
        </form>

        <p className="footer">
          已有账号？<span className="link" onClick={() => navigate('/')}>去登录</span>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
