import React, {useEffect, useState} from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/UserManagementPage.css';
import { API_BASE } from '../config';


interface User {
    id: number;
    username: string;
    email: string;
    is_dispatcher: boolean;
}

const UserManagementPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_BASE}/api/users/`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            const data = await res.json();

            const normalized = data.map((user: any) => ({
                ...user,
                is_dispatcher: Boolean(user.is_dispatcher),
            }));

            setUsers(normalized);
        } catch (err) {
            console.error('❌ 用户获取失败', err);
        }
    };

    const updateDispatcher = async (userId: number, isDispatcher: boolean) => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_BASE}/api/users/${userId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({is_dispatcher: isDispatcher}),
            });

            if (res.ok) {
                const updated = await res.json();
                alert('✅ 权限更新成功');
                fetchUsers();
            } else {
                alert('❌ 更新失败');
            }
        } catch (err) {
            console.error('❌ 权限修改错误', err);
        }
    };

    const filteredUsers = users.filter((user) =>
        user.username.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="superuser-wrapper">
            <Navbar/>
            <div className="superuser-content">
                <div className="user-header-row">
                    <h1>👥 User Management</h1>
                    <input
                        type="text"
                        placeholder="🔍 Search by username..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <table className="user-table">
                    <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Dispatcher</th>
                    </tr>
                    </thead>
                    <tbody>
                    {filteredUsers.map((user) => (
                        <tr key={user.id}>
                            <td>{user.username}</td>
                            <td>{user.email}</td>
                            <td>
                                <select
                                    value={user.is_dispatcher ? 'yes' : 'no'}
                                    onChange={(e) =>
                                        updateDispatcher(user.id, e.target.value === 'yes')
                                    }
                                >
                                    <option value="no"> ❌ </option>
                                    <option value="yes"> ✅ </option>
                                </select>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <Footer/>
        </div>
    );
};

export default UserManagementPage;
