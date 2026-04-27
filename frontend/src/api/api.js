import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000"
});

// Evaluate API
export const evaluateAnswerSheet = (formData) =>
  API.post("/evaluate", formData);

export default API;