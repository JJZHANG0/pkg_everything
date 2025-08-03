import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/AboutPage.css';
import { API_BASE } from '../config';
import ceoImage from '../assets/ceo.png';



const AboutPage: React.FC = () => {
  return (
    <div className="about">
      <Navbar />

      {/* Hero */}
      <section className="about-hero">
        <h1>About CulverBot</h1>
        <p>We're on a mission to make campus deliveries fast, reliable, and hassle-free.</p>
      </section>

      {/* Story */}
      <section className="about-story">
        <div className="story-text">
          <h2>Our Story</h2>
          <p>
            CulverBot was founded in 2023 by a group of university students who were frustrated with
            the lack of efficient delivery options on campus. Whether it was textbooks, lab
            materials, or personal items, getting things from one side of campus to another was
            always a challenge.
          </p>
          <p>
            What started as a small operation with just three couriers has grown into a campus-wide
            service with a team of dedicated delivery personnel serving thousands of students and
            faculty members every semester.
          </p>
          <p>
            Our mission is simple: to provide the fastest, most reliable courier service on campus,
            making life easier for everyone in our university community.
          </p>
        </div>
        <div className="story-image">
          <img src={ceoImage} alt="CEO" className="ceo-image" />
        </div>
      </section>

      {/* Values */}
      <section className="about-values">
        <h2>Our Values</h2>
        <p>The principles that guide everything we do at CulverBot.</p>
        <div className="value-cards">
          <div className="value-card">
            <div className="icon">📦</div>
            <h3>Reliability</h3>
            <p>
              We deliver on time, every time. You can count on us to handle your packages with care
              and get them to their destination as promised.
            </p>
          </div>
          <div className="value-card">
            <div className="icon">📞</div>
            <h3>Accessibility</h3>
            <p>
              Our service is designed to be easy to use for everyone on campus. We're just a few
              taps away whenever you need us.
            </p>
          </div>
          <div className="value-card">
            <div className="icon">📍</div>
            <h3>Community</h3>
            <p>
              We're proud to be part of the campus community and committed to making it better
              through our service.
            </p>
          </div>
        </div>
      </section>

      {/* Team */}
      {/*<section className="about-team">*/}
      {/*  <h2>Meet Our Team</h2>*/}
      {/*  <p>The dedicated people behind CulverBot who make it all happen.</p>*/}
      {/*  <div className="team-members">*/}
      {/*    <div className="team-member">*/}
      {/*      <div className="avatar-placeholder" />*/}
      {/*      <h4>Alex Johnson</h4>*/}
      {/*      <p>Founder & CEO</p>*/}
      {/*    </div>*/}
      {/*    <div className="team-member">*/}
      {/*      <div className="avatar-placeholder" />*/}
      {/*      <h4>Jamie Smith</h4>*/}
      {/*      <p>Operations Manager</p>*/}
      {/*    </div>*/}
      {/*    <div className="team-member">*/}
      {/*      <div className="avatar-placeholder" />*/}
      {/*      <h4>Taylor Wilson</h4>*/}
      {/*      <p>Lead Developer</p>*/}
      {/*    </div>*/}
      {/*    <div className="team-member">*/}
      {/*      <div className="avatar-placeholder" />*/}
      {/*      <h4>Morgan Lee</h4>*/}
      {/*      <p>Customer Support</p>*/}
      {/*    </div>*/}
      {/*  </div>*/}
      {/*</section>*/}

      {/*/!* CTA *!/*/}
      {/*<section className="about-cta">*/}
      {/*  <h2>Ready to get started?</h2>*/}
      {/*  <p>Join thousands of students and faculty who trust CulverBot for their campus delivery needs.</p>*/}
      {/*  <div className="cta-buttons">*/}
      {/*    <button className="btn-solid">Sign Up Now →</button>*/}
      {/*    <button className="btn-outline">Contact Us</button>*/}
      {/*  </div>*/}
      {/*</section>*/}

      <Footer />
    </div>
  );
};

export default AboutPage;
