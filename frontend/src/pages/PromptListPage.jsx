import React, { useState } from 'react';
import './PromptListPage.css';
import { Layout, Button, Modal, Typography, Row, Col } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import PromptList from '../components/PromptList';
import PromptEditor from '../components/PromptEditor';
import { promptAPI } from '../services/api';

const { Content } = Layout;

const PromptListPage = () => {
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState(null);
  const [refreshList, setRefreshList] = useState(0);

  const handleEdit = (prompt = null) => {
    setCurrentPrompt(prompt);
    setEditModalVisible(true);
  };

  const handleSave = async (values) => {
    try {
      if (currentPrompt) {
        await promptAPI.update(currentPrompt.title, values);
      } else {
        await promptAPI.create(values);
      }
      setEditModalVisible(false);
      setRefreshList((prev) => prev + 1);
    } catch (error) {
      console.error('Save prompt failed:', error);
      // Consider showing a message to the user
    }
  };

  return (
    <Layout className="prompt-list-page">
      <Row
        justify="space-between"
        align="middle"
        className="prompt-list-header"
      >
        <Col>
          <Typography.Title level={4} style={{ margin: 0 }}>
            Prompt List
          </Typography.Title>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleEdit()}
          >
            New Prompt
          </Button>
        </Col>
      </Row>
      <Content
        style={{
          // Styles are now in PromptListPage.css
          // background: '#fff', // Removed
          // padding: 24, // Handled by .prompt-list-page .ant-layout-content
          // margin: 0, // Handled by .prompt-list-page .ant-layout-content
          minHeight: 280, // Retain minHeight or adjust in CSS if needed
        }}
      >
        <PromptList onEdit={handleEdit} key={refreshList} />
      </Content>

      <Modal
        title={currentPrompt ? 'Edit Prompt' : 'New Prompt'}
        open={editModalVisible}
        footer={null}
        onCancel={() => setEditModalVisible(false)}
        width={800}
      >
        <PromptEditor
          prompt={currentPrompt}
          onSave={handleSave}
          onCancel={() => setEditModalVisible(false)}
        />
      </Modal>
    </Layout>
  );
};

export default PromptListPage;
