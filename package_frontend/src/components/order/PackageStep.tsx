import React from "react";

interface PackageStepProps {
  formData: any;
  setFormData: (data: any) => void;
  next: () => void;
}

const PackageStep: React.FC<PackageStepProps> = ({ formData, setFormData, next }) => {
  const handleNext = () => {
    const { packageType, weight, fragile } = formData;
    if (!packageType || !weight || !fragile) {
      alert("Please fill in all required fields before continuing.");
      return;
    }
    next();
  };

  return (
    <div className="step-container">
      <h2>Package Details</h2>
      <p>Tell us about what you're sending</p>

      <label>Package Type<span style={{ color: "red" }}>*</span></label>
      <select
        value={formData.packageType}
        onChange={(e) => setFormData({ ...formData, packageType: e.target.value })}
      >
        <option value="">Select package type</option>
        <option value="documents">Documents</option>
        <option value="box">Box</option>
        <option value="bag">Bag</option>
      </select>

      <label>Approximate Weight<span style={{ color: "red" }}>*</span></label>
      <select
        value={formData.weight}
        onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
      >
        <option value="">Select weight</option>
        <option value="light">Light (&lt; 5 lbs)</option>
        <option value="medium">Medium (5-15 lbs)</option>
        <option value="heavy">Heavy (&gt; 15 lbs)</option>
      </select>

      <label>Is this package fragile?<span style={{ color: "red" }}>*</span></label>
      <select
        value={formData.fragile}
        onChange={(e) => setFormData({ ...formData, fragile: e.target.value })}
      >
        <option value="">Select...</option>
        <option value="yes">Yes</option>
        <option value="no">No</option>
      </select>

      <label>Package Description (Optional)</label>
      <textarea
        value={formData.description}
        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        placeholder="Briefly describe your package"
      />

      <div className="step-buttons">
        <div />
        <button className="btn-solid" onClick={handleNext}>
          Continue →
        </button>
      </div>
    </div>
  );
};

export default PackageStep;
