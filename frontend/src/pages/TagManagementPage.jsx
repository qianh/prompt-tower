import React, { useState, useEffect, useCallback } from 'react';
import { Input, Button, Form, message, Typography, List, Spin } from 'antd';
import { tagAPI } from '../services/api'; // Changed from promptAPI

const { Title, Paragraph } = Typography;

const TagManagementPage = () => {
  const [form] = Form.useForm();
  const [tags, setTags] = useState([]); // Stores unique tag names as strings
  const [loading, setLoading] = useState(true);
  const [addLoading, setAddLoading] = useState(false);

  const fetchGlobalTags = useCallback(async () => {
    setLoading(true);
    try {
      const globalTagsModels = await tagAPI.list(); // Returns List[models.Tag] e.g. [{name: "tag1"}]
      const tagNames = globalTagsModels.map(tagModel => tagModel.name).sort();
      setTags(tagNames);
    } catch (error) {
      console.error('Failed to load global tags:', error);
      message.error('Failed to load global tags. Please try again.');
      setTags([]);
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
    if (tags.some(tag => tag.toLowerCase() === trimmedTagName.toLowerCase())) {
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
      const errorDetail = error.response?.data?.detail || 'Failed to add tag. Please try again.';
      message.error(errorDetail);
    } finally {
      setAddLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: 'auto', padding: '20px' }}>
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
        <List
          bordered
          dataSource={tags}
          renderItem={tag => (
            <List.Item>
              {tag}
            </List.Item>
          )}
          locale={{ emptyText: loading ? ' ' : 'No global tags defined yet.' }}
        />
      </Spin>
      <Paragraph type="secondary" style={{ marginTop: '10px' }}>
        This page displays all globally defined tags. Adding a tag here makes it available system-wide.
      </Paragraph>
    </div>
  );
};

export default TagManagementPage;
