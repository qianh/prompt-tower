import React, { useState } from "react";
import { Layout, Button, Modal } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import PromptList from "./components/PromptList";
import PromptEditor from "./components/PromptEditor";
import { promptAPI } from "./services/api";
import "./App.css";

const { Header, Content } = Layout;

function App() {
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState(null);
  const [refreshList, setRefreshList] = useState(0);

  // 打开编辑器
  const handleEdit = (prompt = null) => {
    setCurrentPrompt(prompt);
    setEditModalVisible(true);
  };

  // 保存prompt
  const handleSave = async (values) => {
    if (currentPrompt) {
      // 更新
      await promptAPI.update(currentPrompt.title, values);
    } else {
      // 创建
      await promptAPI.create(values);
    }
    setEditModalVisible(false);
    setRefreshList((prev) => prev + 1);
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <h1 style={{ color: "white", margin: 0 }}>Prompt管理系统</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => handleEdit()}
        >
          新建Prompt
        </Button>
      </Header>

      <Content style={{ padding: "24px" }}>
        <PromptList onEdit={handleEdit} key={refreshList} />
      </Content>

      <Modal
        title={currentPrompt ? "编辑Prompt" : "新建Prompt"}
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
}

export default App;
