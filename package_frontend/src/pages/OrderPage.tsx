import React, { useState } from "react";
import PackageStep from "../components/order/PackageStep";
import LocationStep from "../components/order/LocationStep";
import ScheduleStep from "../components/order/ScheduleStep";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/OrderPage.css";
import { API_BASE } from '../config';


const OrderPage: React.FC = () => {
  const [step, setStep] = useState(1);

  const [formData, setFormData] = useState({
    packageType: "",
    weight: "",
    fragile: "", // "yes" / "no"
    description: "",
    pickup: {
      building: "",
      instructions: "",
    },
    delivery: {
      building: "",
    },
    speed: "",
    scheduleDate: "",
    scheduleTime: "",
  });

  const [orderCode, setOrderCode] = useState<string | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);

  const next = () => setStep((prev) => prev + 1);
  const back = () => setStep((prev) => prev - 1);

  const submitOrder = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("⚠️ 未登录，无法提交订单！");
      return;
    }

    const payload = {
      package_type: formData.packageType,
      weight: formData.weight,
      fragile: formData.fragile === "yes",
      description: formData.description,
      pickup_building: formData.pickup.building,
      pickup_instructions: formData.pickup.instructions,
      delivery_building: formData.delivery.building,
      delivery_speed: formData.speed,
      scheduled_date: formData.scheduleDate || null,
      scheduled_time: formData.scheduleTime || null,
    };

    try {
      const res = await fetch(`${API_BASE}/api/orders/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (res.status === 201) {
        const data = await res.json();
        console.log("✅ Created Order:", data);
        setOrderCode(`CO-${String(data.id).padStart(6, "0")}`);
        setQrCodeUrl(data.qr_code_url);
        setStep(4); // ✅ 显示成功页面
      } else {
        const error = await res.json();
        console.error("❌ 提交失败", error);
        alert(`❌ 提交失败：${JSON.stringify(error)}`);
      }
    } catch (err) {
      console.error("请求错误", err);
      alert("网络错误，请稍后再试");
    }
  };

  return (
    <div className="order-wrapper">
      <Navbar />
      <StepIndicator step={step} />

      {step === 1 && (
        <PackageStep formData={formData} setFormData={setFormData} next={next} />
      )}

      {step === 2 && (
        <LocationStep
          formData={formData}
          setFormData={setFormData}
          next={next}
          back={back}
        />
      )}

      {step === 3 && (
        <ScheduleStep
          formData={formData}
          setFormData={setFormData}
          back={back}
          submit={submitOrder}
        />
      )}

      {step === 4 && (
        <div className="step-container" style={{ textAlign: "center" }}>
          <h2>🎉 订单提交成功！</h2>
          <p>订单编号：<strong>{orderCode}</strong></p>
          {qrCodeUrl && (
            <div style={{ margin: "2rem 0" }}>
              <img
                src={qrCodeUrl}
                alt="二维码"
                style={{ width: "200px", height: "200px" }}
              />
              <p style={{ color: "#6b7280", fontSize: "0.9rem" }}>请截图或保存二维码用于查验</p>
            </div>
          )}
          <button className="btn-outline" onClick={() => window.location.href = "/dashboard"}>
            返回首页
          </button>
        </div>
      )}

      <Footer />
    </div>
  );
};

const StepIndicator: React.FC<{ step: number }> = ({ step }) => {
  const steps = ["📦 Package", "📍 Locations", "⏱️ Schedule"];
  return (
    <div className="step-indicator">
      {steps.map((label, index) => (
        <span
          key={index}
          className={step === index + 1 ? "active" : ""}
        >
          {label}
        </span>
      ))}
    </div>
  );
};

export default OrderPage;
