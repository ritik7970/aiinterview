import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function Results() {
  const { interviewId } = useParams();
  const navigate = useNavigate();

  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadEvaluation();
  }, [interviewId]);

  async function loadEvaluation() {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/interviews/${interviewId}/evaluation`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load interview report"
        );
      }

      setEvaluation(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="results-page">
        <div className="results-container">
          <h2>Loading interview report...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-page">
        <div className="results-container">
          <h2>Unable to load report</h2>

          <p>{error}</p>

          <button
            className="dashboard-button"
            onClick={() => navigate("/history")}
          >
            Back to History
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page">
      <div className="results-container">

        <div className="results-header">
          <button
            className="back-button"
            onClick={() => navigate("/history")}
          >
            ← Back to History
          </button>

          <h1>Interview Report</h1>

          <p className="job-title">
            {evaluation.job_title}
          </p>
        </div>

        {/* Overall Score */}

        <div className="overall-score-card">

          <p>Overall Score</p>

          <div className="overall-score">
            {evaluation.overall_score}
          </div>

          <span>out of 100</span>

        </div>

        {/* Category Scores */}

        <div className="score-grid">

          <ScoreCard
            title="Technical Knowledge"
            score={evaluation.technical_score}
          />

          <ScoreCard
            title="Communication"
            score={evaluation.communication_score}
          />

          <ScoreCard
            title="Problem Solving"
            score={evaluation.problem_solving_score}
          />

          <ScoreCard
            title="Job Relevance"
            score={evaluation.relevance_score}
          />

        </div>

        {/* Summary */}

        <section className="result-section">

          <h2>📌 Overall Summary</h2>

          <p>
            {evaluation.summary}
          </p>

        </section>

        {/* Strengths */}

        <section className="result-section">

          <h2>💪 Strengths</h2>

          <ul>
            {evaluation.strengths.map(
              (item, index) => (
                <li key={index}>
                  {item}
                </li>
              )
            )}
          </ul>

        </section>

        {/* Weaknesses */}

        <section className="result-section">

          <h2>⚠️ Areas to Improve</h2>

          <ul>
            {evaluation.weaknesses.map(
              (item, index) => (
                <li key={index}>
                  {item}
                </li>
              )
            )}
          </ul>

        </section>

        {/* Recommendations */}

        <section className="result-section">

          <h2>🚀 Recommendations</h2>

          <ol>
            {evaluation.recommendations.map(
              (item, index) => (
                <li key={index}>
                  {item}
                </li>
              )
            )}
          </ol>

        </section>

        <button
          className="dashboard-button"
          onClick={() => navigate("/dashboard")}
        >
          Back to Dashboard
        </button>

      </div>
    </div>
  );
}


function ScoreCard({ title, score }) {
  return (
    <div className="score-card">

      <h3>{title}</h3>

      <div className="small-score">
        {score}/100
      </div>

    </div>
  );
}


export default Results;