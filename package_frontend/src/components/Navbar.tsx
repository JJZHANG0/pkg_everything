import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/Navbar.css';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState<string | null>(null);
  const [isDispatcher, setIsDispatcher] = useState<boolean>(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('username');
    const dispatcherFlag = localStorage.getItem('is_dispatcher');

    if (token && storedUser) {
      setUsername(storedUser);
      setIsDispatcher(dispatcherFlag === 'true');
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('is_dispatcher');
    setUsername(null);
    setIsDispatcher(false);
    navigate('/');
  };

  const handleDispatcherClick = () => {
    const token = localStorage.getItem('access_token');
    const flag = localStorage.getItem('is_dispatcher');
    if (!token) {
      alert('请先登录后再访问 Dispatcher 页面');
      navigate('/');
    } else if (flag !== 'true') {
      alert('您不是配送人员，无法访问该页面');
      navigate('/');
    } else {
      navigate('/dispatcher');
    }
  };

  return (
    <nav className="navbar">
      <div className="nav-left">📦 CulverBot</div>

      <ul className="nav-center">
        <li className={location.pathname === '/home' ? 'active' : ''} onClick={() => navigate('/home')}>Home</li>
        <li className={location.pathname === '/about' ? 'active' : ''} onClick={() => navigate('/about')}>About</li>
        <li className={location.pathname === '/order' ? 'active' : ''} onClick={() => navigate('/order')}>Order</li>
        <li className={location.pathname === '/contact' ? 'active' : ''} onClick={() => navigate('/contact')}>Contact</li>
        <li className={location.pathname === '/dispatcher' ? 'active' : ''} onClick={() => navigate('/dispatcher')}>Dispatcher</li>
      </ul>

      <div className="nav-right">
        {username ? (
          <div className="user-info">
            <span className="user-welcome">
              Welcome,&nbsp;
              <strong
                onClick={() => navigate('/dashboard')}
                style={{ cursor: 'pointer', textDecoration: 'underline' }}
              >
                {username}
              </strong>
            </span>
            <button className="btn-outline" onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <>
            <button className="btn-outline" onClick={() => navigate('/')}>Log in</button>
            <button className="btn-solid" onClick={() => navigate('/register')}>Register</button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
