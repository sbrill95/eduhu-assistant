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
      case 'H5P.QuestionSet': return '📋';
      case 'H5P.Blanks': return '🔤';
      case 'H5P.TrueFalse': return '✅';
      case 'H5P.DragText': return '🔀';
      default: return '📄';
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'H5P.MultiChoice': 'Multiple Choice',
      'H5P.QuestionSet': 'Quiz',
      'H5P.Blanks': 'Lückentext',
      'H5P.TrueFalse': 'Wahr oder Falsch',
      'H5P.DragText': 'Wörter zuordnen',
    };
    return labels[type] || type.replace('H5P.', '');
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
    const currentIndex = exercises.findIndex(e => e.id === activeExercise);
    const currentExercise = exercises[currentIndex];
    const hasNext = currentIndex < exercises.length - 1;
    const hasPrev = currentIndex > 0;

    return (
      <div className="min-h-screen bg-[#F5F0EB] p-5 font-[Inter]">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => setActiveExercise(null)}
              className="text-[#8B7355] hover:text-[#2D2018] transition-colors text-sm flex items-center gap-1"
            >
              ← Übersicht
            </button>
            {exercises.length > 1 && (
              <span className="text-sm text-[#8B7355]">
                {currentIndex + 1} / {exercises.length}
              </span>
            )}
          </div>
          {currentExercise && (
            <h2 className="text-lg font-semibold text-[#2D2018] mb-4">{currentExercise.title}</h2>
          )}
          <H5PPlayer exerciseId={activeExercise} />
          {exercises.length > 1 && (
            <div className="flex justify-between mt-4">
              {hasPrev ? (
                <button
                  onClick={() => setActiveExercise(exercises[currentIndex - 1]?.id ?? null)}
                  className="text-[#C8552D] hover:text-[#A8461F] text-sm font-medium"
                >
                  ← Vorherige
                </button>
              ) : <div />}
              {hasNext && (
                <button
                  onClick={() => setActiveExercise(exercises[currentIndex + 1]?.id ?? null)}
                  className="bg-[#C8552D] text-white py-2 px-5 rounded-lg hover:bg-[#A8461F] transition-colors text-sm font-medium"
                >
                  Nächste →
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F5F0EB] font-[Inter] p-5">
      <header className="text-center mb-8">
        <div className="text-5xl mb-3">🦉</div>
        <h1 className="text-2xl font-bold text-[#2D2018]">{pageTitle}</h1>
        <p className="text-[#8B7355] mt-1 text-sm">{exercises.length} Übungen</p>
      </header>
      <div className="max-w-2xl mx-auto space-y-3">
        {exercises.map((exercise, index) => (
          <div
            key={exercise.id}
            onClick={() => setActiveExercise(exercise.id)}
            className="bg-white rounded-xl shadow-sm p-4 cursor-pointer hover:shadow-md hover:bg-[#FAF7F4] transition-all flex items-center gap-4"
          >
            <div className="w-10 h-10 rounded-lg bg-[#FADDD0] flex items-center justify-center text-lg flex-shrink-0">
              {getIconForType(exercise.h5p_type)}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-sm font-semibold text-[#2D2018] line-clamp-2">{exercise.title}</h2>
              <span className="text-xs text-[#8B7355]">{getTypeLabel(exercise.h5p_type)}</span>
            </div>
            <div className="flex-shrink-0 text-[#8B7355] text-sm">
              {index + 1}/{exercises.length}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExercisePage;
