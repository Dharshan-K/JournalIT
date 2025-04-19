import { useEffect, useState } from "react";
import removeMarkdown from "remove-markdown";
import "./home.css";

function Home() {
  const [username, setUsername] = useState("");
  const [reponame, setReponame] = useState("");
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [journal, setJournal] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [githubPagesUrl, setGithubPagesUrl] = useState("");
  const [isPushing, setIsPushing] = useState(false);

  useEffect(() => {
    async function getToken() {
      const tokenResponse = await fetch(
        `https://journalit-backend.onrender.com/getUserAccessToken?code=${localStorage.getItem(
          "github_code"
        )}&state=${localStorage.getItem("github_state")}&scope=repo`
      );

      const tokenData = await tokenResponse.json();
      const accessToken = tokenData.access_token;
      localStorage.setItem("token", accessToken);
      setToken(accessToken);
    }

    getToken();
  }, []);

  useEffect(() => {
    async function fetchData() {
      if (!token) {
        return;
      }
      const userToken = localStorage.getItem("token");

      const userResponse = await fetch("https://api.github.com/user", {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/vnd.github+json",
        },
      });
      const userData = await userResponse.json();
      if (userData.login) {
        const storeUser = await fetch(
          "https://journalit-backend.onrender.com/createUser",
          {
            method: "POST",
            headers: {
              Accept: "application/json",
            },
            body: JSON.stringify({
              userName: userData.login,
              email: userData.email,
            }),
          }
        );
      }
      setUsername(userData.login);
      setEmail(userData.email);
    }

    fetchData();
  }, [token]);
  async function handleGenerateJournal() {
    if (!token) {
      alert("github token not available. log in again");
      return;
    }
    let userToken = localStorage.getItem("token");
    setIsGenerating(true);
    setIsTyping(true);

    const response = await fetch(
      `https://journalit-backend.onrender.com/events?code=${token}&userName=${username}`,
      {
        method: "GET",
      }
    );

    const data = await response.json();
    const promtOutput = data.candidates[0].content.parts[0].text;
    const journalText = promtOutput || "No journal data found.";
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
    }, 100);
  }

  async function handlePushToGitHub() {
    const userToken = localStorage.getItem("token");
    setIsPushing(true);

    try {
      const response = await fetch(
        "https://journalit-backend.onrender.com/commitJournal",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            journal: journal,
            userName: username,
            token: token,
            email: email,
          }),
        }
      );

      if (!response.ok) {
        const message = response.json();
        throw new Error("Failed to commit journal");
      }

      const data = await response.json();
      const htmlUrl = data.response["html_url"];
      setGithubPagesUrl(htmlUrl);
    } catch (error) {
      console.error(error);
      console.log("Failed to push journal.");
    } finally {
      setIsPushing(false);
    }
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
          {isGenerating && isTyping ? "Generating..." : "Generate Journal"}
        </button>
      )}
      <div className="journal-container">
        <textarea
          className="journal-box"
          value={journal}
          readOnly
          placeholder="Your generated journal will appear here..."
        />
        {journal && (
          <div className="button-row">
            {githubPagesUrl && (
              <a
                href={githubPagesUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <button className="visit-btn">Visit GitHub Pages</button>
              </a>
            )}
            <button
              className="push-btn"
              onClick={handlePushToGitHub}
              disabled={isPushing}
            >
              {isPushing ? "Pushing..." : "Push to GitHub"}
              {isPushing && <span className="loader" />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
