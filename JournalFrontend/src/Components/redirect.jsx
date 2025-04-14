// CallbackRedirect.jsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function CallbackRedirect() {
  const navigate = useNavigate();
  console.log("welcome callback");

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const code = query.get("code");
    const state = query.get("state");
    console.log("code and state", code, state);

    localStorage.setItem("github_code", code);
    localStorage.setItem("github_state", state);

    navigate("/home");
  }, []);

  return <p>Redirecting...</p>;
}

export default CallbackRedirect;
