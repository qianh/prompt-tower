import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Input, Select, message, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined, CopyOutlined, PoweroffOutlined } from '@ant-design/icons';
import { promptAPI } from '../services/api';
import { useAuth } from '../context/AuthContext'; // Import useAuth

const { Search } = Input;
const { Option } = Select;

const PromptList = ({ onEdit }) => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [searchIn, setSearchIn] = useState(['title', 'tags', 'content']);
  const { user } = useAuth(); // Get current user

  // 加载prompts
  const loadPrompts = async () => {
    setLoading(true);
    try {
      const data = await promptAPI.list();
      setPrompts(data);
    } catch (error) {
      message.error('加载失败：' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 搜索prompts
  const handleSearch = async (value) => {
    if (!value) {
      loadPrompts();
      return;
    }

    setLoading(true);
    try {
      const result = await promptAPI.search(value, searchIn);
      setPrompts(result.results);
    } catch (error) {
      message.error('搜索失败：' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 复制prompt
  const handleCopy = (record) => {
    navigator.clipboard.writeText(record.content);
    message.success('已复制到剪贴板');
  };

  // 删除prompt
  const handleDelete = async (title) => {
    try {
      await promptAPI.delete(title);
      message.success('删除成功');
      loadPrompts();
    } catch (error) {
      message.error('删除失败：' + error.message);
    }
  };

  // 切换状态
  const handleToggleStatus = async (title) => {
    try {
      await promptAPI.toggleStatus(title);
      message.success('状态已更新');
      loadPrompts();
    } catch (error) {
      message.error('操作失败：' + error.message);
    }
  };

  useEffect(() => {
    loadPrompts();
  }, []);

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
      render: (tags) => (
        <>
          {tags.map(tag => (
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
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
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
          placeholder="搜索prompt"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onSearch={handleSearch}
          style={{ width: 300 }}
        />
        <Select
          mode="multiple"
          style={{ width: 300 }}
          placeholder="选择搜索范围"
          value={searchIn}
          onChange={setSearchIn}
        >
          <Option value="title">标题</Option>
          <Option value="tags">标签</Option>
          <Option value="content">内容</Option>
        </Select>
        <Button type="primary" onClick={loadPrompts}>
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
