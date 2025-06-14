import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import TagManagementPage from './pages/TagManagementPage';
import PromptListPage from './pages/PromptListPage'; // Added
import ProtectedRoute from './components/ProtectedRoute';
import AuthenticatedLayout from './components/layout/AuthenticatedLayout'; // Added
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
          {/* Catch-all for authenticated routes, redirecting to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
