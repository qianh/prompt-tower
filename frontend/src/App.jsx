import React, { useState } from "react";
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Button, Modal } from "antd";
import { PlusOutlined, LogoutOutlined } from "@ant-design/icons";
import PromptList from "./components/PromptList";
import PromptEditor from "./components/PromptEditor";
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import { promptAPI } from "./services/api";
import "./App.css";

const { Header, Content } = Layout;

// This is the main application layout for authenticated users
const MainAppLayout = () => {
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState(null);
  const [refreshList, setRefreshList] = useState(0);
  const { user, logout } = useAuth(); // Get user and logout function

  const handleEdit = (prompt = null) => {
    setCurrentPrompt(prompt);
    setEditModalVisible(true);
  };

  const handleSave = async (values) => {
    try {
      if (currentPrompt) {
        await promptAPI.update(currentPrompt.title, values);
      } else {
        await promptAPI.create(values);
      }
      setEditModalVisible(false);
      setRefreshList((prev) => prev + 1);
    } catch (error) {
      console.error("Save prompt failed:", error);
      // Consider showing a message to the user
    }
  };

  const handleLogout = () => {
    logout();
    // AuthProvider and ProtectedRoute will handle redirecting to login
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
        <div>
          {user && <span style={{ color: 'white', marginRight: '15px' }}>Welcome, {user.username}!</span>}
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleEdit()}
            style={{ marginRight: '10px' }}
          >
            新建Prompt
          </Button>
          <Button
            danger
            icon={<LogoutOutlined />}
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>
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
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/*" element={<ProtectedRoute />}>
        {/* Nested routes under ProtectedRoute render inside its Outlet */}
        {/* MainAppLayout will be the default for authenticated users at "/" and any sub-routes not matched*/}
        <Route index element={<MainAppLayout />} />
        {/* Example for future nested protected routes: */}
        {/* <Route path="dashboard" element={<DashboardPage />} /> */}
         {/* A catch-all for any other authenticated routes, rendering MainAppLayout or redirecting */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
