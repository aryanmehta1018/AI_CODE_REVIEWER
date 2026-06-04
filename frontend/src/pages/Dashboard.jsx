import { useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";
import { Link, useNavigate } from "react-router-dom";
import { useRef } from "react";
import toast from "react-hot-toast";
import { FaSpinner } from "react-icons/fa";

function Dashboard() {
  const navigate = useNavigate();
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] =
    useState("python");
  const [review, setReview] = useState(null);
  const [syntaxErrors, setSyntaxErrors] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  async function handleReview() {
    try {
      setLoading(true);

      const token =
        localStorage.getItem("token");

      const response = await axios.post(
        "http://127.0.0.1:8000/review",
        {
          code,
          language,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setReview(response.data.review);
      setSyntaxErrors(
        response.data.syntax_errors || []
      );
      showSyntaxMarkers(
        response.data.syntax_errors || []
      );
    } catch (err) {
      console.log(err);

      toast.error(
        "Review failed. AI service may be busy."
      );
    } finally {
      setLoading(false);
    }
  }

  async function copyCode() {
    await navigator.clipboard.writeText(
      review.improved_code
    );

    toast.success("Code copied!");
  }

  function handleLogout() {
    localStorage.removeItem("token");

    navigate("/");
  }

  function downloadReview() {
    const content = `
  BUGS
  ${review.bugs}

  IMPROVEMENTS
  ${review.improvements}

  OPTIMIZATIONS
  ${review.optimizations}

  NOTES
  ${review.notes}
  `;

    const blob = new Blob(
      [content],
      { type: "text/plain" }
    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;
    a.download = "review.txt";
    a.click();
  }

  function showSyntaxMarkers(errors) {

    if (
      !editorRef.current ||
      !monacoRef.current
    ) {
      return;
    }

    const model =
      editorRef.current.getModel();

    const markers = errors.map(
      (error) => ({
        startLineNumber: error.line,
        endLineNumber: error.line,
        startColumn: 1,
        endColumn: 999,

        message: error.message,

        severity:
          monacoRef.current.MarkerSeverity
            .Error,
      })
    );

    monacoRef.current.editor.setModelMarkers(
      model,
      "syntax",
      markers
    );
  }

  return (
    <div className="dashboard-page">
      {/* Navbar */}

      <div className="navbar">
        <h1>AI Code Reviewer</h1>

        <div className="nav-links">
          <Link to="/my-reviews">
            My Reviews
          </Link>

          <button
            className="logout-btn"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Hero */}

      <div className="hero-section">
        <h2>
          Paste your code.
          <br />
          Let AI review it instantly.
        </h2>

        <p>
          Detect bugs, improve
          readability, and optimize
          performance with AI-powered
          reviews.
        </p>
      </div>

      <div className="language-selector">

        <span className="language-title">
          Select Language
        </span>

        <select
          value={language}
          onChange={(e) =>
            setLanguage(e.target.value)
          }
        >

          <option value="python">
            Python
          </option>

          <option value="javascript">
            JavaScript
          </option>

          <option value="java">
            Java
          </option>

          <option value="cpp">
            C++
          </option>

        </select>

      </div>

      {/* Editor */}

      <div className="editor-container">
        <Editor
          height="500px"
          language={language}
          theme="vs-dark"
          value={code}
          onChange={(value) => {

            setCode(value);

            if (
              editorRef.current &&
              monacoRef.current
            ) {

              monacoRef.current.editor
                .setModelMarkers(
                  editorRef.current.getModel(),
                  "syntax",
                  []
                );
            }
          }}
          onMount={(editor, monaco) => {
            editorRef.current = editor;
            monacoRef.current = monaco;
          }}
        />
      </div>

      {syntaxErrors.length > 0 && (
        <div className="syntax-errors">

          <h3>Syntax Errors</h3>

          {syntaxErrors.map((error, index) => (
            <p key={index}>
              Line {error.line}: {error.message}
            </p>
          ))}

        </div>
      )}

      {/* Button */}

      <div className="review-btn-container">
        <button
          className="review-btn"
          onClick={handleReview}
        >
          {loading ? (
            <>
              <FaSpinner className="spin" />
              Reviewing...
            </>
          ) : (
            "Review Code"
          )}
        </button>
      </div>

      {/* Review Output */}
      

      {review && (
        <div className="review-output">
          <div className="score-card">
            <h3>Code Quality Score</h3>

            <div className="score-number">
              {review.score}/100
            </div>
          </div>

            <div className="review-card-glass">
              <h2>Bugs</h2>
              <pre>{review.bugs}</pre>
            </div>

            <div className="review-card-glass">
              <h2>Improvements</h2>
              <pre>{review.improvements}</pre>
            </div>

            <div className="review-card-glass">
              <h2>Optimizations</h2>
              <pre>{review.optimizations}</pre>
            </div>

            <div className="compare-section">

              <div>
                <h2>Original Code</h2>
                <div className="editor-align-spacer"></div>
                <Editor
                  height="400px"
                  theme="vs-dark"
                  defaultLanguage="python"
                  value={code}
                  options={{
                    readOnly: true,
                    minimap: { enabled: false }
                  }}
                />
              </div>

              <div>
                <h2>Improved Code</h2>
                <div className="action-buttons">

                  <button
                    className="copy-btn"
                    onClick={copyCode}
                  >
                    📋 Copy Code
                  </button>

                  <button
                    className="download-btn"
                    onClick={downloadReview}
                  >
                    📄 Download Review
                  </button>

                </div>

                <Editor
                  height="400px"
                  theme="vs-dark"
                  defaultLanguage="python"
                  value={review.improved_code}
                  options={{
                    readOnly: true,
                    minimap: { enabled: false }
                  }}
                />
              </div>

            </div>

            

            <div className="review-card-glass">
              <h2>Additional Notes</h2>
              <pre>{review.notes}</pre>
            </div>

        </div>
    )}
    </div>
  );
}

export default Dashboard;