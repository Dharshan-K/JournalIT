import React, { useState } from "react";
import "./SignIn.css";

function SignIn() {
  const [form, setForm] = useState({
    userName: "",
    password: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    window.location.href =
      "https://github.com/login/oauth/authorize?client_id=Ov23liYRhS6aIOrQ4ltR&redirect_uri=https://j-it.netlify.app/callback&scope=repo,admin:repo_hook,user";
  };

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Jit</h1>
        <p className="tagline">
          Journal-It: Reflect on your code, one commit at a time.
        </p>
        <button className="github-button" onClick={handleSubmit}>
          <img
            src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            alt="GitHub Logo"
          />
          Login with GitHub
        </button>
      </div>
    </div>
  );
}

export default SignIn;
