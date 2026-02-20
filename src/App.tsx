import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import MaterialPage from './pages/MaterialPage';
import LibraryPage from './pages/LibraryPage';
import ProfilePage from './pages/ProfilePage';
import ExerciseAccessPage from './pages/ExerciseAccessPage';
import ExercisePage from './pages/ExercisePage';
import PollPage from './pages/PollPage';
import AudioPage from './pages/AudioPage';
import VerifyPage from './pages/VerifyPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import MagicLoginPage from './pages/MagicLoginPage';
import UpgradePage from './pages/UpgradePage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/workspace" element={<ChatPage />} />
        <Route path="/material" element={<MaterialPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        {/* Backwards compatibility redirects */}
        <Route path="/chat" element={<Navigate to="/workspace" replace />} />
        <Route path="/curriculum" element={<Navigate to="/profile" replace />} />
        {/* Student-facing pages (no sidebar) */}
        <Route path="/s" element={<ExerciseAccessPage />} />
        <Route path="/s/:code" element={<ExercisePage />} />
        <Route path="/poll/:code" element={<PollPage />} />
        <Route path="/audio/:code" element={<AudioPage />} />
        {/* Auth pages */}
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/magic-login" element={<MagicLoginPage />} />
        <Route path="/upgrade" element={<UpgradePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
