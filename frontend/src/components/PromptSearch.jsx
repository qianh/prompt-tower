import React, { useState } from 'react';
import { Input, Select, Space, Card, List, Tag, Empty, Spin } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { promptAPI } from '../services/api';

const { Search } = Input;
const { Option } = Select;

const PromptSearch = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [searchIn, setSearchIn] = useState(['title', 'tags', 'content']);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (value) => {
    if (!value.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }

    setLoading(true);
    setSearched(true);
    try {
      const response = await promptAPI.search(value, searchIn);
      setResults(response.results);
    } catch (error) {
      console.error('搜索失败:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const highlightText = (text, query) => {
    if (!query) return text;
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <span key={index} className="search-highlight">{part}</span> : part
    );
  };

  return (
    <Card title="Prompt搜索" style={{ marginBottom: 24 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space style={{ width: '100%' }}>
          <Search
            placeholder="输入搜索关键词"
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={handleSearch}
            style={{ width: 400 }}
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
        </Space>

        <Spin spinning={loading}>
          {searched && results.length === 0 ? (
            <Empty description="没有找到匹配的Prompt" />
          ) : (
            <List
              dataSource={results}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Space>
                        <span>{item.title}</span>
                        {item.tags.map(tag => (
                          <Tag key={tag} color="blue">{tag}</Tag>
                        ))}
                      </Space>
                    }
                    description={
                      <div className="prompt-content-preview">
                        {item.content.substring(0, 200)}
                        {item.content.length > 200 && '...'}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Space>
    </Card>
  );
};

export default PromptSearch;
