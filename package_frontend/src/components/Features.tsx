import React from 'react';
import '../styles/Features.css';

const Features: React.FC = () => {
  return (
    <section className="features">
      <h2>Why Choose CulverBot?</h2>
      <p className="features-subtitle">
        Our campus courier service is designed with students and faculty in mind.
      </p>
      <div className="feature-cards">
        <div className="feature-card">
          <div className="feature-icon">⏱️</div>
          <h3>Fast Delivery</h3>
          <p>Get your packages delivered within hours, not days.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">📍</div>
          <h3>Campus Coverage</h3>
          <p>We deliver to every building and dorm on campus.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🛡️</div>
          <h3>Secure Handling</h3>
          <p>Your packages are handled with care and security.</p>
        </div>
      </div>
    </section>
  );
};

export default Features;
