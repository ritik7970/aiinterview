import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function Interview() {

  const { interviewId } = useParams();

  const navigate = useNavigate();

  const [question, setQuestion] = useState("");

  const [questionId, setQuestionId] = useState(null);

  const [answer, setAnswer] = useState("");

  const [feedback, setFeedback] = useState("");

  const [score, setScore] = useState(null);

  const [loading, setLoading] = useState(true);

  const [submitting, setSubmitting] = useState(false);

  const [completed, setCompleted] = useState(false);

  const [finalScore, setFinalScore] = useState(null);


  useEffect(() => {

    startInterview();

  }, []);


  async function startInterview() {

    const token = localStorage.getItem("token");

    if (!token) {

      navigate("/login");

      return;

    }

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/interviews/${interviewId}/start`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail || "Unable to start interview"
        );

      }

      setQuestion(data.question);

      setQuestionId(data.question_id);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  }


  async function submitAnswer(e) {

    e.preventDefault();

    if (!answer.trim()) {

      return;

    }

    const token = localStorage.getItem("token");

    setSubmitting(true);

    setFeedback("");

    try {

      const formData = new FormData();

      formData.append(
        "question_id",
        questionId
      );

      formData.append(
        "answer",
        answer
      );

      const response = await fetch(
        `http://127.0.0.1:8000/interviews/${interviewId}/answer`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${token}`
          },

          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail || "Failed to submit answer"
        );

      }

      setScore(data.score);

      setFeedback(data.feedback);

      setAnswer("");

      if (data.completed) {

        setCompleted(true);

        setFinalScore(data.score);

      } else {

        setQuestion(data.question);

        setQuestionId(data.question_id);

      }

    } catch (error) {

      console.error(error);

      setFeedback(error.message);

    } finally {

      setSubmitting(false);

    }
  }


  if (loading) {

    return (
      <div className="interview-page">

        <h2>
          Preparing your interview...
        </h2>

      </div>
    );

  }


  if (completed) {

    return (
      <div className="interview-page">

        <div className="interview-card">

          <h1>
            🎉 Interview Completed
          </h1>

          <h2>
            Your Score
          </h2>

          <div className="final-score">
            {finalScore}/100
          </div>

          <p>
            Your detailed evaluation will be available
            in the interview history.
          </p>

          <button
            onClick={() =>
              navigate("/dashboard")
            }
          >
            Back to Dashboard
          </button>

        </div>

      </div>
    );

  }


  return (
    <div className="interview-page">

      <div className="interview-card">

        <div className="interview-header">

          <h1>
            AI Interview
          </h1>

          <span>
            Question
          </span>

        </div>


        <div className="question-box">

          <h2>
            {question}
          </h2>

        </div>


        {feedback && (

          <div className="feedback-box">

            <h3>
              Previous Answer Evaluation
            </h3>

            <p>
              Score: {score}/100
            </p>

            <p>
              {feedback}
            </p>

          </div>

        )}


        <form onSubmit={submitAnswer}>

          <label>
            Your Answer
          </label>

          <textarea
            value={answer}
            onChange={(e) =>
              setAnswer(e.target.value)
            }
            placeholder="Type your answer here..."
            rows="8"
            disabled={submitting}
          />

          <button
            type="submit"
            disabled={submitting}
          >

            {submitting
              ? "Evaluating..."
              : "Submit Answer"}

          </button>

        </form>

      </div>

    </div>
  );
}

export default Interview;