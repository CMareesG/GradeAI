import React from "react";
import "./ResultPage.css";

function ResultPage({ result, setPage }) {

  return (
    <div className="result-page">

      <div className="result-container">

        {/* HEADER */}
        <div className="result-header">

          <div className="header-left">
            <button
              className="back-btn"
              onClick={() => setPage("subjects")}
            >
              ← Back
            </button>
          </div>

          <div className="header-center">
            <h1 className="result-title">Evaluation Result</h1>
          </div>

          <div className="header-spacer"></div>

        </div>

        {/* SUMMARY */}
        <div className="summary-grid">

          <div className="summary-card">
            <h2>{result.total_score}</h2>
            <p>Total Score</p>
          </div>

          <div className="summary-card">
            <h2>{result.percentage}%</h2>
            <p>Percentage</p>
          </div>

          <div className="summary-card">
            <h2>{result.grade}</h2>
            <p>Grade</p>
          </div>

        </div>

        {/* DETAILS */}
        <div className="details">

          {result.results.map((r, i) => (
            <div key={i} className="result-row">

              <div className="left">
                <h3>{r.question_id}</h3>
                <p className="score">
                  {r.score} / {r.max_score}
                </p>
              </div>

              <div className="right">
                <p className="feedback">{r.feedback}</p>

                {r.missing_keywords?.length > 0 && (
                  <p className="missing">
                    Missing: {r.missing_keywords.join(", ")}
                  </p>
                )}
              </div>

            </div>
          ))}

        </div>

      </div>

    </div>
  );
}

export default ResultPage;