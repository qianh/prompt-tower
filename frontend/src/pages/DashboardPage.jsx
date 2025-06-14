import React, { useState, useEffect, useCallback } from 'react';
import { Card, Col, Row, Statistic, message, Spin, Typography } from 'antd';
import { FileTextOutlined, TagsOutlined, RiseOutlined, CheckCircleOutlined, UserOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { promptAPI, tagAPI, userAPI } from '../services/api'; 

const DashboardPage = () => {
  const [totalPrompts, setTotalPrompts] = useState(0);
  const [totalTags, setTotalTags] = useState(0);
  const [totalUsage, setTotalUsage] = useState(0);
  const [currentlyEnabled, setCurrentlyEnabled] = useState(0);
  const [enabledPercentage, setEnabledPercentage] = useState(0);
  const [totalUsers, setTotalUsers] = useState(0); 
  const [loading, setLoading] = useState(true);

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
    <div style={{ padding: '20px' }}>
      <Typography.Title level={2} style={{ marginBottom: '24px' }}>Dashboard Overview</Typography.Title>
      <Spin spinning={loading} tip="Loading dashboard data...">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Link to="/prompts">
              <Card hoverable>
                <Statistic title="Total Prompts" value={totalPrompts} loading={loading} prefix={<FileTextOutlined />} />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Link to="/tags">
              <Card hoverable>
                <Statistic title="Total Tags" value={totalTags} loading={loading} prefix={<TagsOutlined />} />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Link to="/users">
              <Card hoverable>
                <Statistic title="Total Users" value={totalUsers} loading={loading} prefix={<UserOutlined />} />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title="Total Usage" value={totalUsage} loading={loading} prefix={<RiseOutlined />} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title={`Currently Enabled (${enabledPercentage}%)`} value={currentlyEnabled} loading={loading} prefix={<CheckCircleOutlined />} />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default DashboardPage;
