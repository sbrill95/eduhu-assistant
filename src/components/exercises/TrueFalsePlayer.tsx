import { useState } from 'react';

interface TrueFalsePlayerProps {
  content: {
    question: string;
    correct: string;
    l10n: {
      trueText: string;
      falseText: string;
      checkAnswer: string;
    };
  };
  onComplete?: (score: number) => void;
}

export function TrueFalsePlayer({ content, onComplete }: TrueFalsePlayerProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<boolean | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleAnswer = (answer: boolean) => {
    setSelectedAnswer(answer);
    const isCorrect = (answer ? 'true' : 'false') === content.correct;
    setShowFeedback(true);
    if (isCorrect && onComplete) {
      onComplete(1);
    }
  };

  const getButtonClassName = (isTrueButton: boolean) => {
    let className = 'p-4 rounded-xl shadow w-full text-center cursor-pointer transition-colors';
    if (showFeedback && selectedAnswer === isTrueButton) {
      const isCorrect = (selectedAnswer ? 'true' : 'false') === content.correct;
      className += isCorrect ? ' bg-green-500 text-white' : ' bg-red-500 text-white';
    } else {
      className += ' bg-white hover:bg-gray-100';
    }
    return className;
  };

  return (
    <div className="p-6 bg-[#F5F0EB] font-inter">
      <h2 className="text-xl font-bold mb-4 text-center">{content.question}</h2>
      <div className="flex space-x-4">
        <div className={getButtonClassName(true)} onClick={() => !showFeedback && handleAnswer(true)}>
          {content.l10n.trueText}
        </div>
        <div className={getButtonClassName(false)} onClick={() => !showFeedback && handleAnswer(false)}>
          {content.l10n.falseText}
        </div>
      </div>
      {showFeedback && (
        <div className="mt-4 text-center">
          <button
            onClick={() => {
              setSelectedAnswer(null);
              setShowFeedback(false);
            }}
            className="px-4 py-2 bg-[#C8552D] text-white rounded-lg"
          >
            Wiederholen
          </button>
        </div>
      )}
    </div>
  );
}