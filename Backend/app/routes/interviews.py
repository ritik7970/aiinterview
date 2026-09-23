import os

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlalchemy.orm import Session

import pymupdf
#from ..database import Base
from ..database import get_db
from ..models import (
    Interview,
    InterviewQuestion,
    InterviewEvaluation,
    User
)

from ..services.ai_service import (
    generate_first_question,
    evaluate_answer,
    generate_next_question,
    generate_final_evaluation
)

from .users import get_current_user


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


UPLOAD_DIR = "uploads/resumes"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


def extract_pdf_text(file_path: str) -> str:

    text = ""

    document = pymupdf.open(file_path)

    for page in document:
        text += page.get_text()

    document.close()

    return text


@router.post("/")
async def create_interview(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume: UploadFile = File(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    if resume.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported currently"
        )

    filename = (
        f"{current_user.id}_"
        f"{datetime.utcnow().timestamp()}_"
        f"{resume.filename}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    contents = await resume.read()

    with open(file_path, "wb") as file:
        file.write(contents)

    resume_text = extract_pdf_text(
        file_path
    )

    interview = Interview(
        user_id=current_user.id,
        job_title=job_title,
        job_description=job_description,
        resume_filename=resume.filename,
        resume_text=resume_text,
        status="created"
    )

    db.add(interview)

    db.commit()

    db.refresh(interview)

    return {
        "message": "Interview created successfully",
        "interview_id": interview.id,
        "job_title": interview.job_title,
        "status": interview.status
    }


@router.post("/{interview_id}/start")
def start_interview(
    interview_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    existing_question = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.interview_id == interview_id
    ).first()

    if existing_question:

        return {
            "question_id": existing_question.id,
            "question": existing_question.question_text
        }

    ai_result = generate_first_question(
        interview.job_title,
        interview.job_description,
        interview.resume_text or ""
    )

    question_text = ai_result["question"]

    question = InterviewQuestion(
        interview_id=interview.id,
        question_number=1,
        question_text=question_text
    )

    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()

    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "question_id": question.id,
        "question": question.question_text
    }


@router.post("/{interview_id}/answer")
@router.post("/{interview_id}/answer")
def submit_answer(
    interview_id: int,
    question_id: int = Form(...),
    answer: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # 1. Find interview
    # -----------------------------------------

    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    # -----------------------------------------
    # 2. Find question
    # -----------------------------------------

    question = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.interview_id == interview_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    # -----------------------------------------
    # 3. Save candidate answer
    # -----------------------------------------

    question.answer_text = answer

    # -----------------------------------------
    # 4. Evaluate answer using AI
    # -----------------------------------------

    evaluation = evaluate_answer(
        interview.job_title,
        interview.job_description,
        question.question_text,
        answer
    )

    question.score = evaluation["score"]

    question.feedback = evaluation["feedback"]

    db.commit()

    # -----------------------------------------
    # 5. Count questions
    # -----------------------------------------

    question_count = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.interview_id == interview_id
    ).count()

    # =========================================
    # 6. FINAL QUESTION
    # =========================================

    if question_count >= 5:

        print(
            "========== FINAL EVALUATION STARTED =========="
        )

        print(
            "Interview ID:",
            interview_id
        )

        print(
            "Question count:",
            question_count
        )

        # -------------------------------------
        # Get all interview questions
        # -------------------------------------

        questions = db.query(
            InterviewQuestion
        ).filter(
            InterviewQuestion.interview_id == interview_id
        ).order_by(
            InterviewQuestion.question_number
        ).all()

        # -------------------------------------
        # Prepare complete interview data
        # -------------------------------------

        interview_data = []

        for q in questions:

            interview_data.append({
                "question": q.question_text,
                "answer": q.answer_text or "",
                "score": q.score or 0,
                "feedback": q.feedback or ""
            })

        # -------------------------------------
        # Generate final AI evaluation
        # -------------------------------------

        final_evaluation = generate_final_evaluation(

            interview.job_title,

            interview.job_description,

            interview.resume_text or "",

            interview_data
        )

        print(
            "========== AI FINAL EVALUATION =========="
        )

        print(final_evaluation)

        # -------------------------------------
        # Validate AI response
        # -------------------------------------

        required_fields = [
            "overall_score",
            "technical_score",
            "communication_score",
            "problem_solving_score",
            "relevance_score",
            "strengths",
            "weaknesses",
            "recommendations",
            "summary"
        ]

        for field in required_fields:

            if field not in final_evaluation:

                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"AI final evaluation "
                        f"missing field: {field}"
                    )
                )

        # -------------------------------------
        # Mark interview completed
        # -------------------------------------

        interview.status = "completed"

        interview.completed_at = datetime.utcnow()

        interview.overall_score = int(
            final_evaluation["overall_score"]
        )

        # -------------------------------------
        # Create InterviewEvaluation record
        # -------------------------------------

        evaluation_record = InterviewEvaluation(

            interview_id=interview.id,

            overall_score=int(
                final_evaluation["overall_score"]
            ),

            technical_score=int(
                final_evaluation["technical_score"]
            ),

            communication_score=int(
                final_evaluation["communication_score"]
            ),

            problem_solving_score=int(
                final_evaluation["problem_solving_score"]
            ),

            relevance_score=int(
                final_evaluation["relevance_score"]
            ),

            strengths="\n".join(
                final_evaluation["strengths"]
            ),

            weaknesses="\n".join(
                final_evaluation["weaknesses"]
            ),

            recommendations="\n".join(
                final_evaluation["recommendations"]
            ),

            summary=final_evaluation["summary"]
        )

        db.add(evaluation_record)

        # -------------------------------------
        # Save everything
        # -------------------------------------

        db.commit()

        db.refresh(evaluation_record)

        print(
            "========== FINAL EVALUATION SAVED =========="
        )

        print(
            "Evaluation ID:",
            evaluation_record.id
        )

        print(
            "Interview ID:",
            interview.id
        )

        # -------------------------------------
        # Return final evaluation to frontend
        # -------------------------------------

        return {
            "completed": True,

            "evaluation": {
                "overall_score":
                    final_evaluation["overall_score"],

                "technical_score":
                    final_evaluation["technical_score"],

                "communication_score":
                    final_evaluation[
                        "communication_score"
                    ],

                "problem_solving_score":
                    final_evaluation[
                        "problem_solving_score"
                    ],

                "relevance_score":
                    final_evaluation[
                        "relevance_score"
                    ],

                "strengths":
                    final_evaluation["strengths"],

                "weaknesses":
                    final_evaluation["weaknesses"],

                "recommendations":
                    final_evaluation[
                        "recommendations"
                    ],

                "summary":
                    final_evaluation["summary"]
            }
        }

    # =========================================
    # QUESTIONS 1–4
    # =========================================

    next_question_number = question_count + 1

    next_result = generate_next_question(

        interview.job_title,

        interview.job_description,

        interview.resume_text or "",

        question.question_text,

        answer,

        question.feedback or ""
    )

    next_question = InterviewQuestion(

        interview_id=interview.id,

        question_number=next_question_number,

        question_text=next_result["question"]
    )

    db.add(next_question)

    db.commit()

    db.refresh(next_question)

    return {

        "completed": False,

        "score": question.score,

        "feedback": question.feedback,

        "question_id": next_question.id,

        "question": next_question.question_text
    }
@router.get("/history")
def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(
        Interview.created_at.desc()
    ).all()

    result = []

    for interview in interviews:
        result.append({
            "id": interview.id,
            "job_title": interview.job_title,
            "resume_filename": interview.resume_filename,
            "status": interview.status,
            "overall_score": interview.overall_score,
            "created_at": interview.created_at,
            "started_at": interview.started_at,
            "completed_at": interview.completed_at
        })

    return result
@router.get("/{interview_id}/evaluation")
def get_evaluation(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    evaluation = db.query(InterviewEvaluation).filter(
        InterviewEvaluation.interview_id == interview_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not available"
        )

    return {
        "interview_id": interview.id,
        "job_title": interview.job_title,
        "overall_score": evaluation.overall_score,
        "technical_score": evaluation.technical_score,
        "communication_score": evaluation.communication_score,
        "problem_solving_score": evaluation.problem_solving_score,
        "relevance_score": evaluation.relevance_score,
        "strengths": evaluation.strengths.split("\n"),
        "weaknesses": evaluation.weaknesses.split("\n"),
        "recommendations": evaluation.recommendations.split("\n"),
        "summary": evaluation.summary
    }