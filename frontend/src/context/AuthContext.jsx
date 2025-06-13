import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);
  const [loading, setLoading] = useState(true); // To track initial auth check

  const fetchCurrentUser = useCallback(async () => {
    if (authAPI.isAuthenticated()) {
      try {
        setLoading(true);
        const currentUser = await authAPI.getCurrentUser();
        setUser(currentUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to fetch current user:', error);
        // Token might be invalid or expired, so clear it
        authAPI.logout(); // This also removes token from localStorage
        setUser(null);
        setToken(null);
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const data = await authAPI.login(username, password);
      setToken(data.access_token);
      setIsAuthenticated(true);
      // Fetch user details after successful login
      await fetchCurrentUser(); 
      return data;
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
      setToken(null);
      console.error('Login error in AuthContext:', error);
      throw error; // Re-throw to be caught by the form
    } finally {
      setLoading(false);
    }
  };

  const signup = async (username, password) => {
    setLoading(true);
    try {
      const data = await authAPI.signup(username, password);
      // Typically, signup does not automatically log the user in.
      // User will be redirected to login or can login after signup.
      return data;
    } catch (error) {
      console.error('Signup error in AuthContext:', error);
      throw error; // Re-throw for form error handling
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    // Optionally, redirect to login page or home page
    // window.location.href = '/login'; // Example, better to use React Router navigation
  };

  const value = {
    user,
    token,
    isAuthenticated,
    loading, // Expose loading state for UI updates
    login,
    signup,
    logout,
    fetchCurrentUser // Expose if manual refresh is needed elsewhere
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined || context === null) { // Check for null as well as undefined
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
