import React from 'react';
import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import SharedHeader from './SharedHeader'; // Assuming SharedHeader is in the same directory

const { Content } = Layout;

const AuthenticatedLayout = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <SharedHeader />
      <Content style={{ padding: '0', marginTop: '0' }}> {/* Adjusted padding and margin */}
        <Outlet />
      </Content>
    </Layout>
  );
};

export default AuthenticatedLayout;
