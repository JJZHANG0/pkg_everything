import React, {useEffect, useState} from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import CommandResultModal from '../components/CommandResultModal';
import '../styles/DispatcherPage.css';
import { API_BASE } from '../config';

interface Order {
    id: number;
    pickup_building: string;
    delivery_building: string;
    status: string;
    created_at: string;
    student: {
        username: string;
        is_student: boolean;
        is_teacher: boolean;
    };
}

interface RobotStatus {
    id: number;
    name: string;
    status: string;
    current_location: string;
    battery_level: number;
    door_status: string;
    current_orders: Order[];
    last_update: string;
}

const DispatcherPage: React.FC = () => {
    const [authorized, setAuthorized] = useState(false);
    const [loading, setLoading] = useState(true);
    const [orders, setOrders] = useState<Order[]>([]);
    const [robotStatus, setRobotStatus] = useState<RobotStatus | null>(null);
    const [logs, setLogs] = useState<string[]>([]);
    
    // 弹窗状态
    const [modalOpen, setModalOpen] = useState(false);
    const [modalData, setModalData] = useState({
        command: '',
        result: 'success' as 'success' | 'error' | 'timeout',
        message: '',
        timestamp: ''
    });

    useEffect(() => {
        // 请求通知权限
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        
        const fetchUserAndOrders = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                setAuthorized(false);
                setLoading(false);
                return;
            }

            try {
                const res = await fetch(`${API_BASE}/api/users/me/`, {
                    headers: {Authorization: `Bearer ${token}`},
                });

                if (!res.ok) return setAuthorized(false);

                const user = await res.json();
                if (user.is_dispatcher) {
                    setAuthorized(true);
                    fetchOrders(token);
                    fetchRobotStatus(token);
                    // 启动定时器，每5秒获取机器人状态
                    const interval = setInterval(() => {
                        fetchRobotStatus(token);
                    }, 5000);
                    
                    // 启动紧急按钮监控
                    startEmergencyButtonMonitoring(token);
                    startCommandMonitoring(token); // 启动命令监控
                    
                    return () => {
                        clearInterval(interval);
                        stopEmergencyButtonMonitoring();
                    };
                } else {
                    setAuthorized(false);
                }
            } catch (err) {
                console.error('用户验证失败:', err);
                setAuthorized(false);
            } finally {
                setLoading(false);
            }
        };

        const fetchOrders = async (token: string) => {
            try {
                const res = await fetch(`${API_BASE}/api/dispatch/orders/`, {
                    headers: {Authorization: `Bearer ${token}`},
                });
                const data = await res.json();
                setOrders(data);
            } catch (err) {
                console.error('订单获取失败:', err);
            }
        };

        const fetchRobotStatus = async (token: string) => {
            try {
                const res = await fetch(`${API_BASE}/api/robots/1/status/`, {
                    headers: {Authorization: `Bearer ${token}`},
                });
                if (res.ok) {
                    const data = await res.json();
                    setRobotStatus(data);
                }
            } catch (err) {
                console.error('机器人状态获取失败:', err);
            }
        };

        // 紧急按钮监控
        let emergencyMonitoringInterval: NodeJS.Timeout | null = null;
        let commandMonitoringInterval: NodeJS.Timeout | null = null;
        
        const startEmergencyButtonMonitoring = (token: string) => {
            // 每1秒检查一次紧急按钮事件
            emergencyMonitoringInterval = setInterval(async () => {
                try {
                    // 使用专用的紧急按钮事件API
                    const eventsRes = await fetch(`${API_BASE}/api/robots/1/emergency_events/`, {
                        headers: {Authorization: `Bearer ${token}`},
                    });
                    
                    if (eventsRes.ok) {
                        const eventsData = await eventsRes.json();
                        
                        if (eventsData.event_count > 0) {
                            const latestEvent = eventsData.emergency_events[0];
                            addLog(`🚨 检测到机器人紧急按钮事件！时间: ${new Date(latestEvent.timestamp).toLocaleString('zh-CN')}`);
                            
                            // 显示紧急通知弹窗
                            setModalData({
                                command: 'emergency_open_door',
                                result: 'success',
                                message: '🚨 机器人紧急按钮已被按下！门已立即开启',
                                timestamp: new Date().toLocaleString('zh-CN')
                            });
                            setModalOpen(true);
                            
                            // 播放提示音（如果浏览器支持）
                            if ('Notification' in window && Notification.permission === 'granted') {
                                new Notification('紧急按钮触发', {
                                    body: '机器人的紧急按钮已被按下！',
                                    icon: '/favicon.ico',
                                    requireInteraction: true
                                });
                            }
                            
                            // 立即刷新机器人状态
                            setTimeout(() => {
                                fetchRobotStatus(token);
                            }, 1000);
                        }
                    }
                } catch (err) {
                    console.error('紧急按钮监控失败:', err);
                }
            }, 1000); // 改为1秒检查一次，提高响应速度
        };
        
        const startCommandMonitoring = (token: string) => {
            // 每2秒检查一次所有命令事件
            commandMonitoringInterval = setInterval(async () => {
                try {
                    // 使用通用的命令事件API
                    const eventsRes = await fetch(`${API_BASE}/api/robots/1/command_events/`, {
                        headers: {Authorization: `Bearer ${token}`},
                    });
                    
                    if (eventsRes.ok) {
                        const eventsData = await eventsRes.json();
                        
                        if (eventsData.event_count > 0) {
                            const latestEvent = eventsData.command_events[0];
                            
                            // 检查是否是新的命令事件（不是紧急按钮）
                            if (!latestEvent.message.includes('紧急按钮')) {
                                addLog(`📡 检测到机器人命令事件: ${latestEvent.message}`);
                                
                                // 根据命令类型显示不同的通知
                                let notificationMessage = '机器人收到新命令';
                                let notificationTitle = '命令事件';
                                
                                if (latestEvent.message.includes('开门')) {
                                    notificationMessage = '机器人正在执行开门命令';
                                    notificationTitle = '开门命令';
                                } else if (latestEvent.message.includes('关门')) {
                                    notificationMessage = '机器人正在执行关门命令';
                                    notificationTitle = '关门命令';
                                } else if (latestEvent.message.includes('开始配送')) {
                                    notificationMessage = '机器人开始配送任务';
                                    notificationTitle = '配送命令';
                                } else if (latestEvent.message.includes('停止')) {
                                    notificationMessage = '机器人停止运行';
                                    notificationTitle = '停止命令';
                                }
                                
                                // 显示命令通知弹窗
                                setModalData({
                                    command: 'command_event',
                                    result: 'success',
                                    message: notificationMessage,
                                    timestamp: new Date().toLocaleString('zh-CN')
                                });
                                setModalOpen(true);
                                
                                // 播放提示音（如果浏览器支持）
                                if ('Notification' in window && Notification.permission === 'granted') {
                                    new Notification(notificationTitle, {
                                        body: notificationMessage,
                                        icon: '/favicon.ico',
                                        requireInteraction: false
                                    });
                                }
                                
                                // 立即刷新机器人状态
                                setTimeout(() => {
                                    fetchRobotStatus(token);
                                }, 1000);
                            }
                        }
                    }
                } catch (err) {
                    console.error('命令监控失败:', err);
                }
            }, 2000); // 每2秒检查一次命令事件
        };
        
        const stopEmergencyButtonMonitoring = () => {
            if (emergencyMonitoringInterval) {
                clearInterval(emergencyMonitoringInterval);
                emergencyMonitoringInterval = null;
            }
            if (commandMonitoringInterval) {
                clearInterval(commandMonitoringInterval);
                commandMonitoringInterval = null;
            }
        };

        fetchUserAndOrders();
    }, []);

    const updateStatus = async (orderId: number, newStatus: string) => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_BASE}/api/dispatch/orders/${orderId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({status: newStatus}),
            });

            if (res.ok) {
                const responseData = await res.json();
                const updatedOrder = responseData.order_data || responseData;
                
                setOrders((prev) => prev.map((o) => (o.id === orderId ? updatedOrder : o)));
                addLog(`✅ 订单 #${orderId} 状态更新为: ${newStatus}`);
                console.log('✅ 状态更新成功:', responseData);
            } else {
                const errorData = await res.json();
                addLog(`❌ 订单 #${orderId} 状态更新失败: ${errorData.detail || 'Unknown error'}`);
                alert(`❌ FAILED TO UPDATE: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (err) {
            console.error('状态更新异常:', err);
            addLog(`❌ 订单 #${orderId} 状态更新异常: ${err}`);
        }
    };

    // 机器人控制函数
    const controlRobot = async (action: string) => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch(`${API_BASE}/api/robots/1/control/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({action: action}),
            });

            if (res.ok) {
                const data = await res.json();
                addLog(`🚀 指令已发送: ${action} - 指令ID: ${data.command_id}`);
                console.log('机器人控制成功:', data);
                
                // 开始轮询检查指令执行状态
                if (token) {
                    pollCommandStatus(data.command_id, action, token);
                }
            } else {
                const errorData = await res.json();
                addLog(`❌ 机器人控制失败: ${action} - ${errorData.detail || 'Unknown error'}`);
                alert(`❌ 机器人控制失败: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (err) {
            console.error('机器人控制异常:', err);
            addLog(`❌ 机器人控制异常: ${action} - ${err}`);
        }
    };
    
    // 紧急按钮函数
    const emergencyButton = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('请先登录');
            return;
        }

        // 确认紧急按钮操作
        const confirmed = window.confirm('🚨 确认触发紧急按钮？\n\n这将立即开启机器人的门！');
        if (!confirmed) {
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/robots/1/emergency_button/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            });

            if (res.ok) {
                const data = await res.json();
                addLog(`🚨 紧急按钮已触发！门已立即开启 - 指令ID: ${data.command_id}`);
                console.log('紧急按钮触发成功:', data);
                
                // 显示紧急成功弹窗
                setModalData({
                    command: 'emergency_open_door',
                    result: 'success',
                    message: '🚨 紧急按钮已触发！机器人的门已立即开启',
                    timestamp: new Date().toLocaleString('zh-CN')
                });
                setModalOpen(true);
                
                // 立即刷新机器人状态
                setTimeout(() => {
                    const fetchRobotStatus = async (token: string) => {
                        try {
                            const res = await fetch(`${API_BASE}/api/robots/1/status/`, {
                                headers: {Authorization: `Bearer ${token}`},
                            });
                            if (res.ok) {
                                const data = await res.json();
                                setRobotStatus(data);
                            }
                        } catch (err) {
                            console.error('机器人状态获取失败:', err);
                        }
                    };
                    fetchRobotStatus(token);
                }, 1000);
            } else {
                const errorData = await res.json();
                addLog(`❌ 紧急按钮触发失败: ${errorData.detail || 'Unknown error'}`);
                alert(`❌ 紧急按钮触发失败: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (err) {
            console.error('紧急按钮触发失败:', err);
            addLog(`❌ 紧急按钮触发失败: ${err}`);
            alert(`❌ 紧急按钮触发失败: ${err}`);
        }
    };
    
    // 轮询检查指令执行状态
    const pollCommandStatus = async (commandId: number, action: string, token: string) => {
        let attempts = 0;
        const maxAttempts = 30; // 最多轮询30次（30秒）
        
        const checkStatus = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/robots/1/status/`, {
                    headers: {Authorization: `Bearer ${token}`},
                });
                
                if (res.ok) {
                    const data = await res.json();
                    
                    // 检查门状态变化（对于开门/关门指令）
                    if (action === 'open_door' && data.door_status === 'OPEN') {
                        addLog(`✅ 开门指令执行成功！门状态: ${data.door_status}`);
                        // 显示成功弹窗
                        setModalData({
                            command: action,
                            result: 'success',
                            message: `门已成功打开，当前门状态: ${data.door_status}`,
                            timestamp: new Date().toLocaleString('zh-CN')
                        });
                        setModalOpen(true);
                        return;
                    } else if (action === 'close_door' && data.door_status === 'CLOSED') {
                        addLog(`✅ 关门指令执行成功！门状态: ${data.door_status}`);
                        // 显示成功弹窗
                        setModalData({
                            command: action,
                            result: 'success',
                            message: `门已成功关闭，当前门状态: ${data.door_status}`,
                            timestamp: new Date().toLocaleString('zh-CN')
                        });
                        setModalOpen(true);
                        return;
                    } else if (action === 'start_delivery' && data.status === 'DELIVERING') {
                        addLog(`✅ 开始配送指令执行成功！机器人状态: ${data.status}`);
                        // 显示成功弹窗
                        setModalData({
                            command: action,
                            result: 'success',
                            message: `机器人已开始配送，当前状态: ${data.status}`,
                            timestamp: new Date().toLocaleString('zh-CN')
                        });
                        setModalOpen(true);
                        return;
                    } else if (action === 'stop_robot' && data.status === 'IDLE') {
                        addLog(`✅ 停止机器人指令执行成功！机器人状态: ${data.status}`);
                        // 显示成功弹窗
                        setModalData({
                            command: action,
                            result: 'success',
                            message: `机器人已停止，当前状态: ${data.status}`,
                            timestamp: new Date().toLocaleString('zh-CN')
                        });
                        setModalOpen(true);
                        return;
                    }
                }
                
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(checkStatus, 1000); // 1秒后再次检查
                } else {
                    addLog(`⏰ 指令执行超时: ${action} - 请检查机器人状态`);
                    // 显示超时弹窗
                    setModalData({
                        command: action,
                        result: 'timeout',
                        message: `指令执行超时，请检查机器人状态和连接`,
                        timestamp: new Date().toLocaleString('zh-CN')
                    });
                    setModalOpen(true);
                }
                
            } catch (err) {
                console.error('检查指令状态失败:', err);
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(checkStatus, 1000);
                } else {
                    // 显示错误弹窗
                    setModalData({
                        command: action,
                        result: 'error',
                        message: `检查指令状态失败: ${err}`,
                        timestamp: new Date().toLocaleString('zh-CN')
                    });
                    setModalOpen(true);
                }
            }
        };
        
        // 开始检查
        setTimeout(checkStatus, 1000);
    };

    const addLog = (message: string) => {
        const timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [`[${timestamp}] ${message}`, ...prev.slice(0, 49)]); // 保留最近50条日志
    };

    const formatRole = (order: Order) => {
        if (order.student?.is_teacher) return 'Teacher';
        if (order.student?.is_student) return 'Student';
        return 'User';
    };

    const formatTime = (iso: string) => {
        const date = new Date(iso);
        return date.toLocaleString();
    };

    if (loading) return <div className="loading">⏳ LOADING...</div>;
    if (!authorized) return <div className="forbidden">⛔ NOT AUTHORIZED</div>;

    return (
        <div className="dispatcher-wrapper">
            <Navbar/>
            <div className="dispatcher-container">
                <div className="dispatcher-header">
                    <h1>🚚 Dispatcher Control Panel</h1>
                    <p>You can monitor and manage the delivery status of all active orders and control the robot.</p>
                </div>

                {/* 机器人控制面板 */}
                <div className="robot-control-panel">
                    <h2>🤖 Robot Control</h2>
                    <div className="robot-status">
                        <div className="status-item">
                            <span className="label">Status:</span>
                            <span className={`value status-${robotStatus?.status?.toLowerCase()}`}>
                                {robotStatus?.status || 'Unknown'}
                            </span>
                        </div>
                        <div className="status-item">
                            <span className="label">Location:</span>
                            <span className="value">{robotStatus?.current_location || 'Unknown'}</span>
                        </div>
                        <div className="status-item">
                            <span className="label">Battery:</span>
                            <span className="value">{robotStatus?.battery_level || 0}%</span>
                        </div>
                        <div className="status-item">
                            <span className="label">Door:</span>
                            <span className={`value door-${robotStatus?.door_status?.toLowerCase()}`}>
                                {robotStatus?.door_status || 'Unknown'}
                            </span>
                        </div>
                    </div>
                    
                    <div className="control-buttons">
                        <button 
                            className="control-btn open-door"
                            onClick={() => controlRobot('open_door')}
                            disabled={robotStatus?.door_status === 'OPEN'}
                        >
                            🚪 Open Door
                        </button>
                        <button 
                            className="control-btn close-door"
                            onClick={() => controlRobot('close_door')}
                            disabled={robotStatus?.door_status === 'CLOSED'}
                        >
                            🚪 Close Door
                        </button>
                        <button 
                            className="control-btn start-delivery"
                            onClick={() => controlRobot('start_delivery')}
                            disabled={robotStatus?.status === 'DELIVERING'}
                        >
                            🚀 Start Delivery
                        </button>
                        <button 
                            className="control-btn stop-robot"
                            onClick={() => controlRobot('stop_robot')}
                            disabled={robotStatus?.status === 'IDLE'}
                        >
                            ⏹️ Stop Robot
                        </button>
                        
                        {/* 紧急按钮 */}
                        <button 
                            className="control-btn emergency-btn"
                            onClick={() => emergencyButton()}
                            title="紧急按钮 - 立即开门"
                        >
                            🚨 Emergency
                        </button>
                        
                        {/* 测试通知按钮 */}
                        <button 
                            className="control-btn test-notification"
                            onClick={() => {
                                // 测试浏览器通知
                                if ('Notification' in window && Notification.permission === 'granted') {
                                    new Notification('测试通知', {
                                        body: '这是一个测试通知，用于验证紧急按钮通知功能',
                                        icon: '/favicon.ico',
                                        requireInteraction: true
                                    });
                                }
                                
                                // 测试弹窗
                                setModalData({
                                    command: 'test_notification',
                                    result: 'success',
                                    message: '🚨 测试：机器人紧急按钮已被按下！门已立即开启',
                                    timestamp: new Date().toLocaleString('zh-CN')
                                });
                                setModalOpen(true);
                                
                                addLog('🧪 测试通知功能');
                            }}
                            title="测试通知功能"
                        >
                            🧪 Test Notification
                        </button>
                    </div>
                </div>

                {/* 订单管理表格 */}
                <div className="order-table-wrapper">
                    <h2>📦 Order Management</h2>
                    <table className="order-table">
                        <thead>
                        <tr>
                            <th>ID</th>
                            <th>Pickup</th>
                            <th>Delivery</th>
                            <th>Status</th>
                            <th>Change</th>
                            <th>Ordered By</th>
                            <th>Role</th>
                            <th>Order Time</th>
                        </tr>
                        </thead>
                        <tbody>
                        {orders.map((order) => (
                            <tr key={order.id}>
                                <td>#{String(order.id).padStart(5, '0')}</td>
                                <td>{order.pickup_building}</td>
                                <td>{order.delivery_building}</td>
                                <td>
                    <span className={`status-pill ${order.status.toLowerCase()}`}>
                      {order.status}
                    </span>
                                </td>
                                <td>
                                    <select
                                        value={order.status}
                                        onChange={(e) => updateStatus(order.id, e.target.value)}
                                    >
                                        <option value="PENDING">Unselected</option>
                                        <option value="ASSIGNED">Assigned</option>
                                        <option value="DELIVERING">Delivering</option>
                                        <option value="DELIVERED">Delivered</option>
                                        <option value="PICKED_UP">Picked Up</option>
                                    </select>
                                </td>
                                <td>{order.student?.username || '—'}</td>
                                <td>{formatRole(order)}</td>
                                <td>{formatTime(order.created_at)}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>

                {/* 系统日志 */}
                <div className="system-logs">
                    <h2>📋 System Logs</h2>
                    <div className="logs-container">
                        {logs.map((log, index) => (
                            <div key={index} className="log-entry">
                                {log}
                            </div>
                        ))}
                        {logs.length === 0 && (
                            <div className="no-logs">No logs available</div>
                        )}
                    </div>
                </div>
            </div>
            
            {/* 指令执行结果弹窗 */}
            <CommandResultModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                command={modalData.command}
                result={modalData.result}
                message={modalData.message}
                timestamp={modalData.timestamp}
            />
            
            <Footer/>
        </div>
    );
};

export default DispatcherPage;
