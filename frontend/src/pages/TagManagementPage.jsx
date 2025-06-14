import React, { useState, useEffect, useCallback } from 'react';
import { Input, Button, Form, message, Typography, Spin, Card, Row, Col, Popconfirm } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
// import { FileTextOutlined } from '@ant-design/icons';
import { tagAPI, promptAPI } from '../services/api'; // Added promptAPI

const { Title, Paragraph } = Typography;

const TagManagementPage = () => {
  const [form] = Form.useForm();
  const [tags, setTags] = useState([]); // Stores unique tag names as strings
  const [loading, setLoading] = useState(true);
  const [addLoading, setAddLoading] = useState(false);

  const fetchGlobalTags = useCallback(async () => {
    setLoading(true);
    try {
      const [globalTagsList, allPrompts] = await Promise.all([
        tagAPI.list(), // Returns List[str]
        promptAPI.list() // Assuming this returns List of prompt objects, each having a 'tags' array
      ]);

      const processedTags = (Array.isArray(globalTagsList) ? globalTagsList : []).map(tagName => {
        let count = 0;
        if (Array.isArray(allPrompts)) {
          allPrompts.forEach(prompt => {
            if (Array.isArray(prompt.tags) && prompt.tags.includes(tagName)) {
              count++;
            }
          });
        }
        return { name: tagName, prompt_count: count };
      });

      setTags(processedTags.sort((a, b) => a.name.localeCompare(b.name)));
    } catch (error) {
      console.error('Failed to load global tags or prompts:', error);
      message.error('Failed to load data. Please try again.');
      setTags([]); // Set to empty array on error
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGlobalTags();
  }, [fetchGlobalTags]);

  const handleAddTag = async (values) => {
    const { tagName } = values;
    const trimmedTagName = tagName.trim();

    if (!trimmedTagName) {
      message.error('Tag name cannot be empty');
      return;
    }

    // Check against the current list for immediate feedback, though backend handles uniqueness.
    if (tags.some(tag => tag.name.toLowerCase() === trimmedTagName.toLowerCase())) {
      message.warning(`Tag "${trimmedTagName}" already exists.`);
      return;
    }
    
    setAddLoading(true);
    try {
      await tagAPI.create({ name: trimmedTagName });
      message.success(`Tag "${trimmedTagName}" added successfully to the global list.`);
      form.resetFields();
      await fetchGlobalTags(); // Refresh the list from the backend
    } catch (error) {
      console.error('Failed to add tag:', error);
      // Check if the error response from FastAPI (due to HTTPException) has a detail field
      const errorDetail = (error.response && error.response.data && error.response.data.detail) || 'Failed to add tag. Please try again.';
      message.error(errorDetail);
    } finally {
      setAddLoading(false);
    }
  };

  const handleDeleteTag = async (tagName) => {
    try {
      // Assuming tagAPI.delete expects the tag name string.
      // If it expects an object like { name: tagName }, this needs adjustment.
      await tagAPI.delete(tagName); 
      message.success(`Tag "${tagName}" deleted successfully.`);
      fetchGlobalTags(); // Refresh the list
    } catch (error) {
      console.error('Failed to delete tag:', error);
      const errorDetail = (error.response && error.response.data && error.response.data.detail) || 'Failed to delete tag. Please try again.';
      message.error(errorDetail);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: 'auto', padding: '20px' }}>
      <Title level={2}>Tag Management</Title>
      
      <Form
        form={form}
        layout="inline"
        onFinish={handleAddTag}
        style={{ marginBottom: '20px' }}
      >
        <Form.Item
          name="tagName"
          rules={[{ required: true, message: 'Please input the tag name!' }]}
          style={{ flexGrow: 1 }}
        >
          <Input placeholder="Enter new global tag name" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={addLoading}>
            Add Tag
          </Button>
        </Form.Item>
      </Form>

      <Title level={4} style={{ marginTop: '30px' }}>Global Tags</Title>
      <Spin spinning={loading} tip="Loading tags...">
        {tags.length > 0 ? (
          <Row gutter={[16, 16]}>
            {tags.map(tag => (
              <Col key={tag.name} xs={24} sm={12} md={8} lg={8} xl={8}>
                <Card size="small" style={{ position: 'relative' }}>
                  <div style={{ position: 'absolute', top: '8px', right: '8px', zIndex: 1 }}>
                    <Popconfirm
                      title="Are you sure you want to delete this tag?"
                      onConfirm={() => handleDeleteTag(tag.name)}
                      okText="Yes"
                      cancelText="No"
                    >
                      <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                    </Popconfirm>
                  </div>
                  <Card.Meta title={tag.name} />
                  <Typography.Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
                    关联提示词: {tag.prompt_count}个
                  </Typography.Text>
                </Card>
              </Col>
            ))}
          </Row>
        ) : (
          !loading && <Typography.Text>No global tags defined yet.</Typography.Text>
        )}
      </Spin>
      <Paragraph type="secondary" style={{ marginTop: '10px' }}>
        This page displays all globally defined tags. Adding a tag here makes it available system-wide.
      </Paragraph>
    </div>
  );
};

export default TagManagementPage;
