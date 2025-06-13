import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
// import { authAPI } from '../services/api'; // Replaced by useAuth
import { useAuth } from '../context/AuthContext';

const LoginForm = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState(false);
  const { login: contextLogin } = useAuth(); // Get login function from context

  const onFinish = async (values) => {
    setLoading(true);
    try {
      // Call the login function from AuthContext
      const data = await contextLogin(values.username, values.password);
      if (onLoginSuccess) {
        onLoginSuccess(data); // Pass data which includes token etc.
      }
      message.success('Login successful!');
    } catch (error) {
      console.error('Login failed in LoginForm:', error);
      // AuthContext login re-throws error, so error.response should be available
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      name="login_form"
      initialValues={{ remember: true }}
      onFinish={onFinish}
      style={{ maxWidth: 300, margin: 'auto' }}
    >
      <Form.Item
        name="username"
        rules={[{ required: true, message: 'Please input your Username!' }]}
      >
        <Input prefix={<UserOutlined />} placeholder="Username" />
      </Form.Item>
      <Form.Item
        name="password"
        rules={[{ required: true, message: 'Please input your Password!' }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Password" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
          Log in
        </Button>
      </Form.Item>
    </Form>
  );
};

export default LoginForm;
