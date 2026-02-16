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

def generate_question_set(questions: list[tuple[dict, str]]) -> dict:
    """Bundle multiple H5P questions into a QuestionSet.
    questions = list of (content_dict, library_string) tuples.
    """
    question_list = []
    for content, library in questions:
        question_list.append({
            "params": content,
            "library": library,
            "subContentId": str(uuid.uuid4()),
            "metadata": {"contentType": library.split(" ")[0]}
        })

    return {
        "introPage": {
            "showIntroPage": False,
            "title": "",
            "introduction": ""
        },
        "progressType": "dots",
        "passPercentage": 50,
        "questions": question_list,
        "texts": {
            "prevButton": "Zurück",
            "nextButton": "Weiter",
            "finishButton": "Fertig",
            "submitButton": "Absenden",
            "textualProgress": "Frage @current von @total",
            "jumpToQuestion": "Frage %d von %total",
            "questionLabel": "Frage",
            "readSpeakerProgress": "Frage @current von @total",
            "unansweredText": "Nicht beantwortet",
            "answeredText": "Beantwortet",
            "currentQuestionText": "Aktuelle Frage",
            "navigationLabel": "Fragen"
        },
        "override": {
            "checkButton": True,
            "showSolutionButton": "on",
            "retryButton": "on"
        },
        "disableBackwardsNavigation": False
    }


def exercise_set_to_h5p(exercise_set) -> list[tuple[dict, str, str]]:
    """Convert an ExerciseSet into H5P exercises.
    Returns list of (h5p_content_dict, h5p_type_string, title_string).
    Multiple questions are bundled into ONE QuestionSet."""
    etype = exercise_set.exercise_type

    if etype == "multichoice" and exercise_set.questions:
        if len(exercise_set.questions) == 1:
            q = exercise_set.questions[0]
            answers = [{"text": a.text, "correct": a.correct, "feedback": a.feedback} for a in q.answers]
            content = generate_multichoice(q.question, answers)
            return [(content, "H5P.MultiChoice", exercise_set.title)]
        else:
            mc_questions = []
            for q in exercise_set.questions:
                answers = [{"text": a.text, "correct": a.correct, "feedback": a.feedback} for a in q.answers]
                mc_content = generate_multichoice(q.question, answers)
                mc_questions.append((mc_content, "H5P.MultiChoice 1.16"))
            content = generate_question_set(mc_questions)
            return [(content, "H5P.QuestionSet", exercise_set.title)]

    elif etype == "blanks" and exercise_set.text_with_gaps:
        content = generate_blanks(exercise_set.text_with_gaps)
        return [(content, "H5P.Blanks", exercise_set.title)]

    elif etype == "truefalse" and exercise_set.questions:
        if len(exercise_set.questions) == 1:
            q = exercise_set.questions[0]
            content = generate_truefalse(q.question, q.correct or False)
            return [(content, "H5P.TrueFalse", exercise_set.title)]
        else:
            tf_questions = []
            for q in exercise_set.questions:
                tf_content = generate_truefalse(q.question, q.correct or False)
                tf_questions.append((tf_content, "H5P.TrueFalse 1.8"))
            content = generate_question_set(tf_questions)
            return [(content, "H5P.QuestionSet", exercise_set.title)]

    elif etype == "dragtext" and exercise_set.text_with_gaps:
        content = generate_drag_text(exercise_set.text_with_gaps)
        return [(content, "H5P.DragText", exercise_set.title)]

    else:
        if exercise_set.questions:
            mc_questions = []
            for q in exercise_set.questions:
                answers = [{"text": a.text, "correct": a.correct, "feedback": a.feedback} for a in q.answers]
                mc_content = generate_multichoice(q.question, answers)
                mc_questions.append((mc_content, "H5P.MultiChoice 1.16"))
            if len(mc_questions) == 1:
                return [(mc_questions[0][0], "H5P.MultiChoice", exercise_set.title)]
            content = generate_question_set(mc_questions)
            return [(content, "H5P.QuestionSet", exercise_set.title)]
        raise ValueError(f"Cannot convert exercise_type '{etype}' with given data")


def youtube_quiz_to_h5p(quiz_structure) -> list[dict]:
    """Convert a YouTubeQuizStructure to a list of H5P content items.
    
    Returns list of (h5p_type, content_json) tuples ready for exercise creation.
    """
    h5p_items = []

    for frage in quiz_structure.fragen:
        if frage.typ == "multiple_choice" and frage.optionen:
            answers = []
            for opt in frage.optionen:
                answers.append({
                    "text": opt,
                    "correct": opt.strip().lower() == frage.richtige_antwort.strip().lower(),
                    "feedback": frage.erklaerung if opt.strip().lower() == frage.richtige_antwort.strip().lower() else "",
                })
            # Ensure at least one correct answer
            if not any(a["correct"] for a in answers):
                answers[0]["correct"] = True
            content = generate_multichoice(frage.frage, answers)
            h5p_items.append(("H5P.MultiChoice", content))

        elif frage.typ == "true_false":
            correct = frage.richtige_antwort.strip().lower() in ("wahr", "richtig", "true", "ja")
            answers = [
                {"text": "Wahr", "correct": correct, "feedback": frage.erklaerung if correct else ""},
                {"text": "Falsch", "correct": not correct, "feedback": frage.erklaerung if not correct else ""},
            ]
            content = generate_multichoice(frage.frage, answers)
            h5p_items.append(("H5P.MultiChoice", content))

        elif frage.typ == "lueckentext":
            # Convert to blanks format: "Das Ergebnis ist *Antwort*."
            text = frage.frage.replace("___", f"*{frage.richtige_antwort}*")
            if "*" not in text:
                text += f" *{frage.richtige_antwort}*"
            content = generate_blanks(text)
            h5p_items.append(("H5P.Blanks", content))

    return h5p_items
