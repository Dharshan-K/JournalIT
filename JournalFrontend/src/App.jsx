import { useState } from "react";
import "./App.css";
import Home from "./Components/home.jsx";
import SignIn from "./Components/signIn.jsx";
import { Routes, Route } from "react-router-dom";
import CallbackRedirect from "./Components/redirect";

function App() {
  const url =
    "https://github.com/login/oauth/authorize?client_id=Ov23liYRhS6aIOrQ4ltR&redirect_uri=https://your-app.com/auth/github/callback&scope=user&state=random_string";

  return (
    <Routes>
      <Route path="/" element={<SignIn />} />
      <Route path="/home" element={<Home />} />
      <Route path="/callback" element={<CallbackRedirect />} />
    </Routes>
  );
}

export default App;
