import React, {useState} from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/SuperuserPage.css';
import {useNavigate} from 'react-router-dom';
import { API_BASE } from '../config';


const ADMIN_UNLOCK_CODE = '123123';

const SuperuserPage: React.FC = () => {
    const navigate = useNavigate();
    const [unlocked, setUnlocked] = useState(false);
    const [password, setPassword] = useState('');

    const handleUnlock = (e: React.FormEvent) => {
        e.preventDefault();
        if (password === ADMIN_UNLOCK_CODE) {
            setUnlocked(true);
        } else {
            alert('❌ Incorrect unlock code');
            // setTimeout(() => navigate('/home'), 100);
        }
    };
    console.log('🔒 当前状态：unlocked =', unlocked);

    if (!unlocked) {
        return (
            <div className="superuser-wrapper">
                <Navbar/>
                <div className="unlock-container fade-in">
                    <h2>🔐 Enter Admin Unlock Code</h2>
                    <form onSubmit={handleUnlock}>
                        <input
                            type="password"
                            placeholder="Enter unlock code"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button type="submit" className="btn-solid">Unlock</button>
                    </form>
                </div>
                <Footer/>
            </div>
        );
    }

    return (
        <div className="superuser-wrapper">
            <Navbar/>
            <div className="superuser-content">
                <h1>🌟 Super Admin Dashboard</h1>
                <p>Welcome, administrator. You have access to all system-level controls.</p>

                <div className="superuser-sections">
                    <div className="superuser-card">
                        <h2>📦 All Orders Overview</h2>
                        <p>Monitor and manage all delivery orders, including status changes and reassignment.</p>
                        <button className="btn-outline" onClick={() => navigate('/superuser/orders')}>
                            View Orders
                        </button>
                    </div>

                    <div className="superuser-card">
                        <h2>🚚 Dispatcher Assignment</h2>
                        <p>Assign delivery personnel for each order and manage dispatcher permissions.</p>
                        <button className="btn-outline" onClick={() => navigate('/superuser/dispatch')}>
                            Assign Dispatchers
                        </button>
                    </div>

                    <div className="superuser-card">
                        <h2>👥 User Management</h2>
                        <p>View and manage all users, their roles, and system access privileges.</p>
                        <button className="btn-solid" onClick={() => navigate('/superuser/users')}>
                            Manage Users
                        </button>
                    </div>

                    <div className="superuser-card">
                        <h2>📨 Message Inbox</h2>
                        <p>Review and respond to feedback or inquiries submitted via the Contact Us page.</p>
                        <button className="btn-outline" onClick={() => navigate('/superuser/messages')}>
                            View Messages
                        </button>
                    </div>

                    <div className="superuser-card">
                        <h2>🛠️ System Settings</h2>
                        <p>Configure system-wide options and perform administrative maintenance tasks.</p>
                        <button className="btn-outline" disabled>
                            Coming Soon
                        </button>
                    </div>
                </div>
            </div>
            <Footer/>
        </div>
    );
};

export default SuperuserPage;
