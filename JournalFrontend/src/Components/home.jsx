import { useEffect, useState } from "react";
import removeMarkdown from "remove-markdown";
import "./home.css";

function Home() {
  const [username, setUsername] = useState("");
  const [token, setToken] = useState("");
  const [journal, setJournal] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  // const query = new URLSearchParams(window.location.search);
  // const githubCode = query.get("code");
  // const state = query.get("state");

  useEffect(() => {
    async function getToken() {
      console.log("fetching token");
      const tokenResponse = await fetch(
        `http://127.0.0.1:8000/getUserAccessToken?code=${localStorage.getItem(
          "github_code"
        )}&state=${localStorage.getItem("github_state")}&scope=repo`
      );

      const tokenData = await tokenResponse.json();
      console.log("tokenData", tokenData);
      const accessToken = tokenData.access_token;
      localStorage.setItem("token", accessToken);
      setToken(accessToken); // triggers the second useEffect
    }

    getToken(); // run once
  }, []);

  useEffect(() => {
    async function fetchData() {
      if (!token) {
        console.log("token", token);
        return;
      }
      console.log("userToken", token);
      const userToken = localStorage.getItem("token");

      const userResponse = await fetch("https://api.github.com/user", {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/vnd.github+json",
        },
      });

      const userData = await userResponse.json();
      console.log("user", userData);
      setUsername(userData.login);
    }

    fetchData(); // run only when token is ready
  }, [token]);
  async function handleGenerateJournal() {
    // if (!token) {
    //   console.log("token not available", localStorage.g);
    //   return;
    // }
    let userToken = localStorage.getItem("token");

    const response = await fetch(`http://127.0.0.1:8000/events?code=${token}`, {
      method: "GET",
    });

    const data = await response.json();
    console.log("data", data);
    console.log("data", data.candidates[0].content.parts[0].text);
    const promtOutput = data.candidates[0].content.parts[0].text;
    const journalText = promtOutput || "No journal data found."; // Assume `journal` key or fallback
    const text = removeMarkdown(journalText);

    typeOutJournal(text);
  }

  function typeOutJournal(text) {
    setJournal("");
    setIsTyping(true);
    const lines = text.split("\n");
    let currentLine = 0;

    const interval = setInterval(() => {
      setJournal((prev) => prev + lines[currentLine] + "\n");
      currentLine++;
      if (currentLine >= lines.length) {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 100); // Typing speed per line
  }

  return (
    <div className="home-container">
      {username && (
        <h2 className="greeting">Hello {username}, Journal your git.</h2>
      )}
      {username && (
        <button
          className="generate-btn"
          onClick={handleGenerateJournal}
          disabled={isTyping}
        >
          {isTyping ? "Generating..." : "Generate Journal"}
        </button>
      )}
      <textarea
        className="journal-box"
        value={journal}
        readOnly
        placeholder="Your generated journal will appear here..."
      />
    </div>
  );
}

export default Home;
