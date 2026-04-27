import React, { useEffect, useState } from "react";
import { evaluateAnswerSheet } from "../api/api";
import "./EvaluationPage.css"; // ✅ IMPORT CSS

function EvaluationPage({ subject, setPage, setResult }) {

  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`http://localhost:8000/tests/${subject}`)
      .then(res => res.json())
      .then(data => {
        setTests(data);
        setSelectedTest(data[0]);
      });
  }, [subject]);

  const handleUpload = async () => {

    if (!file) return alert("Please upload a file");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("subject", subject);
    formData.append("test", selectedTest);

    setLoading(true);

    try {
      const res = await evaluateAnswerSheet(formData);
      setResult(res.data);
      setPage("result");
    } catch (err) {
      alert("Error processing file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">

      <div className="wrapper">

        {/* HEADER */}
        <div className="header">
          <h2>{subject.toUpperCase()}</h2>
          <p>Select test and upload answer sheet</p>
        </div>

        {/* CARD */}
        <div className="card">

          {/* TEST SELECT */}
          <div className="field">
            <label>Test</label>
            <select
              value={selectedTest}
              onChange={(e) => setSelectedTest(e.target.value)}
              className="select"
            >
              {tests.map((t, i) => {
                const cleanName = t.replace(".json", "").toUpperCase();
                return <option key={i} value={t}>{cleanName}</option>;
              })}
            </select>
          </div>

          {/* UPLOAD BOX */}
          <div
            className="uploadBox"
            onClick={() => document.getElementById("fileInput").click()}
          >
            <input
              id="fileInput"
              type="file"
              style={{ display: "none" }}
              onChange={(e) => setFile(e.target.files[0])}
            />

            {file ? (
              <>
                <p className="fileSuccess">File Selected</p>
                <p className="fileName">{file.name}</p>
              </>
            ) : (
              <>
                <p className="uploadTitle">Upload Answer Sheet</p>
                <p className="uploadSub">Click to select PDF</p>
              </>
            )}
          </div>

          {/* BUTTON */}
          <button
            className="button"
            onClick={handleUpload}
            disabled={loading}
          >
            {loading ? "Evaluating..." : "Evaluate Answer Sheet"}
          </button>

        </div>

      </div>

    </div>
  );
}

export default EvaluationPage;