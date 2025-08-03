import React from "react";

interface Props {
  formData: any;
  setFormData: React.Dispatch<React.SetStateAction<any>>;
  next: () => void;
  back: () => void;
}

const LocationStep: React.FC<Props> = ({ formData, setFormData, next, back }) => {
  const handleNext = () => {
    if (!formData.pickup.building || !formData.delivery.building) {
      alert("Please select both pickup and delivery buildings.");
      return;
    }
    next();
  };

  return (
    <div className="step-container">
      <h2>Pickup & Delivery</h2>
      <p>Where should we pick up and deliver your package?</p>

      <h3>Pickup Location</h3>
      <label>Pickup Building<span style={{ color: "red" }}>*</span></label>
      <select
        value={formData.pickup.building}
        onChange={(e) =>
          setFormData({
            ...formData,
            pickup: { ...formData.pickup, building: e.target.value },
          })
        }
      >
        <option value="">Select building</option>
        <option value="ORIGIN">ORIGIN</option>
      </select>

      <label>Pickup Instructions (Optional)<span style={{ color: "#9ca3af", fontSize: "0.9rem" }}>(Optional)</span></label>
      <textarea
        value={formData.pickup.instructions}
        onChange={(e) =>
          setFormData({
            ...formData,
            pickup: { ...formData.pickup, instructions: e.target.value },
          })
        }
        placeholder="e.g., meet at front gate"
      />

      <h3>Delivery Location</h3>
      <label>Delivery Building</label>
      <select
        value={formData.delivery.building}
        onChange={(e) =>
          setFormData({
            ...formData,
            delivery: { ...formData.delivery, building: e.target.value },
          })
        }
      >
        <option value="">Select building</option>
        <option value="Lauridsen Barrack">Lauridsen Barrack</option>
      </select>

      <div className="step-buttons">
        <button className="btn-outline" onClick={back}>← Back</button>
        <button className="btn-solid" onClick={handleNext}>Continue →</button>
      </div>
    </div>
  );
};

export default LocationStep;
