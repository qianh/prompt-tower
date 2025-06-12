import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, Alert, Spin, Space, Divider } from 'antd';
import { BulbOutlined, RocketOutlined } from '@ant-design/icons';
import { llmAPI } from '../services/api';

const { TextArea } = Input;
const { Option } = Select;

const LLMOptimizer = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [providers, setProviders] = useState([]);
  const [result, setResult] = useState(null);

  useEffect(() => {
    // 加载可用的LLM提供商
    llmAPI.getProviders().then(data => {
      setProviders(data.providers || []);
    }).catch(error => {
      console.error('加载LLM提供商失败:', error);
    });
  }, []);

  const handleOptimize = async (values) => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await llmAPI.optimize(
        values.content,
        values.context,
        values.provider
      );
      setResult(response);
    } catch (error) {
      console.error('优化失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板');
  };

  return (
    <Card 
      title={
        <Space>
          <RocketOutlined />
          <span>AI Prompt优化器</span>
        </Space>
      }
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleOptimize}
        initialValues={{ provider: 'gemini' }}
      >
        <Form.Item
          name="content"
          label="原始Prompt"
          rules={[{ required: true, message: '请输入要优化的prompt' }]}
        >
          <TextArea
            rows={6}
            placeholder="输入您想要优化的prompt内容..."
          />
        </Form.Item>

        <Form.Item
          name="context"
          label="上下文信息（可选）"
        >
          <TextArea
            rows={3}
            placeholder="提供额外的上下文信息，帮助AI更好地理解您的需求..."
          />
        </Form.Item>

        <Form.Item
          name="provider"
          label="AI模型"
        >
          <Select>
            {providers.map(provider => (
              <Option key={provider} value={provider}>
                {provider.charAt(0).toUpperCase() + provider.slice(1)}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<BulbOutlined />}
            size="large"
          >
            开始优化
          </Button>
        </Form.Item>
      </Form>

      {loading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" tip="AI正在优化您的Prompt..." />
        </div>
      )}

      {result && (
        <>
          <Divider />
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="优化完成"
              description="AI已经为您优化了Prompt，请查看下方结果"
              type="success"
              showIcon
            />
            
            <Card
              title="优化后的Prompt"
              extra={
                <Button onClick={() => copyToClipboard(result.optimized)}>
                  复制
                </Button>
              }
            >
              <pre style={{ whiteSpace: 'pre-wrap' }}>{result.optimized}</pre>
            </Card>

            {result.suggestions && result.suggestions.length > 0 && (
              <Card title="优化建议">
                <ul>
                  {result.suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              </Card>
            )}
          </Space>
        </>
      )}
    </Card>
  );
};

export default LLMOptimizer;
