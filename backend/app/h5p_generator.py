import uuid

def generate_multichoice(question: str, answers: list[dict]) -> dict:
    """
    Generate H5P.MultiChoice content.json.
    answers = [{"text": "...", "correct": bool, "feedback": "..."}, ...]
    """
    formatted_answers = []
    for ans in answers:
        formatted_answers.append({
            "correct": ans.get("correct", False),
            "tipsAndFeedback": {
                "tip": "",
                "chosenFeedback": ans.get("feedback", ""),
                "notChosenFeedback": ""
            },
            "text": f"<div>{ans.get('text', '')}</div>"
        })

    return {
        "question": f"<p>{question}</p>",
        "answers": formatted_answers,
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
            "type": "auto",
            "singlePoint": False,
            "randomAnswers": True,
            "showSolutionsRequiresInput": True,
            "confirmCheckDialog": False,
            "confirmRetryDialog": False,
            "autoCheck": False
        },
        "UI": {
            "checkAnswerButton": "Überprüfen",
            "showSolutionButton": "Lösung anzeigen",
            "tryAgainButton": "Wiederholen",
            "scoreBarLabel": "Du hast :num von :total Punkten erreicht",
        }
    }

def generate_blanks(text_with_blanks: str, feedback_correct: str = "Richtig!", feedback_wrong: str = "Leider falsch.") -> dict:
    """
    Generate H5P.Blanks content.json.
    text_with_blanks uses *answer* syntax: "Die Hauptstadt von Deutschland ist *Berlin*."
    """
    return {
        "text": f"<p>{text_with_blanks}</p>",
        "overallFeedback": [
            {
                "from": 0,
                "to": 99,
                "feedback": feedback_wrong
            },
            {
                "from": 100,
                "to": 100,
                "feedback": feedback_correct
            }
        ],
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
            "showSolutionsRequiresInput": True,
            "caseSensitive": False,
            "autoCheck": False
        },
        "checkAnswerButton": "Überprüfen",
        "tryAgainButton": "Wiederholen",
        "showSolutionButton": "Lösung anzeigen",
        "inputLabel": "Leeres Feld @num von @total"
    }

def generate_truefalse(question: str, correct: bool, feedback_correct: str = "Richtig!", feedback_wrong: str = "Leider falsch.") -> dict:
    """Generate H5P.TrueFalse content.json."""
    return {
        "question": f"<p>{question}</p>",
        "correct": "true" if correct else "false",
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
        },
        "l10n": {
            "trueText": "Wahr",
            "falseText": "Falsch",
            "checkAnswer": "Überprüfen",
            "showSolutionButton": "Lösung anzeigen",
            "tryAgain": "Wiederholen",
            "wrongAnswerMessage": feedback_wrong,
            "correctAnswerMessage": feedback_correct,
            "scoreBarLabel": "Du hast :num von :total Punkten"
        }
    }

def generate_drag_text(text_with_draggables: str) -> dict:
    """
    Generate H5P.DragText content.json.
    text_with_draggables uses *draggable* syntax: "Berlin ist die Hauptstadt von *Deutschland*."
    """
    return {
        "textField": f"<p>{text_with_draggables}</p>",
        "overallFeedback": [
            {"from": 0, "to": 100, "feedback": ""}
        ],
        "checkAnswer": "Überprüfen",
        "tryAgain": "Wiederholen",
        "showSolution": "Lösung anzeigen",
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
            "instantFeedback": False
        }
    }

def exercise_set_to_h5p(exercise_set) -> list[tuple[dict, str, str]]:
    """Convert an ExerciseSet from the H5P agent into H5P exercises.

    Returns list of (h5p_content_dict, h5p_type_string, title_string).
    Each question becomes a separate exercise."""
    etype = exercise_set.exercise_type
    results = []

    if etype == "multichoice" and exercise_set.questions:
        for i, q in enumerate(exercise_set.questions):
            answers = [{"text": a.text, "correct": a.correct, "feedback": a.feedback} for a in q.answers]
            content = generate_multichoice(q.question, answers)
            title = f"{exercise_set.title} - Frage {i+1}" if len(exercise_set.questions) > 1 else exercise_set.title
            results.append((content, "H5P.MultiChoice", title))
    elif etype == "blanks" and exercise_set.text_with_gaps:
        content = generate_blanks(exercise_set.text_with_gaps)
        results.append((content, "H5P.Blanks", exercise_set.title))
    elif etype == "truefalse" and exercise_set.questions:
        for i, q in enumerate(exercise_set.questions):
            content = generate_truefalse(q.question, q.correct or False)
            title = f"{exercise_set.title} - Frage {i+1}" if len(exercise_set.questions) > 1 else exercise_set.title
            results.append((content, "H5P.TrueFalse", title))
    elif etype == "dragtext" and exercise_set.text_with_gaps:
        content = generate_drag_text(exercise_set.text_with_gaps)
        results.append((content, "H5P.DragText", exercise_set.title))
    else:
        # Fallback to multichoice
        if exercise_set.questions:
            for i, q in enumerate(exercise_set.questions):
                answers = [{"text": a.text, "correct": a.correct, "feedback": a.feedback} for a in q.answers]
                content = generate_multichoice(q.question, answers)
                title = f"{exercise_set.title} - Frage {i+1}" if len(exercise_set.questions) > 1 else exercise_set.title
                results.append((content, "H5P.MultiChoice", title))
        if not results:
            raise ValueError(f"Cannot convert exercise_type '{etype}' with given data")

    return results
