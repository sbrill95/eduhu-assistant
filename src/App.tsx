import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import CurriculumPage from './pages/CurriculumPage';
import ProfilePage from './pages/ProfilePage';
import MaterialPage from './pages/MaterialPage';
import ExerciseAccessPage from './pages/ExerciseAccessPage';
import ExercisePage from './pages/ExercisePage';
import PollPage from './pages/PollPage';
import AudioPage from './pages/AudioPage';
import VerifyPage from './pages/VerifyPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import MagicLoginPage from './pages/MagicLoginPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/curriculum" element={<CurriculumPage />} />
        <Route path="/material" element={<MaterialPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/s" element={<ExerciseAccessPage />} />
        <Route path="/s/:code" element={<ExercisePage />} />
        <Route path="/poll/:code" element={<PollPage />} />
        <Route path="/audio/:code" element={<AudioPage />} />
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/magic-login" element={<MagicLoginPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
