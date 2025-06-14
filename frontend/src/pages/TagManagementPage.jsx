import React, { useState } from 'react';
import { Input, Button, Form, message, Typography, List } from 'antd';
// import { tagAPI } from '../services/api'; // Assuming a tagAPI service

const { Title } = Typography;

const TagManagementPage = () => {
  const [form] = Form.useForm();
  const [tags, setTags] = useState([]); // To store and display existing tags
  const [loading, setLoading] = useState(false);

  // Placeholder for fetching existing tags - this would normally come from an API
  // For now, we'll use a static list for display, or leave it empty
  // useEffect(() => {
  //   const fetchTags = async () => {
  //     try {
  //       // const existingTags = await tagAPI.getAll();
  //       // setTags(existingTags);
  //       setTags([{ id: 1, name: 'General' }, { id: 2, name: 'Productivity' }]); // Example
  //     } catch (error) {
  //       message.error('Failed to load tags');
  //     }
  //   };
  //   fetchTags();
  // }, []);

  const handleAddTag = async (values) => {
    const { tagName } = values;
    if (!tagName || tagName.trim() === '') {
      message.error('Tag name cannot be empty');
      return;
    }
    setLoading(true);
    try {
      // Placeholder for API call
      // const newTag = await tagAPI.create({ name: tagName.trim() });
      // For now, simulate API call and add to local state
      console.log('Simulating add tag:', tagName.trim());
      message.success(`Tag "${tagName.trim()}" added successfully (simulated).`);
      // setTags(prevTags => [...prevTags, { id: Date.now(), name: newTag.name }]); // If API returns the new tag
      setTags(prevTags => [...prevTags, { id: Date.now(), name: tagName.trim() }]);
      form.resetFields();
    } catch (error) {
      console.error('Failed to add tag:', error);
      message.error('Failed to add tag. Please try again.');
    } finally {
      setLoading(false);
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
          <Input placeholder="Enter new tag name" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Add Tag
          </Button>
        </Form.Item>
      </Form>

      <Title level={4} style={{ marginTop: '30px' }}>Existing Tags</Title>
      <List
        bordered
        dataSource={tags}
        renderItem={item => (
          <List.Item>
            {item.name}
            {/* As per requirements, no edit/delete actions */}
          </List.Item>
        )}
        locale={{ emptyText: 'No tags added yet.' }}
      />
    </div>
  );
};

export default TagManagementPage;
