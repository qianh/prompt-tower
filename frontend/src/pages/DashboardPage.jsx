import React, { useState, useEffect, useCallback } from 'react';
import { Card, Col, Row, Statistic, message, Spin } from 'antd';
import { Link } from 'react-router-dom';
import { promptAPI, tagAPI } from '../services/api'; // Added tagAPI

const DashboardPage = () => {
  const [totalPrompts, setTotalPrompts] = useState(0);
  const [totalTags, setTotalTags] = useState(0);
  const [totalUsage, setTotalUsage] = useState(0);
  const [currentlyEnabled, setCurrentlyEnabled] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch prompts and global tags in parallel
      const [promptsResponse, globalTagsResponse] = await Promise.all([
        promptAPI.list(),
        tagAPI.list() // Fetches the list of global tag objects e.g. [{name: "tag1"}]
      ]);

      // Total Prompts
      setTotalPrompts(promptsResponse.length);

      // Total Tags (from global tag list)
      setTotalTags(globalTagsResponse.length);

      // Total Usage (assuming usage_count field exists on each prompt object)
      const usageSum = promptsResponse.reduce((acc, prompt) => {
        return acc + (prompt.usage_count || 0); // Default to 0 if usage_count is not present or falsy
      }, 0);
      setTotalUsage(usageSum);

      // Currently Enabled
      const enabledCount = promptsResponse.filter(p => p.status === 'enabled').length;
      setCurrentlyEnabled(enabledCount);

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      message.error('Failed to load dashboard data. Please try again.');
      setTotalPrompts(0);
      setTotalTags(0);
      setTotalUsage(0);
      setCurrentlyEnabled(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div style={{ padding: '20px' }}>
      <Spin spinning={loading} tip="Loading dashboard data...">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Link to="/prompts">
              <Card hoverable>
                <Statistic title="Total Prompts" value={totalPrompts} loading={loading} />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Link to="/tags">
              <Card hoverable>
                <Statistic title="Total Tags" value={totalTags} loading={loading} />
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title="Total Usage" value={totalUsage} loading={loading} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title="Currently Enabled" value={currentlyEnabled} loading={loading} />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default DashboardPage;
