import React, { useState } from "react";
import HomePage from "./components/HomePage";
import EvaluationPage from "./components/EvaluationPage";
import ResultPage from "./components/ResultPage";

function App() {

  const [page, setPage] = useState("subjects");
  const [subject, setSubject] = useState("");
  const [result, setResult] = useState(null);

  const renderPage = () => {
    switch (page) {
      case "subjects":
        return <HomePage setPage={setPage} setSubject={setSubject} />;

      case "evaluation":
        return (
          <EvaluationPage
            subject={subject}
            setPage={setPage}
            setResult={setResult}
          />
        );

      case "result":
        return <ResultPage result={result} setPage={setPage} />;

      default:
        return <HomePage setPage={setPage} setSubject={setSubject} />;
    }
  };

  return (
    <div style={styles.appContainer}>

      {/* App Header */}
      <div style={styles.header}>
        <h2>GradeAI</h2>
      </div>

      {/* Page Content */}
      <div style={styles.content}>
        {renderPage()}
      </div>

    </div>
  );
}

export default App;

const styles = {
  appContainer: {
    minHeight: "100vh",
    background: "#0f172a",
    color: "#e2e8f0",
    display: "flex",
    flexDirection: "column"
  },

  header: {
    padding: "20px 40px",
    borderBottom: "1px solid #1e293b",
    fontWeight: "600",
    fontSize: "18px"
  },

  content: {
    flex: 1,
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
  }
};