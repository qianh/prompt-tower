import React from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Card, Typography, Row, Col } from 'antd';
import LoginForm from '../components/LoginForm';

const { Title, Paragraph } = Typography;

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || "/";

  const handleLoginSuccess = async (credentials) => {
    // The login logic (calling API, setting token) is handled by AuthContext's login function
    // AuthContext's login function already calls authAPI.login
    // and then fetchCurrentUser upon success.
    // The AuthProvider will update isAuthenticated, and ProtectedRoute will handle redirection.
    // However, we can still navigate explicitly here if desired, especially for the 'from' location.
    try {
        // await login(credentials.username, credentials.password); // This is handled by LoginForm calling authAPI
        // The onLoginSuccess in LoginForm is what calls this function if provided.
        // The actual login call to the context is made from within the LoginForm itself, or we can make it here.
        // For clarity, let LoginForm call the API, and this page manages redirection based on AuthContext state or explicit navigation.
        // Let's adjust LoginForm to call context's login and pass the result (or let AuthContext handle navigation)

        // Revised: LoginForm's onLoginSuccess will be called by LoginForm after it calls authAPI.login.
        // The AuthContext's login function is now the primary method.
        // So, LoginForm should call useAuth().login.
        // The `onLoginSuccess` prop on LoginForm is to signal the page that login process (via context) completed.
        // The AuthContext state will change, and ProtectedRoute should handle redirecting to `from`.
        // Or we can navigate here.
        navigate(from, { replace: true });
    } catch (error) {
        // Error is already handled and messaged by LoginForm if it calls authAPI.login
        // If login is called from here via useAuth().login, then error handling would be here.
        // Let's ensure LoginForm uses the context's login method for centralized logic.
        console.error("Login unsuccesful from LoginPage", error) 
        // No need to show another message if LoginForm already did
    }
  };

  return (
    <Row justify="center" align="middle" style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Col xs={22} sm={16} md={12} lg={8} xl={6}>
        <Card>
          <Title level={2} style={{ textAlign: 'center' }}>Login</Title>
          <LoginForm onLoginSuccess={handleLoginSuccess} /> 
          <Paragraph style={{ textAlign: 'center', marginTop: '16px' }}>
            Don't have an account? <Link to="/signup">Sign up</Link>
          </Paragraph>
        </Card>
      </Col>
    </Row>
  );
};

export default LoginPage;
