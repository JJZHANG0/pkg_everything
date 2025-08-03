// src/pages/DashboardPage.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/DashboardPage.css';
import { API_BASE } from '../config';


const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [updatedName, setUpdatedName] = useState('');
  const [updatedEmail, setUpdatedEmail] = useState('');
  const [orders, setOrders] = useState<any[]>([]);

  // 🆕 密码相关字段
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    const storedUser = localStorage.getItem('username');
    const storedEmail = localStorage.getItem('email');
    if (storedUser) setUsername(storedUser);
    if (storedEmail) setEmail(storedEmail);

    const fetchOrders = async () => {
      const token = localStorage.getItem('access_token');

      try {
        const res = await fetch(`${API_BASE}/api/orders/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await res.json();
        if (Array.isArray(data)) {
          setOrders([...data].reverse());
        } else {
          console.error('❌ 响应不是数组:', data);
        }
      } catch (err) {
        console.error('❌ 请求失败', err);
      }
    };

    fetchOrders();
  }, []);

  const handleSave = async () => {
    if (newPassword && newPassword !== confirmPassword) {
      alert('❌ 两次输入的密码不一致');
      return;
    }

    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id');
    const body: any = {
      first_name: updatedName,
      email: updatedEmail,
    };

    if (newPassword) {
      body.password = newPassword;
    }

    const res = await fetch(`${API_BASE}/api/users/${userId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json();
      alert('✅ 用户信息更新成功');
      setUsername(data.username);
      setEmail(data.email);
      setEditMode(false);
      setNewPassword('');
      setConfirmPassword('');
    } else {
      alert('❌ 更新失败');
    }
  };

  const recent = orders[0];

  return (
    <div className="dashboard-wrapper">
      <Navbar />
      <div className="dashboard-content">
        <h1>Welcome, {username}!</h1>
        <p>Manage your deliveries and track your packages.</p>

        <div className="dashboard-edit-wrapper">
          <div className={`dashboard-left ${editMode ? 'slide-left' : ''}`}>
            {/* 🕒 Recent Orders */}
            <div className="dashboard-card">
              <h2>🕒 Recent Orders</h2>
              {recent ? (
                <>
                  <p><strong>Order #</strong> CO-{String(recent.id).padStart(6, '0')}</p>
                  <p><strong>Date</strong> {new Date(recent.created_at).toLocaleDateString()}</p>
                  <p><strong>Status</strong> <span className={`status-pill ${recent.status}`}>{recent.status}</span></p>
                  <p><strong>From</strong> {recent.pickup_building}</p>
                  <p><strong>To</strong> {recent.delivery_building}</p>
                </>
              ) : (
                <p>You have no recent orders.</p>
              )}
              <div className="card-buttons">
                <button className="btn-solid" onClick={() => navigate('/order')}>+ Place New Order</button>
                <button className="btn-outline" onClick={() => navigate('/orders')}>📋 View All Orders</button>
              </div>
            </div>

            {/* 👤 Account Info */}
            <div className="dashboard-card">
              <h2>👤 Account Information</h2>
              <p><strong>Name</strong> {username}</p>
              <p><strong>Email</strong> {email}</p>
              <p><strong>Role</strong> Student</p>
              <p><strong>Phone</strong> 123-456-7890</p>
              <p><strong>Total Orders</strong> {orders.length}</p>
              <p><strong>Joined</strong> Apr 19, 2025</p>
              <button className="btn-outline" onClick={() => setEditMode(true)}>⚙️ Edit Profile</button>
            </div>
          </div>

          {/* ✏️ 编辑弹窗 */}
          {editMode && (
            <div className="profile-edit-panel">
              <h3>✏️ Edit Your Info</h3>

              <label>Name</label>
              <input value={updatedName} onChange={(e) => setUpdatedName(e.target.value)} placeholder="Enter new name" />

              <label>Email</label>
              <input value={updatedEmail} onChange={(e) => setUpdatedEmail(e.target.value)} placeholder="Enter new email" />

              <label>New Password</label>
              <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Enter new password" />

              <label>Confirm Password</label>
              <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm password" />

              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <button className="btn-cancel" onClick={() => setEditMode(false)}>Cancel</button>
                <button className="btn-save" onClick={handleSave}>Save</button>
              </div>
            </div>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default DashboardPage;
