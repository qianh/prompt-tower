import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Spin, Typography, message } from 'antd';
import { FileTextOutlined, TagsOutlined, RiseOutlined, CheckCircleOutlined, UserOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { promptAPI, tagAPI, userAPI } from '../services/api'; 
import './DashboardPage.css';

const DashboardPage = () => {
  const [totalPrompts, setTotalPrompts] = useState(0);
  const [totalTags, setTotalTags] = useState(0);
  const [totalUsage, setTotalUsage] = useState(0);
  const [currentlyEnabled, setCurrentlyEnabled] = useState(0);
  const [enabledPercentage, setEnabledPercentage] = useState(0);
  const [totalUsers, setTotalUsers] = useState(0); 
  const [loading, setLoading] = useState(true);

  // 科技感图标样式
  const techIconStyle = { 
    color: 'rgba(147, 197, 253, 0.9)', 
    fontSize: '28px',
    filter: 'drop-shadow(0 1px 3px rgba(0, 0, 0, 0.2))'
  };

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch prompts, global tags in parallel
      const [promptsResponse, globalTagsResponse, usersResponse] = await Promise.all([
        promptAPI.list(),
        tagAPI.list(), 
        userAPI.list()
      ]);

      // Total Prompts
      setTotalPrompts(promptsResponse.length);

      // Total Tags (from global tag list)
      setTotalTags(globalTagsResponse.length);

      // Total Users
      setTotalUsers(usersResponse.length);

      // Total Usage (assuming usage_count field exists on each prompt object)
      const usageSum = promptsResponse.reduce((acc, prompt) => {
        return acc + (prompt.usage_count || 0); 
      }, 0);
      setTotalUsage(usageSum);

      // Currently Enabled
      const enabledCount = promptsResponse.filter(p => p.status === 'enabled').length;
      setCurrentlyEnabled(enabledCount);

      // Calculate and set enabled percentage
      if (promptsResponse.length > 0) {
        setEnabledPercentage(Math.round((enabledCount / promptsResponse.length) * 100));
      } else {
        setEnabledPercentage(0);
      }

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      message.error('Failed to load dashboard data. Please try again.');
      setTotalPrompts(0);
      setTotalTags(0);
      setTotalUsage(0);
      setCurrentlyEnabled(0);
      setEnabledPercentage(0);
      setTotalUsers(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div className="dashboard-page" style={{ padding: '20px' }}>
      <div style={{ marginBottom: '32px' }}>
        <Typography.Title 
          level={2}
          style={{ 
            margin: 0, 
            color: '#1f2937',
            fontSize: '28px',
            fontWeight: '700',
            textShadow: '0 1px 3px rgba(255, 255, 255, 0.8)',
            letterSpacing: '-0.5px'
          }}
        >
          数据面板总览
        </Typography.Title>
      </div>
      <Spin spinning={loading} tip="Loading dashboard data...">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Link to="/prompts">
              <Card className="dashboard-card-prompts" hoverable>
                <Statistic 
                  title="提示词总数" 
                  value={totalPrompts} 
                  loading={loading} 
                  prefix={<FileTextOutlined style={techIconStyle} />}
                />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Link to="/tags">
              <Card className="dashboard-card-tags" hoverable>
                <Statistic 
                  title="标签总数" 
                  value={totalTags} 
                  loading={loading} 
                  prefix={<TagsOutlined style={techIconStyle} />}
                />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Link to="/users">
              <Card className="dashboard-card-users" hoverable>
                <Statistic 
                  title="用户总数" 
                  value={totalUsers} 
                  loading={loading} 
                  prefix={<UserOutlined style={techIconStyle} />}
                />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card className="dashboard-card-usage" hoverable>
              <Statistic 
                title="总使用次数" 
                value={totalUsage} 
                loading={loading} 
                prefix={<RiseOutlined style={techIconStyle} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card className="dashboard-card-enabled" hoverable>
              <Statistic 
                title={`当前启用 (${enabledPercentage}%)`} 
                value={currentlyEnabled} 
                loading={loading} 
                prefix={<CheckCircleOutlined style={techIconStyle} />}
              />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default DashboardPage;
