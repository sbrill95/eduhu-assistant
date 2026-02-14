import { useState, useMemo } from 'react';

interface BlanksPlayerProps {
  content: {
    text: string;
  };
  onComplete?: (score: number) => void;
}

type Part = { type: 'text'; value: string } | { type: 'blank'; blankIndex: number };

export function BlanksPlayer({ content, onComplete }: BlanksPlayerProps) {
  const [answers, setAnswers] = useState<string[]>([]);
  const [showFeedback, setShowFeedback] = useState(false);

  const { parsed, correctAnswers } = useMemo(() => {
    const stripped = content.text.replace(/<[^>]*>/g, '');
    const regex = /\*([^*]+)\*/g;
    const correct: string[] = [];
    const result: Part[] = [];
    let lastIndex = 0;
    let match;
    while ((match = regex.exec(stripped)) !== null) {
      if (match.index > lastIndex) {
        result.push({ type: 'text', value: stripped.slice(lastIndex, match.index) });
      }
      correct.push(match[1] ?? "");
      result.push({ type: 'blank', blankIndex: correct.length - 1 });
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < stripped.length) {
      result.push({ type: 'text', value: stripped.slice(lastIndex) });
    }
    return { parsed: result, correctAnswers: correct };
  }, [content.text]);

  // Init answers on first render
  if (answers.length === 0 && correctAnswers.length > 0) {
    setAnswers(new Array(correctAnswers.length).fill(''));
  }

  const handleCheckAnswer = () => {
    setShowFeedback(true);
    const score = answers.reduce((acc, answer, index) => {
      return acc + (answer.toLowerCase().trim() === (correctAnswers[index] ?? "").toLowerCase().trim() ? 1 : 0);
    }, 0);
    if (onComplete) onComplete(score / correctAnswers.length);
  };

  const handleRetry = () => {
    setAnswers(new Array(correctAnswers.length).fill(''));
    setShowFeedback(false);
  };

  return (
    <div className="p-6 bg-[#F5F0EB]" style={{ fontFamily: 'Inter, sans-serif' }}>
      <div className="text-lg leading-relaxed">
        {parsed.map((part, i) =>
          part.type === 'text' ? (
            <span key={i}>{part.value}</span>
          ) : (
            <span key={i} className="inline-block mx-1">
              <input
                type="text"
                value={answers[part.blankIndex] ?? ''}
                onChange={(e) => {
                  const next = [...answers];
                  next[part.blankIndex] = e.target.value;
                  setAnswers(next);
                }}
                disabled={showFeedback}
                className={`w-32 rounded-lg border p-1 text-center ${
                  showFeedback
                    ? answers[part.blankIndex]?.toLowerCase().trim() === correctAnswers[part.blankIndex]?.toLowerCase().trim()
                      ? 'border-green-500 bg-green-100'
                      : 'border-red-500 bg-red-100'
                    : 'border-gray-300 focus:border-[#C8552D] focus:ring-1 focus:ring-[#C8552D]'
                }`}
              />
              {showFeedback && answers[part.blankIndex]?.toLowerCase().trim() !== correctAnswers[part.blankIndex]?.toLowerCase().trim() && (
                <span className="ml-1 text-sm text-green-700">({correctAnswers[part.blankIndex]})</span>
              )}
            </span>
          )
        )}
      </div>
      <div className="mt-6">
        {!showFeedback ? (
          <button onClick={handleCheckAnswer} className="px-4 py-2 bg-[#C8552D] text-white rounded-lg">
            Überprüfen
          </button>
        ) : (
          <button onClick={handleRetry} className="px-4 py-2 bg-[#C8552D] text-white rounded-lg">
            Wiederholen
          </button>
        )}
      </div>
    </div>
  );
}
