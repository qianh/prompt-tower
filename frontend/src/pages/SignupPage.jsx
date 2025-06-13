import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Typography, Row, Col, message } from 'antd';
import SignupForm from '../components/SignupForm';
// import { useAuth } from '../context/AuthContext'; // Not strictly needed if SignupForm handles API call

const { Title, Paragraph } = Typography;

const SignupPage = () => {
  const navigate = useNavigate();
  // const { signup } = useAuth(); // If signup logic were centralized in AuthContext

  const handleSignupSuccess = (data) => {
    // The SignupForm already shows a success message.
    // data might contain the new user info (excluding sensitive details)
    // console.log('Signup successful on page:', data);
    // Redirect to login page after successful signup
    message.info('Please log in with your new account.'); // Reinforce or rely on form message
    navigate('/login');
  };

  return (
    <Row justify="center" align="middle" style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Col xs={22} sm={16} md={12} lg={8} xl={6}>
        <Card>
          <Title level={2} style={{ textAlign: 'center' }}>Sign Up</Title>
          {/* SignupForm itself calls authAPI.signup and displays messages */}
          <SignupForm onSignupSuccess={handleSignupSuccess} />
          <Paragraph style={{ textAlign: 'center', marginTop: '16px' }}>
            Already have an account? <Link to="/login">Log in</Link>
          </Paragraph>
        </Card>
      </Col>
    </Row>
  );
};

export default SignupPage;
