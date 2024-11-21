from api.models import Answer, Result, Choice, Participant, Exam


def calculate_exam_result(participant_id: int, exam_id: int):
    """
    Calculate the result of an exam for a specific participant.
    """
    try:
        participant = Participant.objects.get(id=participant_id)
        exam = Exam.objects.get(id=exam_id)

        questions = exam.questions.all()
        answers = Answer.objects.filter(
            participant=participant, question__in=questions)

        score = 0
        max_score = len(questions)

        # Avaliar cada resposta
        for answer in answers:
            if answer.choice.is_correct:
                score += 1

        # Salvar o resultado
        result, created = Result.objects.update_or_create(
            participant=participant,
            exam=exam,
            defaults={"score": score, "max_score": max_score},
        )

        return {
            "participant": participant.user.username,
            "exam": exam.name,
            "score": score,
            "max_score": max_score,
        }

    except Participant.DoesNotExist:
        raise ValueError("Participant not found.")
    except Exam.DoesNotExist:
        raise ValueError("Exam not found.")
    except Exception as e:
        raise RuntimeError(f"Error while calculating results: {e}")
