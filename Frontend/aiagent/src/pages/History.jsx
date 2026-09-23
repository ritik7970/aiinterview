import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function History() {
  const navigate = useNavigate();

  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/interviews/history",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load interview history"
        );
      }

      setInterviews(data);

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }

  function openInterview(id, status) {
    if (status === "completed") {
      navigate(`/results/${id}`);
    } else {
      navigate(`/interview/${id}`);
    }
  }

  if (loading) {
    return (
      <div className="history-page">
        <h2>Loading interview history...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-page">
        <h2>{error}</h2>

        <button onClick={() => navigate("/dashboard")}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="history-page">

      <div className="history-container">

        <div className="history-header">

          <div>
            <h1>Interview History</h1>

            <p>
              View your previous interview attempts and results.
            </p>
          </div>

          <button
            onClick={() => navigate("/dashboard")}
          >
            Dashboard
          </button>

        </div>

        {interviews.length === 0 ? (

          <div className="empty-history">

            <h2>No interviews yet</h2>

            <p>
              Start your first AI-powered interview.
            </p>

            <button
              onClick={() => navigate("/interview")}
            >
              Start New Interview
            </button>

          </div>

        ) : (

          <div className="history-list">

            {interviews.map((interview) => (

              <div
                className="history-card"
                key={interview.id}
              >

                <div className="history-card-main">

                  <h2>
                    {interview.job_title}
                  </h2>

                  <p>
                    Resume: {interview.resume_filename}
                  </p>

                  <p>
                    Created:{" "}
                    {new Date(
                      interview.created_at
                    ).toLocaleString()}
                  </p>

                </div>

                <div className="history-card-right">

                  <span
                    className={`status ${interview.status}`}
                  >
                    {interview.status}
                  </span>

                  {interview.overall_score !== null && (

                    <div className="history-score">

                      {interview.overall_score}/100

                    </div>

                  )}

                  <button
                    onClick={() =>
                      openInterview(
                        interview.id,
                        interview.status
                      )
                    }
                  >
                    {interview.status === "completed"
                      ? "View Report"
                      : "Continue"}
                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </div>
  );
}

export default History;