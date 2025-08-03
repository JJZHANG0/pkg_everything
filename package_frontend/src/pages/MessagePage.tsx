// src/pages/MessagePage.tsx
import React, {useEffect, useState} from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/MessagePage.css';
import { API_BASE } from '../config';


interface Message {
    id: number;
    name: string;
    email: string;
    message: string;
    created_at: string;
}

const MessagePage: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);

    useEffect(() => {
        fetchMessages();
    }, []);

    const fetchMessages = async () => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_BASE}/api/messages/`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            const data = await res.json();
            setMessages(data);
        } catch (err) {
            console.error('❌ 获取留言失败:', err);
        }
    };

    const handleDelete = async (id: number) => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_BASE}/api/messages/${id}/`, {
                method: 'DELETE',
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (res.ok) {
                setMessages((prev) => prev.filter((m) => m.id !== id));
                alert('✅ 留言已删除');
            } else {
                alert('❌ 删除失败');
            }
        } catch (err) {
            console.error('❌ 删除异常:', err);
        }
    };

    return (
        <div className="message-wrapper">
            <Navbar/>
            <div className="message-container">
                <h1>📨 User Messages</h1>
                <p>Here are the latest user-submitted messages from the Contact page.</p>

                {messages.length === 0 ? (
                    <p className="no-messages">📭 No messages yet.</p>
                ) : (
                    <div className="message-list">
                        {messages.map((msg) => (
                            <div className="message-card" key={msg.id}>
                                <h3>✉️ {msg.name} ({msg.email})</h3>
                                <p className="content">📝 {msg.message}</p>
                                <p className="timestamp">🕒 {new Date(msg.created_at).toLocaleString()}</p>
                                <button className="btn-delete" onClick={() => handleDelete(msg.id)}>
                                    🗑 Delete
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            <Footer/>
        </div>
    );
};

export default MessagePage;
