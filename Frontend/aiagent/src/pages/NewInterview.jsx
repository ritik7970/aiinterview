import { useState } from "react";
import { useNavigate } from "react-router-dom";

function NewInterview() {
  const navigate = useNavigate();

  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    setError("");

    if (!resume) {
      setError("Please upload your resume.");
      return;
    }

    if (resume.type !== "application/pdf") {
      setError("Only PDF resumes are supported.");
      return;
    }

    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/login");
      return;
    }

    const formData = new FormData();

    formData.append("job_title", jobTitle);
    formData.append("job_description", jobDescription);
    formData.append("resume", resume);

    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/interviews/",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to create interview"
        );
      }

      console.log("Interview created:", data);

      // For now, go back to dashboard.
      // Later this will take us to the actual AI interview.
      navigate(`/interview/${data.interview_id}`);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="new-interview-page">

      <div className="interview-form-card">

        <h1>Start New Interview</h1>

        <p className="subtitle">
          Upload your resume and provide the job description
          to prepare your AI interview.
        </p>

        <form onSubmit={handleSubmit}>

          <label>Job Title</label>

          <input
            type="text"
            placeholder="e.g. Python Developer"
            value={jobTitle}
            onChange={(e) =>
              setJobTitle(e.target.value)
            }
            required
          />

          <label>Resume</label>

          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={(e) =>
              setResume(e.target.files[0])
            }
            required
          />

          {resume && (
            <p className="file-name">
              Selected: {resume.name}
            </p>
          )}

          <label>Job Description</label>

          <textarea
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) =>
              setJobDescription(e.target.value)
            }
            rows="10"
            required
          />

          {error && (
            <p className="error">
              {error}
            </p>
          )}

          <div className="form-buttons">

            <button
              type="button"
              className="cancel-button"
              onClick={() => navigate("/dashboard")}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Creating Interview..."
                : "Start Interview"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}

export default NewInterview;