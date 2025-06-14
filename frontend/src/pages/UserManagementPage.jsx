import React, { useState, useEffect } from 'react';
import { Card, Col, Row, Typography, message, Spin, Avatar, Statistic } from 'antd';
import { UserOutlined, FileTextOutlined, CalendarOutlined } from '@ant-design/icons';
import { userAPI } from '../services/api';

const { Title, Text } = Typography;

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await userAPI.list();
      setUsers(data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      message.error('获取用户信息失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div style={{ padding: '20px' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        <UserOutlined style={{ marginRight: '8px' }} />
        用户管理
      </Title>
      
      <Spin spinning={loading} tip="加载用户信息...">
        <Row gutter={[16, 16]}>
          {users.map((user) => (
            <Col xs={24} sm={12} md={8} lg={6} key={user.id || user.username}>
              <Card
                hoverable
                style={{
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
                bodyStyle={{ padding: '20px' }}
              >
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <Avatar
                    size={64}
                    icon={<UserOutlined />}
                    style={{
                      backgroundColor: '#1890ff',
                      marginBottom: '12px',
                    }}
                  />
                  <Title level={4} style={{ margin: '0 0 4px 0' }}>
                    {user.username}
                  </Title>
                  <Text type="secondary">
                    <UserOutlined style={{ marginRight: '4px' }} />
                    用户ID: {user.id}
                  </Text>
                </div>
                
                <div style={{ marginTop: '16px' }}>
                  <Statistic
                    title="提交的提示词"
                    value={user.prompt_count || 0}
                    prefix={<FileTextOutlined style={{ color: '#52c41a' }} />}
                    valueStyle={{ color: '#52c41a', fontSize: '20px' }}
                  />
                </div>
                
                <div style={{ 
                  marginTop: '16px', 
                  paddingTop: '16px', 
                  borderTop: '1px solid #f0f0f0',
                  textAlign: 'center'
                }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    用户ID: {user.id || 'N/A'}
                  </Text>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
        
        {!loading && users.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <UserOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
            <Title level={4} style={{ color: '#999', marginTop: '16px' }}>
              暂无用户数据
            </Title>
          </div>
        )}
      </Spin>
    </div>
  );
};

export default UserManagementPage;
