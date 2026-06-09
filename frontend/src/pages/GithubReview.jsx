import { useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";

function GithubReview() {

  const [repoUrl, setRepoUrl] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [result, setResult] =
    useState(null);

  async function analyzeRepo() {

    try {

      setLoading(true);

      const token =
        localStorage.getItem("token");

      const response =
        await axios.post(
          `${import.meta.env.VITE_API_URL}/github-review`,
          {
            repo_url: repoUrl
          },
          {
            headers: {
              Authorization:
                `Bearer ${token}`
            }
          }
        );

      setResult(response.data);

    } catch (err) {

      console.log(err);

      toast.error(
        "Repository analysis failed"
      );

    } finally {

      setLoading(false);

    }

  }

  return (

    <div className="github-page">

      <div className="navbar">

        <h1>
          GitHub Repository Analyzer
        </h1>

        <Link to="/dashboard">
          Back to Dashboard
        </Link>

      </div>

      <div className="hero-section">

        <h2>
          Analyze an entire GitHub repository
        </h2>

        <p>
          Paste a public GitHub repository URL
          and let AI review the codebase.
        </p>

      </div>

      <div className="github-review-box">

        <input
          type="text"
          placeholder="https://github.com/user/repository"
          value={repoUrl}
          onChange={(e) =>
            setRepoUrl(e.target.value)
          }
        />

        <button
          onClick={analyzeRepo}
        >
          {
            loading
              ? "Analyzing..."
              : "Analyze Repository"
          }
        </button>

      </div>

      {
        result && (

          <div className="review-output">

            <h2>
              Analysis Result
            </h2>

            <pre>
              {
                JSON.stringify(
                  result,
                  null,
                  2
                )
              }
            </pre>

          </div>

        )
      }

    </div>

  );

}

export default GithubReview;