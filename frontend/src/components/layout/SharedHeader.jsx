import React from 'react';
import { Layout, Button, Space } from 'antd';
import { LogoutOutlined, AppstoreOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const { Header } = Layout;

const SharedHeader = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Link to="/dashboard">
          <h1 style={{ color: 'white', margin: 0, marginRight: '20px' }}>Prompt管理系统</h1>
        </Link>
        <Link to="/dashboard">
          <Button type="link" icon={<AppstoreOutlined />} style={{ color: 'white' }}>
            Dashboard
          </Button>
        </Link>
      </div>
      <Space>
        {user && <span style={{ color: 'white' }}>Welcome, {user.username}!</span>}
        <Button
          danger
          icon={<LogoutOutlined />}
          onClick={handleLogout}
        >
          Logout
        </Button>
      </Space>
    </Header>
  );
};

export default SharedHeader;
