import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import TagManagementPage from './pages/TagManagementPage';
import PromptListPage from './pages/PromptListPage'; 
import UserManagementPage from './pages/UserManagementPage'; 
import ProtectedRoute from './components/ProtectedRoute';
import AuthenticatedLayout from './components/layout/AuthenticatedLayout'; 
import "./App.css";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* Protected Routes with AuthenticatedLayout */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AuthenticatedLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="prompts" element={<PromptListPage />} />
          <Route path="tags" element={<TagManagementPage />} />
          <Route path="users" element={<UserManagementPage />} />
          {/* Catch-all for authenticated routes, redirecting to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
