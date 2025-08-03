import React, {useState} from 'react';
import '../styles/Footer.css';

const Footer: React.FC = () => {
    const [showPolicy, setShowPolicy] = useState(false);
    const [showTerms, setShowTerms] = useState(false);

    return (
        <>
            <footer className="footer">
                <div className="footer-container">
                    <div className="footer-left">
                        © 2025 CulverBot. All rights reserved.
                    </div>
                    <div className="footer-links">
                        <button onClick={() => setShowPolicy(true)}>Privacy Policy</button>
                        <button onClick={() => setShowTerms(true)}>Terms of Service</button>
                        <a href="/contact">Contact Us</a>
                    </div>
                </div>
            </footer>

            {/* Privacy Modal */}
            {showPolicy && (
                <div className="modal-overlay" onClick={() => setShowPolicy(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Privacy Policy</h2>
                        <p>Effective Date: May 22, 2025</p>

                        <p>
                            CulverBot ("we", "our", "us") respects your privacy. This Privacy Policy explains how we
                            collect, use, disclose, and safeguard your information when you visit our website or use our
                            services.
                        </p>

                        <h3>1. Information We Collect</h3>
                        <ul>
                            <li><strong>Personal Data:</strong> When you fill out a contact form or register, we may
                                collect your name, email address, username, and phone number.
                            </li>
                            <li><strong>Order Data:</strong> If you place delivery orders, we collect details such as
                                pickup/delivery locations, time, and order content.
                            </li>
                            <li><strong>Technical Data:</strong> We may collect non-identifiable browser/device data for
                                debugging and analytics.
                            </li>
                        </ul>

                        <h3>2. How We Use Your Information</h3>
                        <ul>
                            <li>To process and manage delivery orders</li>
                            <li>To respond to inquiries or feedback from the contact page</li>
                            <li>To provide, maintain, and improve platform functionality</li>
                            <li>To ensure platform security and prevent fraud</li>
                        </ul>

                        <h3>3. Data Sharing and Disclosure</h3>
                        <p>
                            We do <strong>not</strong> sell, rent, or share your personal information with third parties
                            for marketing purposes. Data may only be shared with campus-authorized personnel (e.g.,
                            delivery staff, administrators) to fulfill services you requested.
                        </p>

                        <h3>4. Data Security</h3>
                        <p>
                            All data is securely stored in password-protected databases with restricted access. We
                            implement HTTPS encryption and follow campus IT guidelines.
                        </p>

                        <h3>5. Your Rights</h3>
                        <ul>
                            <li>You can request a copy of your data or ask us to delete it at any time.</li>
                            <li>You can update or correct your information in your account dashboard.</li>
                        </ul>

                        <h3>6. Cookies</h3>
                        <p>
                            We do not use cookies for tracking or advertising. Only functional session cookies may be
                            used for login and security purposes.
                        </p>

                        <h3>7. Contact Us</h3>
                        <p>
                            For any privacy concerns or questions, contact us
                            at <strong>support@CulverBot-campus.com</strong>.
                        </p>

                        <button className="btn-close" onClick={() => setShowPolicy(false)}>Close</button>
                    </div>
                </div>
            )}

            {/* Terms Modal */}
            {showTerms && (
                <div className="modal-overlay" onClick={() => setShowTerms(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Terms of Service</h2>
                        <p>Effective Date: May 22, 2025</p>

                        <p>
                            By accessing or using the CulverBot platform ("Service"), you agree to the following terms and
                            conditions.
                        </p>

                        <h3>1. Eligibility</h3>
                        <p>
                            You must be a registered student, staff, or authorized member of the school community to use
                            our services. Misuse of identity or credentials is strictly prohibited.
                        </p>

                        <h3>2. Account Responsibilities</h3>
                        <ul>
                            <li>You are responsible for maintaining the confidentiality of your account credentials.
                            </li>
                            <li>You agree not to impersonate others or submit false information.</li>
                        </ul>

                        <h3>3. Acceptable Use</h3>
                        <ul>
                            <li>You agree not to use this service for illegal or prohibited purposes.</li>
                            <li>Abuse, spam, harassment, or exploitation of system vulnerabilities is not allowed.</li>
                        </ul>

                        <h3>4. Delivery Terms</h3>
                        <ul>
                            <li>CulverBot provides delivery coordination within the campus. Users are expected to specify
                                accurate pickup and delivery information.
                            </li>
                            <li>The platform is not liable for lost or damaged items unless negligence is proven.</li>
                        </ul>

                        <h3>5. Modifications</h3>
                        <p>
                            We may modify or discontinue services or features at any time. Changes to these terms will
                            be posted and are effective immediately.
                        </p>

                        <h3>6. Termination</h3>
                        <p>
                            We reserve the right to suspend or terminate any user account that violates these terms or
                            disrupts platform operations.
                        </p>

                        <h3>7. Governing Law</h3>
                        <p>
                            These Terms shall be governed by the applicable policies and laws of your educational
                            institution and relevant local regulations.
                        </p>

                        <h3>8. Contact Us</h3>
                        <p>
                            For questions about these Terms, contact us at <strong>support@CulverBot-campus.com</strong>.
                        </p>

                        <button className="btn-close" onClick={() => setShowTerms(false)}>Close</button>
                    </div>
                </div>
            )}
        </>
    );
};

export default Footer;
