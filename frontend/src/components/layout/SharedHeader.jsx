import React from 'react';
import { Layout, Button, Space, Avatar, Dropdown } from 'antd';
import { LogoutOutlined, AppstoreOutlined, UserOutlined, DownOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const { Header } = Layout;

const SharedHeader = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  // 用户下拉菜单项
  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout,
      style: {
        color: '#ef4444',
        fontWeight: '500'
      }
    }
  ];

  const headerStyle = {
    background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 30%, #cbd5e1 70%, #94a3b8 100%)',
    borderBottom: '1px solid rgba(148, 163, 184, 0.4)',
    padding: '0 24px',
    height: '64px',
    lineHeight: '64px',
    boxShadow: '0 4px 20px rgba(71, 85, 105, 0.12), 0 1px 3px rgba(0, 0, 0, 0.08)',
    position: 'relative',
    zIndex: 1,
    backdropFilter: 'blur(8px)'
  };

  return (
    <Header style={headerStyle}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
        <Link to="/dashboard">
          <h1 style={{ 
            margin: 0, 
            fontSize: '24px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 30%, #06b6d4 70%, #0891b2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            letterSpacing: '-0.5px',
            filter: 'drop-shadow(0 1px 2px rgba(30, 64, 175, 0.2))'
          }}>
            提示词管理系统
          </h1>
        </Link>
        
        <Dropdown
          menu={{ items: userMenuItems }}
          trigger={['hover']}
          placement="bottomRight"
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(147, 197, 253, 0.2) 100%)',
            padding: '6px 12px',
            borderRadius: '20px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            boxShadow: '0 2px 8px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.3)',
            height: '32px',
            backdropFilter: 'blur(10px)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-1px)';
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(59, 130, 246, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.4)';
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(147, 197, 253, 0.25) 100%)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.3)';
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(147, 197, 253, 0.2) 100%)';
          }}
          >
            <Avatar 
              size={22}
              style={{ 
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 50%, #1e40af 100%)',
                marginRight: '8px',
                fontSize: '11px',
                color: 'white',
                fontWeight: '600',
                boxShadow: '0 2px 6px rgba(59, 130, 246, 0.3)'
              }}
            >
              {user.username.charAt(0).toUpperCase()}
            </Avatar>
            <span style={{ 
              marginRight: '6px', 
              fontSize: '14px',
              color: '#06b6d4',
              fontWeight: '700',
              letterSpacing: '0.25px'
            }}>
              {user.username}
            </span>
            <DownOutlined style={{ 
              fontSize: '10px', 
              color: '#4b5563'
            }} />
          </div>
        </Dropdown>
      </div>
    </Header>
  );
};

export default SharedHeader;
