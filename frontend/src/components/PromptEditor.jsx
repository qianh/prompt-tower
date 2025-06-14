import React, { useState, useEffect } from "react";
import { Form, Input, Select, Button, Space, message, Spin, Alert } from "antd";
import { llmAPI, tagAPI } from "../services/api"; // Import tagAPI

const { TextArea } = Input;
const { Option } = Select; // Option might not be needed if using options prop for Select

const PromptEditor = ({ prompt, onSave, onCancel }) => {
  const [form] = Form.useForm();
  const [optimizing, setOptimizing] = useState(false);
  const [optimizeError, setOptimizeError] = useState(null);
  const [globalTags, setGlobalTags] = useState([]); // State for storing global tags
  const [loadingTags, setLoadingTags] = useState(false);

  useEffect(() => {
    // 加载LLM提供商 (original logic)
    llmAPI.getProviders().then((data) => {
      // console.log("LLM Providers:", data);
    }).catch(error => {
      console.error("Failed to load LLM providers:", error);
      // message.error("加载LLM提供商失败"); // Optional: user-facing error
    });

    // 加载全局标签
    setLoadingTags(true);
    tagAPI.list().then((tags) => {
      setGlobalTags(Array.isArray(tags) ? tags : []);
    }).catch(error => {
      console.error("Failed to load global tags:", error);
      message.error("加载全局标签列表失败");
      setGlobalTags([]); // Ensure it's an array on error
    }).finally(() => {
      setLoadingTags(false);
    });

    // 如果是编辑模式，填充表单
    if (prompt) {
      form.setFieldsValue({
        title: prompt.title,
        content: prompt.content,
        tags: prompt.tags || [], // Ensure tags is an array
        remark: prompt.remark,
        status: prompt.status,
      });
    } else {
      form.resetFields(); // Reset for new prompt
      form.setFieldsValue({ status: "enabled", tags: [] }); // Default values for new prompt
    }
  }, [prompt, form]);

  // 优化prompt
  const handleOptimize = async () => {
    const content = form.getFieldValue("content");
    if (!content) {
      message.warning("请先输入prompt内容");
      return;
    }
    setOptimizing(true);
    setOptimizeError(null);
    try {
      const result = await llmAPI.optimize(content);
      form.setFieldValue("content", result.optimized);
      if (result.suggestions && result.suggestions.length > 0) {
        message.info(
          <div>
            <p>优化建议：</p>
            <ul>
              {result.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>,
          10
        );
      }
    } catch (error) {
      console.error("优化失败:", error);
      const errorMsg = error.response?.data?.detail || error.message || "优化失败，请稍后重试";
      setOptimizeError(errorMsg);
      if (errorMsg.includes("超时")) {
        message.warning("LLM处理时间较长，请耐心等待或尝试使用其他模型", 5);
      } else {
        message.error("优化失败：" + errorMsg);
      }
    } finally {
      setOptimizing(false);
    }
  };

  // 保存prompt
  const handleSubmit = async (values) => {
    try {
      // Ensure tags are an array, even if cleared in the form
      const payload = {
        ...values,
        tags: Array.isArray(values.tags) ? values.tags : [],
      };
      await onSave(payload);
      message.success("保存成功");
      form.resetFields();
      form.setFieldsValue({ status: "enabled", tags: [] }); // Reset to defaults for new prompt
      // Optionally, refresh global tags if a new tag might have been added
      // This might be redundant if backend automatically syncs and other components re-fetch
      tagAPI.list().then(tags => setGlobalTags(Array.isArray(tags) ? tags : [])).catch(console.error);
    } catch (error) {
      message.error("保存失败：" + (error.response?.data?.detail || error.message));
    }
  };

  const tagOptions = globalTags.map(tag => ({ label: tag, value: tag }));

  return (
    <div>
      {optimizeError && (
        <Alert
          message="优化提示"
          description={optimizeError}
          type="warning"
          closable
          onClose={() => setOptimizeError(null)}
          style={{ marginBottom: 16 }}
        />
      )}

      <Spin spinning={optimizing || loadingTags} tip={loadingTags ? "加载标签中..." : "AI正在优化中，请耐心等待（最长60秒）..."}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            status: "enabled",
            tags: [],
          }}
        >
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: "请输入标题" }]}
          >
            <Input placeholder="输入唯一的标题" disabled={!!prompt} />
          </Form.Item>

          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: "请输入内容" }]}
          >
            <TextArea rows={10} placeholder="输入prompt内容" />
          </Form.Item>

          <Form.Item>
            <Button
              onClick={handleOptimize}
              loading={optimizing}
              disabled={optimizing}
            >
              {optimizing ? "优化中..." : "使用AI优化"}
            </Button>
            {optimizing && (
              <span style={{ marginLeft: 10, color: "#999" }}>
                处理可能需要较长时间，请勿关闭页面
              </span>
            )}
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <Select
              mode="tags"
              style={{ width: "100%" }}
              placeholder="选择或输入标签，按回车确认"
              options={tagOptions} // Provide global tags as options
              filterOption={(inputValue, option) => 
                option.value.toUpperCase().indexOf(inputValue.toUpperCase()) !== -1
              } // Basic case-insensitive filtering for dropdown
            />
          </Form.Item>

          <Form.Item name="remark" label="备注">
            <TextArea rows={3} placeholder="输入备注说明" />
          </Form.Item>

          <Form.Item name="status" label="状态">
            <Select defaultValue="enabled">
              <Option value="enabled">启用</Option>
              <Option value="disabled">禁用</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={onCancel}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Spin>
    </div>
  );
};

export default PromptEditor;
