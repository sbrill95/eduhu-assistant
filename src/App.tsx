import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '@/pages/LoginPage';
import ChatPage from '@/pages/ChatPage';
import CurriculumPage from '@/pages/CurriculumPage';
import ProfilePage from '@/pages/ProfilePage';
import MaterialPage from '@/pages/MaterialPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/curriculum" element={<CurriculumPage />} />
        <Route path="/material" element={<MaterialPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
