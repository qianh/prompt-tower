import React, { useState, useEffect, useCallback } from 'react';
import './TagManagementPage.css';
import { Input, Button, message, Typography, Spin, Card, Row, Col, Popconfirm } from 'antd';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
// import { FileTextOutlined } from '@ant-design/icons';
import { tagAPI, promptAPI } from '../services/api'; // Added promptAPI

const { Title, Paragraph } = Typography;

const TagManagementPage = () => {
  const [tags, setTags] = useState([]); // Stores unique tag names as strings
  const [loading, setLoading] = useState(true);
  const [addLoading, setAddLoading] = useState(false);
  const [isAddingTag, setIsAddingTag] = useState(false);
  const [inlineNewTagName, setInlineNewTagName] = useState('');

  const fetchGlobalTags = useCallback(async () => {
    setLoading(true);
    try {
      const [globalTagsList, allPrompts] = await Promise.all([
        tagAPI.list(), // Returns List[str]
        promptAPI.list() // Assuming this returns List of prompt objects, each having a 'tags' array
      ]);

      console.log('[TagDebug] Raw globalTagsList from API:', globalTagsList);
      console.log('[TagDebug] Is globalTagsList an array?', Array.isArray(globalTagsList));
      console.log('[TagDebug] Raw allPrompts from API:', allPrompts);
      console.log('[TagDebug] Is allPrompts an array?', Array.isArray(allPrompts));

      const listToProcess = Array.isArray(globalTagsList) ? globalTagsList : [];
      console.log('[TagDebug] listToProcess for tags (should be an array):', listToProcess);
      
      if (!Array.isArray(listToProcess)) {
        console.error('[TagDebug] CRITICAL: listToProcess is NOT an array before .map()!', listToProcess);
      }

      const processedTags = listToProcess.map(tagName => {
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


  const handleInlineTagSubmit = async () => {
    const tagName = inlineNewTagName.trim();
    if (!tagName) {
      message.error('Tag name cannot be empty');
      setIsAddingTag(false); // Still hide input on empty submit attempt via Enter
      setInlineNewTagName('');
      return;
    }
    await handleAddTag({ tagName }); // handleAddTag already sets loading and calls fetchGlobalTags
    setIsAddingTag(false);
    setInlineNewTagName('');
  };

  const handleInlineTagBlurOrCancel = () => {
    // On blur, simply hide the input and clear its value
    // If the user wants to submit, they should press Enter
    setIsAddingTag(false);
    setInlineNewTagName('');
  };

  return (
    <div className="tag-management-page">
      <Title level={2} style={{ marginBottom: '30px' }}>Tag Management</Title>

      <Spin spinning={loading} tip="Loading tags...">
        {tags.length > 0 ? (
          <Row gutter={[16, 16]}>
            {tags.map(tag => (
              <Col key={tag.name} xs={24} sm={12} md={8} lg={8} xl={8}>
                <Card className="tag-card-base tag-card">
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
            {/* Add Tag Card */}
            <Col xs={24} sm={12} md={8} lg={8} xl={8}>
              <Card
                size="small"
                hoverable
                className="tag-card-base add-tag-card"
                bodyStyle={{
                  /* Adjusted to ensure content within add-tag-card also centers if not handled by class */
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '100%'
                }}
                onClick={() => setIsAddingTag(true)}
              >
                {isAddingTag ? (
                  <Input
                    placeholder="New tag name"
                    value={inlineNewTagName}
                    onChange={(e) => setInlineNewTagName(e.target.value)}
                    onPressEnter={handleInlineTagSubmit}
                    onBlur={handleInlineTagBlurOrCancel}
                    autoFocus
                    style={{ margin: 'auto 0' }} // To help with centering
                  />
                ) : (
                  <>
                    <PlusOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
                    <div style={{ marginTop: 8 }}>Add Tag</div>
                  </>
                )}
              </Card>
            </Col>
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
