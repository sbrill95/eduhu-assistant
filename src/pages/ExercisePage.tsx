import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ExercisePlayer } from '../components/exercises/ExercisePlayer';
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

const getPageData = async (code: string) => {
  const res = await fetch(`${API_BASE}/api/public/pages/${code}`);
  if (!res.ok) throw new Error('Page not found');
  return res.json();
};

const getExerciseData = async (id: string) => {
  const res = await fetch(`${API_BASE}/api/public/exercises/${id}`);
  if (!res.ok) throw new Error('Exercise not found');
  return res.json();
};


const ExercisePage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const [page, setPage] = useState<{ title: string; description: string } | null>(null);
  const [exercises, setExercises] = useState<{ id: string; title: string; h5p_type: string }[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (code) {
      getPageData(code)
        .then((data: any) => {
          setPage({ title: data.page.title, description: '' });
          setExercises(data.exercises);
        })
        .catch(() => setError('Seite konnte nicht geladen werden.'))
        .finally(() => setLoading(false));
    }
  }, [code]);

  const handleExerciseClick = (exerciseId: string) => {
    getExerciseData(exerciseId)
        .then((data) => setSelectedExercise(data))
        .catch(() => setError('Übung konnte nicht geladen werden.'));
  };

  const getIconForType = (type: string) => {
    switch (type) {
      case 'multichoice': return '📝';
      case 'blanks': return '🔤';
      case 'truefalse': return '✅';
      case 'dragtext': return '🔀';
      default: return '📄';
    }
  };

  if (loading) {
    return <div style={{ backgroundColor: '#F5F0EB', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Lade...</div>;
  }

  if (error) {
    return <div style={{ backgroundColor: '#F5F0EB', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{error}</div>;
  }
  
  if (selectedExercise) {
    return (
      <div style={{ backgroundColor: '#F5F0EB', minHeight: '100vh', padding: '20px', fontFamily: 'Inter, sans-serif' }}>
        <button onClick={() => setSelectedExercise(null)} style={{ marginBottom: '20px', backgroundColor: '#C8552D', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer' }}>Zurück</button>
        <ExercisePlayer h5pType={selectedExercise.h5p_type} content={selectedExercise.h5p_content} />
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#F5F0EB', minHeight: '100vh', fontFamily: 'Inter, sans-serif', padding: '20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '36px', color: '#333' }}>{page?.title}</h1>
      </header>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        {exercises.map((exercise) => (
          <div
            key={exercise.id}
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              padding: '20px',
              textAlign: 'center',
              transition: 'transform 0.2s',
              cursor: 'pointer',
            }}
            onClick={() => handleExerciseClick(exercise.id)}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <div style={{ fontSize: '48px' }}>{getIconForType(exercise.h5p_type)}</div>
            <h2 style={{ fontSize: '20px', margin: '10px 0' }}>{exercise.title}</h2>
            <button style={{ backgroundColor: '#C8552D', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer' }}>Starten</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExercisePage;
