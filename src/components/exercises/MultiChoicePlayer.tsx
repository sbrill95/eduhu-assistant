import { useState } from 'react';

interface Answer {
  text: string;
  correct: boolean;
  tipsAndFeedback: {
    chosenFeedback: string;
  };
}

interface MultiChoicePlayerProps {
  content: {
    question: string;
    answers: Answer[];
    UI: {
      checkAnswerButton: string;
      showSolutionButton: string;
      tryAgainButton: string;
    };
  };
  onComplete?: (score: number) => void;
}

export function MultiChoicePlayer({ content, onComplete }: MultiChoicePlayerProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);

  const stripHtml = (html: string) => {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return doc.body.textContent || '';
  };

  const handleCheckAnswer = () => {
    if (selectedAnswer === null) return;
    const correct = content.answers[selectedAnswer ?? 0]!.correct;
    setIsCorrect(correct);
    setShowFeedback(true);
    if (correct && onComplete) {
      onComplete(1);
    }
  };

  const handleShowSolution = () => {
    setShowSolution(true);
  };

  const handleRetry = () => {
    setSelectedAnswer(null);
    setShowFeedback(false);
    setShowSolution(false);
    setIsCorrect(false);
  };

  const getCardClassName = (index: number) => {
    let className = 'p-4 rounded-xl shadow cursor-pointer transition-colors';
    if (showFeedback && selectedAnswer === index) {
      className += content.answers[index]!.correct ? ' bg-green-100 border-green-500' : ' bg-red-100 border-red-500';
    } else if (showSolution && content.answers[index]!.correct) {
      className += ' bg-green-100 border-green-500';
    } else {
      className += ' bg-white hover:bg-gray-100';
    }
    if (selectedAnswer === index) {
      className += ' ring-2 ring-primary';
    }
    return className;
  };

  return (
    <div className="p-6 bg-[#F5F0EB] font-inter">
      <h2 className="text-xl font-bold mb-4">{stripHtml(content.question)}</h2>
      <div className="space-y-4">
        {content.answers.map((answer, index) => (
          <div
            key={index}
            className={getCardClassName(index)}
            onClick={() => !showFeedback && setSelectedAnswer(index)}
          >
            {stripHtml(answer.text)}
            {showFeedback && selectedAnswer === index && (
              <p className="mt-2 text-sm">{stripHtml(answer.tipsAndFeedback.chosenFeedback)}</p>
            )}
          </div>
        ))}
      </div>
      <div className="mt-6">
        {!showFeedback ? (
          <button
            onClick={handleCheckAnswer}
            disabled={selectedAnswer === null}
            className="px-4 py-2 bg-[#C8552D] text-white rounded-lg disabled:opacity-50"
          >
            {content.UI.checkAnswerButton}
          </button>
        ) : (
          <div className="flex space-x-4">
            {!isCorrect && (
              <button onClick={handleShowSolution} className="px-4 py-2 bg-[#C8552D] text-white rounded-lg">
                {content.UI.showSolutionButton}
              </button>
            )}
            <button onClick={handleRetry} className="px-4 py-2 bg-[#C8552D] text-white rounded-lg">
              {content.UI.tryAgainButton}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}