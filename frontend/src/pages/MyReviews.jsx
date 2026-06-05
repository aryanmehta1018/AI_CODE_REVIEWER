import { useEffect, useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

function MyReviews() {

  const [reviews, setReviews] = useState([]);
  const [expandedReview, setExpandedReview] =
    useState(null);
  const [searchTerm, setSearchTerm] =
    useState("");
  const [sortOrder, setSortOrder] =
    useState("newest");
  
  useEffect(() => {

    async function fetchReviews() {

      try {

        const token =
          localStorage.getItem("token");

        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/my-reviews`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setReviews(response.data);

      } catch (err) {
        console.log(err);
      }
    }

    fetchReviews();

  }, []);

  function toggleReview(id) {

    if (expandedReview === id) {
      setExpandedReview(null);
    } else {
      setExpandedReview(id);
    }

  }

  async function deleteReview(reviewId) {

    try {

      const token =
        localStorage.getItem("token");

      await axios.delete(
        `${import.meta.env.VITE_API_URL}/review/${reviewId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setReviews(
        reviews.filter(
          (review) =>
            review.id !== reviewId
        )
      );

      toast.success(
        "Review deleted successfully"
      );

    } catch (err) {
      console.log(err);
      toast.error(
        "Failed to delete review"
      );
    }

  }

  const filteredReviews = [...reviews]
    .filter((review) => {

      const text = `
        ${review.code}
        ${review.review.bugs}
        ${review.review.improvements}
        ${review.review.notes}
      `.toLowerCase();

      return text.includes(
        searchTerm.toLowerCase()
      );
    })
    .sort((a, b) => {

      if (sortOrder === "newest") {
        return b.id - a.id;
      }

      return a.id - b.id;
    });

  const scores = reviews
    .map((review) => review.review.score)
    .filter((score) => score !== undefined);

  const averageScore =
    scores.length > 0
      ? Math.round(
          scores.reduce(
            (a, b) => a + b,
            0
          ) / scores.length
        )
      : 0;

  const highestScore =
    scores.length > 0
      ? Math.max(...scores)
      : 0;

  const lowestScore =
    scores.length > 0
      ? Math.min(...scores)
      : 0;

  return (
    <div className="reviews-page">

      <div className="navbar">
        <h1>My Reviews</h1>

        <Link to="/dashboard">
          Back to Dashboard
        </Link>
      </div>

      <div className="reviews-toolbar">

        <input
          type="text"
          placeholder="Search reviews..."
          value={searchTerm}
          onChange={(e) =>
            setSearchTerm(e.target.value)
          }
        />

        <select
          value={sortOrder}
          onChange={(e) =>
            setSortOrder(e.target.value)
          }
        >
          <option value="newest">
            Newest First
          </option>

          <option value="oldest">
            Oldest First
          </option>
        </select>

      </div>

      <div className="stats-row">

        <div className="stat-box">
          <h3>Total Reviews</h3>
          <span>{reviews.length}</span>
        </div>

        <div className="stat-box">
          <h3>Lines Reviewed</h3>
          <span>
            {
              reviews.reduce(
                (acc, review) =>
                  acc +
                  review.code.split("\n").length,
                0
              )
            }
          </span>
        </div>
        <div className="stat-box">
          <h3>Average Score</h3>
          <span>{averageScore}</span>
        </div>

        <div className="stat-box">
          <h3>Best Score</h3>
          <span>{highestScore}</span>
        </div>

        <div className="stat-box">
          <h3>Worst Score</h3>
          <span>{lowestScore}</span>
        </div>

      </div>
      
      {filteredReviews.map((item, index) => (

        <div
          key={item.id}
          className="review-card"
        >

          <div
            className="review-header"
            onClick={() =>
              toggleReview(item.id)
            }
          >

            <h2>
              {expandedReview === item.id
                ? "▼"
                : "▶"}{" "}
              Review • {
                item.code.split("\n").length
              } lines
            </h2>

          </div>

          {expandedReview === item.id && (

            <div className="review-content">
              <div className="review-actions">

                <button
                  className="delete-btn"
                  onClick={() => {

                    const confirmed =
                      window.confirm(
                        "Delete this review?"
                      );

                    if (confirmed) {
                      deleteReview(item.id);
                    }

                  }}
                >
                  Delete Review
                </button>

              </div>

              <h2>Your Code</h2>

              <Editor
                height="250px"
                defaultLanguage="python"
                theme="vs-dark"
                value={item.code}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14
                }}
              />

              <h2>Bugs</h2>
              <pre>{item.review.bugs}</pre>

              <h2>Improvements</h2>
              <pre>{item.review.improvements}</pre>

              <h2>Optimizations</h2>
              <pre>{item.review.optimizations}</pre>

              <h2>Improved Code</h2>

              <Editor
                height="300px"
                defaultLanguage="python"
                theme="vs-dark"
                value={item.review.improved_code}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14
                }}
              />

              <h2>Additional Notes</h2>
              <pre>{item.review.notes}</pre>

            </div>

          )}

        </div>

      ))}

    </div>
  );
}

export default MyReviews;