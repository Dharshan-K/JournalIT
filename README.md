# 📘 Jit — Journal-IT

**Jit (short for Journal-IT)** is a developer productivity tool that **automatically generates a detailed journal of your GitHub activity** — including commits, pull requests, and issues — using the power of the **Gemini API** and the **GitHub API**.

With a single click, developers can turn their daily contributions into structured, insightful journal entries — and publish them as a personal webpage using **GitHub Pages**.

---

## 🚀 Features

- 🔐 **Seamless GitHub Login**  
  No account creation needed — just authenticate with GitHub.

- 🧠 **Intelligent Prompt Construction**  
  Efficiently fetches and summarizes GitHub activity (commits, PRs, issues) into < 100K tokens using custom prompt-building logic.

- 📄 **Auto-generated Journal Entries**  
  Converts contributions into readable, Markdown-based developer journals.

- 🌐 **One-click Deployment**  
  Automatically creates a GitHub repository, pushes the journal, and deploys it to GitHub Pages.

- 🗃️ **Persistent Entry Tracking**  
  Maintains a JSON-based record of all journal entries.

- ⚙️ **Powered by**:
  - [FastAPI](https://fastapi.tiangolo.com/) for backend services
  - GitHub API for retrieving user contribution data
  - Gemini API for summarizing and interpreting event data
  - HTML/CSS/JavaScript for rendering the journal and frontend interactivity

---

## 🛠️ Architecture Overview

1. **GitHub OAuth**: Authenticates users and fetches their public contribution data.
2. **Prompt Constructor**: Efficiently extracts and structures GitHub event data (commits, diffs, PRs, issues).
3. **Gemini Summarizer**: Sends constructed prompts to the Gemini API and receives back formatted journal content.
4. **HTML Generator**: Converts journal content into a standalone HTML page.
5. **Auto-deploy**: Creates a repository, commits the journal, and deploys it using GitHub Pages.
6. **Data Persistence**: Saves journal metadata in a structured JSON file for historical tracking.

---

## 📷 Demo

> [![Demo Video](https://img.youtube.com/vi/TrdMeH92pwI/0.jpg)](https://www.youtube.com/watch?v=TrdMeH92pwI)

---

## 📦 Tech Stack

- **Backend**: FastAPI (Python)
- **AI Integration**: Gemini API (LLM prompt-based summarization)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: GitHub OAuth & GitHub Events API
- **Deployment**: GitHub Pages

---

## 🧪 Getting Started

> _Add setup instructions here if the project is open-source. For now, you can note that this section is under development or for internal use only._

---

## 🔍 Use Cases

- Maintain a personal developer journal effortlessly.
- Showcase daily coding activity and progress in a readable format.
- Generate an auto-updating developer portfolio using only your GitHub activity.

---

## 💡 Future Improvements

- Add support for private repo journaling.
- GitHub Actions-based automatic daily updates.
- Multiple output formats (PDF/Markdown).
- Analytics dashboard for tracking contributions over time.
- Custom prompt tuning for different journal styles (technical, narrative, concise).

---

## 👨‍💻 Author

**[Dharshan]**  
_Software Engineer | Developer Productivity Enthusiast_  
[LinkedIn](#) | [GitHub](#)
