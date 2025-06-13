import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
// import { authAPI } from '../services/api'; // Replaced by useAuth
import { useAuth } from '../context/AuthContext';

const SignupForm = ({ onSignupSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const { signup: contextSignup } = useAuth(); // Get signup function from context

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const data = await contextSignup(values.username, values.password);
      if (onSignupSuccess) {
        onSignupSuccess(data);
      }
      message.success('Signup successful! Please log in.');
      form.resetFields();
    } catch (error) {
      console.error('Signup failed in SignupForm:', error);
      // AuthContext signup re-throws error
      const errorMessage = error.response?.data?.detail || 'Signup failed. Please try again.';
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      name="signup_form"
      onFinish={onFinish}
      style={{ maxWidth: 300, margin: 'auto' }}
    >
      <Form.Item
        name="username"
        rules={[
          { required: true, message: 'Please input your Username!' },
          { min: 3, message: 'Username must be at least 3 characters.'}
        ]}
      >
        <Input prefix={<UserOutlined />} placeholder="Username" />
      </Form.Item>
      {/* <Form.Item
        name="email"
        rules={[
          { required: true, message: 'Please input your Email!' },
          { type: 'email', message: 'The input is not valid E-mail!'}
        ]}
      >
        <Input prefix={<MailOutlined />} placeholder="Email (optional)" />
      </Form.Item> */}
      <Form.Item
        name="password"
        rules={[
          { required: true, message: 'Please input your Password!' },
          { min: 6, message: 'Password must be at least 6 characters.'}
        ]}
        hasFeedback
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Password" />
      </Form.Item>
      <Form.Item
        name="confirm"
        dependencies={['password']}
        hasFeedback
        rules={[
          { required: true, message: 'Please confirm your password!' },
          ({
            getFieldValue
          }) => ({
            validator(_, value) {
              if (!value || getFieldValue('password') === value) {
                return Promise.resolve();
              }
              return Promise.reject(new Error('The two passwords that you entered do not match!'));
            },
          }),
        ]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Confirm Password" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
          Sign up
        </Button>
      </Form.Item>
    </Form>
  );
};

export default SignupForm;
