import React, { useState, useEffect } from 'react';
import './UserManagementPage.css';
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
    <div className="user-management-page">
      <Title level={2} style={{ marginBottom: '24px' }} id="user-management-main-title">
        <UserOutlined style={{ marginRight: '8px' }} />
        用户管理
      </Title>
      
      <Spin spinning={loading} tip="加载用户信息...">
        <Row gutter={[16, 16]}>
          {users.map((user) => (
            <Col xs={24} sm={12} md={8} lg={6} key={user.id || user.username}>
              <Card hoverable className="user-card">
                <div className="user-card-header">
                  <Avatar size={64} icon={<UserOutlined />} />
                  <Title level={4} className="card-username">
                    {user.username}
                  </Title>
                </div>
                
                <div className="user-detail-section">
                  <Statistic
                    title="提交的提示词"
                    value={user.prompt_count || 0}
                    prefix={<FileTextOutlined />}
                                      />
                </div>
                
              </Card>
            </Col>
          ))}
        </Row>
        
        {!loading && users.length === 0 && (
          <div className="empty-users-placeholder">
            <UserOutlined />
            <Title level={4} className="empty-users-title">
              暂无用户数据
            </Title>
          </div>
        )}
      </Spin>
    </div>
  );
};

export default UserManagementPage;
