import React, { useEffect, useState } from "react";
import "./HomePage.css"; // ✅ IMPORT CSS

function HomePage({ setPage, setSubject }) {

  const [subjects, setSubjects] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/subjects")
      .then(res => res.json())
      .then(data => setSubjects(data));
  }, []);

  return (
    <div className="home-page">

      <div className="home-content">

        <h1 className="home-title">Select Subject</h1>

        <div className="home-grid">
          {subjects.map((sub, i) => (
            <div
              key={i}
              className="home-card"
              onClick={() => {
                setSubject(sub);
                setPage("evaluation");
              }}
            >
              {sub.toUpperCase()}
            </div>
          ))}
        </div>

      </div>

    </div>
  );
}

export default HomePage;