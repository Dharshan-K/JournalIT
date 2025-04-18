import React, { useState } from "react";
import "./SignIn.css";

function SignIn() {
  const [form, setForm] = useState({
    userName: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    window.location.href =
      "https://github.com/login/oauth/authorize?client_id=Ov23liYRhS6aIOrQ4ltR&redirect_uri=http://localhost:5173/callback&scope=repo,admin:repo_hook,user";
  };

  return (
    <div className="container">
      <button type="button" onClick={handleSubmit}>
        Login with Github
      </button>
    </div>
  );
}

export default SignIn;
