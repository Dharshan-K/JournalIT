import React, { useState } from "react";
import "./SignIn.css";

function SignIn() {
  const [isSignUp, setIsSignUp] = useState(true);
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

    // const endpoint = isSignUp ? "signUp" : "login";

    // const response = await fetch(`http://127.0.0.1:8000/${endpoint}`, {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify(form),
    // });

    // if (response.ok) {
    //   sessionStorage.setItem("username", response.body.userName);
    //   sessionStorage.setItem("lastUpdated", response.body.lastUpdated);
    //   window.location.href =
    //     "https://github.com/login/oauth/authorize?client_id=Ov23liYRhS6aIOrQ4ltR&redirect_uri=http://localhost:5173/callback&scope=repo,admin:repo_hook,user";
    // } else {
    //   console.log(response.body);
    //   alert(response);
    // }
  };

  return (
    <div className="container">
      {/* <div className="card">
        <h2>{isSignUp ? "Sign Up" : "Login"}</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="userName"
            placeholder="Username"
            value={form.userName}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            required
          /> */}
      <button onClick={handleSubmit}>Login</button>
      {/* </form>
        <p className="toggle" onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp
            ? "Already have an account? Login"
            : "Don't have an account? Sign Up"}
        </p> */}
      {/* </div> */}
    </div>
  );
}

export default SignIn;
