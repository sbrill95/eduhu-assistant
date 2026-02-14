import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { H5PPlayer } from '../components/exercises/H5PPlayer';

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

interface Exercise {
  id: string;
  title: string;
  h5p_type: string;
}

const ExercisePage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const [pageTitle, setPageTitle] = useState('');
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [activeExercise, setActiveExercise] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!code) return;
    fetch(`${API_BASE}/api/public/pages/${code}`)
      .then((res) => {
        if (!res.ok) throw new Error('Seite nicht gefunden');
        return res.json();
      })
      .then((data) => {
        setPageTitle(data.page.title);
        setExercises(data.exercises);
      })
      .catch(() => setError('Seite konnte nicht geladen werden.'))
      .finally(() => setLoading(false));
  }, [code]);

  const getIconForType = (type: string) => {
    switch (type) {
      case 'H5P.MultiChoice': return '📝';
      case 'H5P.Blanks': return '🔤';
      case 'H5P.TrueFalse': return '✅';
      case 'H5P.DragText': return '🔀';
      default: return '📄';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F5F0EB] flex items-center justify-center font-[Inter]">
        <div className="text-lg text-gray-600">Lade...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F5F0EB] flex items-center justify-center font-[Inter]">
        <div className="text-lg text-red-600">{error}</div>
      </div>
    );
  }

  if (activeExercise) {
    return (
      <div className="min-h-screen bg-[#F5F0EB] p-5 font-[Inter]">
        <button
          onClick={() => setActiveExercise(null)}
          className="mb-5 bg-[#C8552D] text-white border-none py-2.5 px-5 rounded-lg cursor-pointer hover:bg-[#A8461F] transition-colors"
        >
          ← Zurück zur Übersicht
        </button>
        <H5PPlayer exerciseId={activeExercise} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F5F0EB] font-[Inter] p-5">
      <header className="text-center mb-10">
        <div className="text-5xl mb-3">🦉</div>
        <h1 className="text-3xl font-bold text-[#2D2018]">{pageTitle}</h1>
        <p className="text-gray-500 mt-2">Wähle eine Übung aus</p>
      </header>
      <div className="grid gap-5 max-w-4xl mx-auto" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
        {exercises.map((exercise) => (
          <div
            key={exercise.id}
            onClick={() => setActiveExercise(exercise.id)}
            className="bg-white rounded-xl shadow-md p-6 text-center cursor-pointer hover:scale-[1.03] hover:shadow-lg transition-all"
          >
            <div className="text-5xl mb-3">{getIconForType(exercise.h5p_type)}</div>
            <h2 className="text-lg font-semibold text-[#2D2018] mb-3">{exercise.title}</h2>
            <span className="text-xs text-gray-400">{exercise.h5p_type.replace('H5P.', '')}</span>
            <div className="mt-4">
              <button className="bg-[#C8552D] text-white border-none py-2 px-6 rounded-lg cursor-pointer hover:bg-[#A8461F] transition-colors">
                Starten
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExercisePage;
