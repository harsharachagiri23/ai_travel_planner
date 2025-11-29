import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import TravelPlanner from "./pages/TravelPlanner";
import TravelResult from "./pages/TravelResult";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TravelPlanner />} />
        <Route path="/result" element={<TravelResult />} />
      </Routes>
    </Router>
  );
}
