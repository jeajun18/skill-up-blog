import { createContext, useContext, useState, useEffect } from 'react';
import axios from '../utils/axios';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, username: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      // TODO: 사용자 정보 가져오기
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      console.log('Login attempt:', { email });
      const response = await axios.post('/users/token/', {
        email,
        password,
      });
      console.log('Login response:', response.data);
      
      if (!response.data.access) {
        throw new Error('토큰을 받지 못했습니다.');
      }

      localStorage.setItem('token', response.data.access);
      setIsAuthenticated(true);
      
      if (response.data.user) {
        setUser(response.data.user);
      } else {
        try {
          const userResponse = await axios.get('/users/me/');
          setUser(userResponse.data);
        } catch (error) {
          console.error('Failed to fetch user data:', error);
        }
      }
    } catch (error: any) {
      console.error('Login error:', error.response?.data);
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          '로그인에 실패했습니다.';
      throw new Error(errorMessage);
    }
  };

  const register = async (email: string, password: string, username: string) => {
    try {
      console.log('Register attempt:', { email, username });
      const response = await axios.post('/users/register/', {
        email,
        password,
        username,
      });
      console.log('Register response:', response.data);
      
      await login(email, password);
    } catch (error: any) {
      console.error('Register error:', error.response?.data);
      const errorData = error.response?.data;
      if (errorData) {
        const message = errorData.detail || 
                       errorData.email?.[0] || 
                       errorData.username?.[0] || 
                       errorData.password?.[0] || 
                       '회원가입에 실패했습니다.';
        throw new Error(message);
      }
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 