// src/pages/MyOrdersPage.tsx
import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/MyOrdersPage.css";
import { API_BASE } from '../config';


interface Order {
  id: number;
  created_at: string;
  package_type: string;
  weight: string;
  fragile: string;
  description: string;
  pickup_building: string;
  pickup_instructions: string;
  delivery_building: string;
  delivery_speed: string;
  scheduled_date: string | null;
  scheduled_time: string | null;
  status: string;
}

const MyOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    const fetchOrders = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      const response = await fetch(`${API_BASE}/api/orders/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      } else {
        console.error("❌ 获取订单失败");
      }
    };

    fetchOrders();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="orders-wrapper">
      <Navbar />

      <div className="orders-content">
        <h1>My Orders</h1>
        <p>View and track all your deliveries</p>

        {/* 表头 */}
        <div className="orders-table-header">
          <div>ORDER #</div>
          <div>DATE</div>
          <div>STATUS</div>
          <div>FROM</div>
          <div>TO</div>
          <div></div>
        </div>

        {/* 数据列表 */}
        {orders.map((order) => (
          <div key={order.id} className="orders-table-row">
            <div>CO-{String(order.id).padStart(6, "0")}</div>
            <div>{formatDate(order.created_at)}</div>
            <div>
              <span className={`status-pill ${order.status}`}>
                {order.status}
              </span>
            </div>
            <div>{order.pickup_building}</div>
            <div>{order.delivery_building}</div>
            <div>
              <button>View</button>
            </div>
          </div>
        ))}
      </div>

      <Footer />
    </div>
  );
};

export default MyOrdersPage;
