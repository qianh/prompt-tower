import React from 'react';
import { Card, Col, Row, Statistic } from 'antd';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  // Placeholder data - this will need to be fetched from the API
  const totalPrompts = 150;
  const totalTags = 30;
  const totalUsage = 1200;
  const currentlyEnabled = 5;

  return (
    <div style={{ padding: '20px' }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Link to="/prompts">
            <Card hoverable>
              <Statistic title="Total Prompts" value={totalPrompts} />
            </Card>
          </Link>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Link to="/tags">
            <Card hoverable>
              <Statistic title="Total Tags" value={totalTags} />
            </Card>
          </Link>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="Total Usage" value={totalUsage} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="Currently Enabled" value={currentlyEnabled} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
