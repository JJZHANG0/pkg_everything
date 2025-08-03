import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import OrderPage from "./pages/OrderPage";
import DashboardPage from "./pages/DashboardPage";
import MyOrdersPage from './pages/MyOrdersPage';
import ContactPage from './pages/ContactPage';
import SuperuserPage from "./pages/SuperuserPage";
import UserManagementPage from "./pages/UserManagementPage";
import DispatcherPage from "./pages/DisptacherPage";
import MessagePage from "./pages/MessagePage";
import NetworkMonitorPage from "./pages/NetworkMonitorPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/order" element={<OrderPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/orders" element={<MyOrdersPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/superuser" element={<SuperuserPage />} />
        <Route path="/superuser/users" element={<UserManagementPage />} />
        <Route path="/dispatcher" element={<DispatcherPage />} />
        <Route path="/superuser/messages" element={<MessagePage />} />
        <Route path="/superuser/network-monitor" element={<NetworkMonitorPage />} />
      </Routes>
    </Router>
  );
}

export default App;
