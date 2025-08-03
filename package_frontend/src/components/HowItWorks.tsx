import React from 'react';
import '../styles/HowItWorks.css';

const HowItWorks: React.FC = () => {
  return (
    <section className="how-it-works">
      <h2>How It Works</h2>
      <p className="how-subtitle">
        Getting your packages delivered is simple and straightforward.
      </p>

      <div className="steps">
        <div className="step">
          <div className="step-circle">1</div>
          <h3>Register</h3>
          <p>Create an account with your campus email.</p>
        </div>
        <div className="step">
          <div className="step-circle">2</div>
          <h3>Place an Order</h3>
          <p>Enter package details and delivery location.</p>
        </div>
        <div className="step">
          <div className="step-circle">3</div>
          <h3>Track & Receive</h3>
          <p>Track your package and receive it at your location.</p>
        </div>
      </div>

      <button className="btn-solid step-button">Place an Order</button>
    </section>
  );
};

export default HowItWorks;
