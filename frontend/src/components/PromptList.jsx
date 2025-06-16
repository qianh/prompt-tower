import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, Tag, Input, Select, message, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined, CopyOutlined, PoweroffOutlined } from '@ant-design/icons';
import { promptAPI, tagAPI } from '../services/api'; // Import tagAPI
import { useAuth } from '../context/AuthContext'; // Import useAuth

const { Search } = Input;
const { Option } = Select;

const PromptList = ({ onEdit }) => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  // const [searchIn, setSearchIn] = useState(['title', 'tags', 'content']); // searchIn is not used for text search currently
  const [allTags, setAllTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState(undefined); // To store the selected tag for filtering
  const { user } = useAuth(); // Get current user

  const loadPrompts = useCallback(async (tagFilter) => {
    setLoading(true);
    try {
      const params = {};
      if (tagFilter) {
        params.tag = tagFilter;
      }
      const data = await promptAPI.list(params);
      setPrompts(data);
      setSearchValue(''); 
    } catch (error) {
      message.error('加载 prompts 失败：' + error.message);
    } finally {
      setLoading(false);
    }
  }, []); 

  const loadTags = useCallback(async () => {
    try {
      const tagsData = await tagAPI.list(); // Use tagAPI.list()
      setAllTags(tagsData || []);
    } catch (error) {
      message.error('加载标签失败：' + error.message);
    }
  }, []);

  useEffect(() => {
    loadPrompts();
    loadTags();
  }, [loadPrompts, loadTags]);

  const handleSearch = async (value) => {
    const query = value.trim();
    if (!query) {
      loadPrompts(selectedTag);
      return;
    }
    setLoading(true);
    setSelectedTag(undefined); 
    try {
      // Defaulting searchIn to all fields if not specified or UI element removed
      const result = await promptAPI.search(query, ['title', 'tags', 'content']); 
      setPrompts(result.results || []);
    } catch (error) {
      message.error('搜索失败：' + error.message);
      setPrompts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTagFilterChange = (tag) => {
    setSelectedTag(tag);
    loadPrompts(tag);
  };

  const handleCopy = async (record) => {
    navigator.clipboard.writeText(record.content);
    message.success('已复制到剪贴板');
    try {
      await promptAPI.incrementUsageCount(record.title);
      message.success('使用次数已增加');
      loadPrompts(selectedTag); // Reload prompts to show updated usage count
    } catch (error) {
      message.error('更新使用次数失败: ' + error.message);
      console.error('Failed to increment usage count:', error);
    }
  };

  const handleDelete = async (title) => {
    try {
      await promptAPI.delete(title);
      message.success('删除成功');
      loadPrompts(selectedTag); 
    } catch (error) {
      message.error('删除失败：' + error.message);
    }
  };

  const handleToggleStatus = async (title) => {
    try {
      await promptAPI.toggleStatus(title);
      message.success('状态已更新');
      loadPrompts(selectedTag); 
    } catch (error) {
      message.error('操作失败：' + error.message);
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tagsArray) => (
        <>
          {tagsArray && tagsArray.map(tag => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
        </>
      ),
    },
    {
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={status === 'enabled' ? 'green' : 'default'}>
          {status === 'enabled' ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
      width: 150,
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 250,
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
          />
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => onEdit(record)}
            disabled={!user || record.creator_username !== user.username}
          />
          <Button
            size="small"
            icon={<PoweroffOutlined />}
            onClick={() => handleToggleStatus(record.title)}
            disabled={!user || record.creator_username !== user.username}
          />
          <Popconfirm
            title="确定要删除吗？"
            onConfirm={() => handleDelete(record.title)}
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={!user || record.creator_username !== user.username}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Search
          placeholder="搜索prompt (标题、标签、内容)"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onSearch={handleSearch}
          style={{ width: 300 }}
          allowClear
        />
        <Select
          style={{ width: 200 }}
          placeholder="按标签过滤"
          value={selectedTag}
          onChange={handleTagFilterChange}
          allowClear
        >
          <Option value={undefined}>所有标签</Option>
          {allTags.map(tag => (
            <Option key={tag} value={tag}>{tag}</Option>
          ))}
        </Select>
        <Button type="primary" onClick={() => loadPrompts(selectedTag)}>
          刷新
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={prompts}
        rowKey="title"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />
    </div>
  );
};

export default PromptList;
