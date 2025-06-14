import React from 'react';
import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import SharedHeader from './SharedHeader'; // Assuming SharedHeader is in the same directory

const { Content } = Layout;

const AuthenticatedLayout = () => {
  return (
    <Layout style={{ 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)'
      }}>
      <SharedHeader />
      <Content style={{ 
          padding: '0', 
          marginTop: '0',
          background: 'transparent'
        }}> {/* Adjusted padding and margin */}
        <Outlet />
      </Content>
    </Layout>
  );
};

export default AuthenticatedLayout;
