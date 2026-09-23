import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser } from "../services/api";

function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/login");
      return;
    }

    getCurrentUser(token)
      .then((data) => {
        setUser(data);
      })
      .catch(() => {
        localStorage.removeItem("token");
        navigate("/login");
      });
  }, [navigate]);

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div className="dashboard">

      <nav className="navbar">

        <h2>AI Interviewer</h2>

        <button onClick={handleLogout}>
          Logout
        </button>

      </nav>

      <main className="dashboard-content">

        <h1>
          Welcome, {user.name}! 👋
        </h1>

        <p>
          Prepare for your next interview with AI.
        </p>

        <div className="dashboard-cards">

          <div
            className="dashboard-card"
            onClick={() => navigate("/interview")}
          >
            <h2>🎤</h2>
            <h2>New Interview</h2>

            <p>
              Start a new AI-powered mock interview.
            </p>

            <button>
              Start Interview
            </button>
          </div>

          <div
            className="dashboard-card"
            onClick={() => navigate("/history")}
          >
            <h2>📊</h2>
            <h2>Interview History</h2>

            <p>
              View your previous interviews and results.
            </p>

            <button>
              View History
            </button>
          </div>

        </div>

      </main>

    </div>
  );
}

export default Dashboard;