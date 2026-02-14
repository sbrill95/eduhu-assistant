import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ExerciseAccessPage: React.FC = () => {
  const [accessCode, setAccessCode] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (accessCode.trim()) {
      navigate(`/s/${accessCode.trim()}`);
    }
  };

  return (
    <div style={{ backgroundColor: '#F5F0EB', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter, sans-serif' }}>
      <div style={{ backgroundColor: 'white', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', textAlign: 'center' }}>
        <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Gib deinen Zugangscode ein</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={accessCode}
            onChange={(e) => setAccessCode(e.target.value)}
            placeholder="Zugangscode"
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #ccc',
              fontSize: '16px',
              marginBottom: '20px',
            }}
          />
          <button
            type="submit"
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: '#C8552D',
              color: 'white',
              fontSize: '16px',
              cursor: 'pointer',
              fontWeight: 'bold',
            }}
          >
            Los!
          </button>
        </form>
      </div>
    </div>
  );
};

export default ExerciseAccessPage;
