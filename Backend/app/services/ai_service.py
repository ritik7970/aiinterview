import os
import json

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_first_question(
    job_title: str,
    job_description: str,
    resume_text: str
):

    prompt = f"""
You are an experienced technical interviewer.

You are interviewing a candidate for this role:

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Generate the first interview question.

The question should:
- Be relevant to the job
- Be relevant to the candidate's resume
- Not be unnecessarily difficult
- Encourage the candidate to explain their experience

Return ONLY JSON:

{{
    "question": "your question here"
}}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    text = response.output_text

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        return {
            "question": text
        }


def evaluate_answer(
    job_title: str,
    job_description: str,
    question: str,
    answer: str
):

    prompt = f"""
You are evaluating a candidate during a job interview.

JOB:
{job_title}

JOB DESCRIPTION:
{job_description}

INTERVIEW QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Evaluate the answer.

Give a score from 0 to 100.

Consider:
- Technical correctness
- Relevance
- Depth
- Clarity
- Understanding

Return ONLY JSON:

{{
    "score": 0,
    "feedback": "brief constructive feedback"
}}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    text = response.output_text

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        return {
            "score": 0,
            "feedback": text
        }


def generate_next_question(
    job_title: str,
    job_description: str,
    resume_text: str,
    previous_question: str,
    previous_answer: str,
    previous_feedback: str
):
    prompt = f"""
You are an experienced human technical interviewer.

You are interviewing a candidate for this position:

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

The previous interview question was:

{previous_question}

The candidate's answer was:

{previous_answer}

Your evaluation of the answer was:

{previous_feedback}

Now generate the next interview question.

Rules:

1. Ask exactly ONE question.
2. Do not repeat the previous question.
3. Do not ask the exact same concept again.
4. If the candidate made an interesting technical claim,
   ask a natural follow-up question about it.
5. If the answer was incomplete or weak, ask a clarification
   or simpler follow-up question.
6. Gradually increase the difficulty.
7. Cover different areas of the job description.
8. Use the candidate's resume when relevant.
9. The question should sound like a real human interviewer.
10. Do not provide the answer.
11. Do not provide explanations outside the JSON.

Return ONLY valid JSON in exactly this format:

{{
    "question": "your next interview question",
    "question_type": "technical"
}}

question_type must be one of:

follow_up
technical
project
behavioral
problem_solving
resume
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    text = response.output_text.strip()

    try:
        result = json.loads(text)

        if not isinstance(result, dict):
            raise ValueError("AI response is not a JSON object")

        question = result.get("question")

        if not question:
            raise ValueError(
                "AI response does not contain a question"
            )

        return {
            "question": question,
            "question_type": result.get(
                "question_type",
                "technical"
            )
        }

    except json.JSONDecodeError as error:
        print("AI returned invalid JSON:")
        print(text)

        # Fallback question so the interview does not crash
        return {
            "question": (
                "Can you explain your approach in more detail "
                "and describe why you chose that approach?"
            ),
            "question_type": "follow_up"
        }

    except Exception as error:
        print("Error processing next question:", error)

        return {
            "question": (
                "Can you explain your previous answer in "
                "more technical detail?"
            ),
            "question_type": "follow_up"
        }
def generate_final_evaluation(
    job_title: str,
    job_description: str,
    resume_text: str,
    interview_data: list
):

    conversation = ""

    for item in interview_data:

        conversation += f"""
QUESTION:
{item["question"]}

ANSWER:
{item["answer"]}

QUESTION SCORE:
{item["score"]}

QUESTION FEEDBACK:
{item["feedback"]}

-------------------------
"""

    prompt = f"""
You are a senior technical interviewer.

You have completed an interview for:

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

FULL INTERVIEW:

{conversation}

Analyze the candidate's complete performance.

Evaluate:

1. Technical knowledge
2. Communication
3. Problem solving
4. Relevance to the job
5. Overall performance

Scores must be integers from 0 to 100.

The overall score should represent the candidate's
overall interview performance.

Provide:

- Overall score
- Technical score
- Communication score
- Problem solving score
- Relevance score
- Strengths
- Weaknesses
- Specific recommendations
- A short overall summary

Return ONLY valid JSON.

Format:

{{
    "overall_score": 0,
    "technical_score": 0,
    "communication_score": 0,
    "problem_solving_score": 0,
    "relevance_score": 0,
    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2",
        "weakness 3"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2",
        "recommendation 3"
    ],
    "summary": "overall performance summary"
}}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    text = response.output_text

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        raise ValueError(
            "AI returned invalid evaluation JSON"
        )