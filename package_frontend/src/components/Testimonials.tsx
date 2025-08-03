import React from 'react';
import '../styles/Testimonials.css';
import user1Image from '../assets/user1.png';
import user2Image from '../assets/user2.png';

const Testimonials: React.FC = () => {
  return (
    <section className="testimonials">
      <h2>What Our Users Say</h2>
      <p className="testimonials-subtitle">
        Don't just take our word for it. Here's what students and faculty have to say.
      </p>

      <div className="testimonial-cards">
        <div className="testimonial-card">
          <div className="avatar">
            <img src={user1Image} alt="Sarah J." />
          </div>
          <h4>Sarah J.</h4>
          <p className="role">Junior, Computer Science</p>
          <p className="comment">
            "CulverBot has been a lifesaver during finals week! I could get my study materials delivered without leaving the library."
          </p>
        </div>

        <div className="testimonial-card">
          <div className="avatar">
            <img src={user2Image} alt="Prof. Martinez" />
          </div>
          <h4>Prof. Martinez</h4>
          <p className="role">Faculty, Engineering</p>
          <p className="comment">
            "I use CulverBot to send important documents between departments. It's reliable and much faster than campus mail."
          </p>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
