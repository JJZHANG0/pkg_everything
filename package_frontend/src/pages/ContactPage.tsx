import React, {useState} from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/ContactPage.css';
import { API_BASE } from '../config';


const ContactPage: React.FC = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: '',
    });

    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSuccess('');
        setError('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/messages/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData),
            });

            if (res.ok) {
                setSuccess('✅ Your message has been sent!');
                setFormData({name: '', email: '', message: ''});
            } else {
                const errData = await res.json();
                setError('❌ Failed to send message. ' + (errData?.detail || ''));
            }
        } catch (err) {
            setError('❌ Failed to send message.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="contact-wrapper">
            <Navbar/>
            <div className="contact-container fade-in">
                <h1>📬 Contact Us</h1>
                <p>Have a question or feedback? We'd love to hear from you!</p>

                <div className="contact-content">
                    {/* 📩 Left: Form */}
                    <form className="contact-form" onSubmit={handleSubmit}>
                        <label>Your Name *</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />

                        <label>Your Email *</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />

                        <label>Message *</label>
                        <textarea
                            name="message"
                            value={formData.message}
                            onChange={handleChange}
                            required
                        />

                        <button type="submit" className="btn-solid" disabled={loading}>
                            {loading ? 'Sending...' : 'Send Message'}
                        </button>

                        {success && <p className="success">{success}</p>}
                        {error && <p className="error">{error}</p>}
                    </form>

                    {/* 📍 Right: Info */}
                    <div className="contact-info">
                        <h3>📌 Office Location</h3>
                        <p>Campus Center, Room 205</p>

                        <h3>📞 Phone</h3>
                        <p>+86 123-456-7890</p>

                        <h3>📧 Email</h3>
                        <p>support@CulverBot-campus.com</p>

                        <h3>⏰ Business Hours</h3>
                        <p>Mon - Fri: 9:00 AM - 6:00 PM</p>
                    </div>
                </div>
            </div>
            <Footer/>
        </div>
    );
};

export default ContactPage;
