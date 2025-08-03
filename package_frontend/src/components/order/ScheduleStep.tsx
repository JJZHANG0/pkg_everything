import React from "react";

interface ScheduleStepProps {
  formData: any;
  setFormData: (data: any) => void;
  back: () => void;
  submit: () => void;
}

const ScheduleStep: React.FC<ScheduleStepProps> = ({ formData, setFormData, back, submit }) => {
  const handleSubmit = () => {
    if (!formData.speed) {
      alert("Please select a delivery speed.");
      return;
    }
    submit();
  };

  return (
    <div className="step-container">
      <h2>Delivery Schedule</h2>
      <p>When would you like your package to be delivered?</p>

      <label>Delivery Speed<span style={{ color: "red" }}>*</span></label>
      <select
        value={formData.speed}
        onChange={(e) => setFormData({ ...formData, speed: e.target.value })}
      >
        <option value="">Select speed</option>
        <option value="standard">Standard (2–3 hours)</option>
        <option value="express">Express (1 hour)</option>
        <option value="rush">Rush (30 minutes)</option>
      </select>

      <label>Schedule for Later (Optional)<span style={{ color: "#9ca3af", fontSize: "0.9rem" }}>(Optional)</span><span style={{ color: "red" }}>*</span></label>
      <div style={{ display: "flex", gap: "1rem" }}>
        <input
          type="date"
          value={formData.scheduleDate}
          onChange={(e) => setFormData({ ...formData, scheduleDate: e.target.value })}
        />
        <input
          type="time"
          value={formData.scheduleTime}
          onChange={(e) => setFormData({ ...formData, scheduleTime: e.target.value })}
        />
      </div>

      <div className="step-buttons">
        <button className="btn-outline" onClick={back}>
          ← Back
        </button>
        <button className="btn-solid" onClick={handleSubmit}>
          Submit
        </button>
      </div>
    </div>
  );
};

export default ScheduleStep;
