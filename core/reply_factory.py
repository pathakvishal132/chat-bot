from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def calculate_score(session):
    score = 0
    question_count = len(PYTHON_QUESTION_LIST)
    s = 0
    wrong_typed_ans = []

    for question_id in range(question_count):
        correct_answer = PYTHON_QUESTION_LIST[question_id]["answer"]
        user_answer_key = f"answer_{question_id}"
        if user_answer_key in session:
            user_answer = session[user_answer_key]
            if user_answer == correct_answer:
                score += 1
            elif user_answer not in PYTHON_QUESTION_LIST[question_id]["options"]:
                question_data = PYTHON_QUESTION_LIST[question_id]
                options = "\n".join(
                    [
                        f"{idx + 1}. {option}"
                        for idx, option in enumerate(question_data["options"])
                    ]
                )
                s += 1
                wrong_typed_ans.append(
                    f"'(Q{s})':{PYTHON_QUESTION_LIST[question_id]['question_text']}."
                    f"Please choose between these options : {options}\n"
                )

    return score, "".join(wrong_typed_ans)


def generate_bot_responses(message, session):
    bot_responses = []
    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        next_question, next_question_id = get_next_question(-1)
        bot_responses.append(next_question)
        session["current_question_id"] = next_question_id
        session.save()
        return bot_responses

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    if answer.strip() == "":
        return False, "Answer cannot be empty."
    session[f"answer_{current_question_id}"] = answer
    session.save()
    return True, ""


def get_next_question(current_question_id):
    next_question_id = current_question_id + 1 if current_question_id is not None else 0
    if next_question_id < len(PYTHON_QUESTION_LIST):
        question_data = PYTHON_QUESTION_LIST[next_question_id]
        question_text = question_data["question_text"]
        options = "\n".join(
            [
                f"{idx + 1}. {option}"
                for idx, option in enumerate(question_data["options"])
            ]
        )
        formatted_question = f"{question_text}\nOptions:\n{options}"
        return formatted_question, next_question_id
    else:
        return None, -1


def generate_final_response(session):
    score, msg = calculate_score(session)
    question_count = len(PYTHON_QUESTION_LIST)
    if score == len(PYTHON_QUESTION_LIST):
        return f"You scored {score} . \n out of {question_count}. \n Congrats you scored full marks now you can exit from browser"
    if msg != "":
        return f"You scored : {score} . \n out of : {question_count}. \n You typed a wrong answer for these questions : {msg}"
    return f"You scored {score} . \n out of {question_count}. \n {msg}"
