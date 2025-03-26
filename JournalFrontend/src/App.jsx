import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Home from "./Components/home.jsx";
import SignIn from "./Components/signIn.jsx"
import { Routes, Route } from "react-router-dom";
import JournalSpecifications from "./Components/journalSpec.jsx"
import JournalEditor from "./Components/journalEditor.jsx"


function App() {
  const [count, setCount] = useState(0);
  const url = "https://github.com/login/oauth/authorize?client_id=Ov23liYRhS6aIOrQ4ltR&redirect_uri=https://your-app.com/auth/github/callback&scope=user&state=random_string"

  return (
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/home" element={<Home />} />
        <Route path="/generateJournal" element={<JournalSpecifications />} />
        <Route path="/editor" element={<JournalEditor />} />
      </Routes>

  )
}

export default App
