import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown'; // Install via npm: npm install react-markdown

function JournalSpecifications() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);

    const githubCode = query.get('code');
    const state = query.get('state');
    const url = `https://github.com/login/oauth/access_token?`;
    console.log("code, state", githubCode, state);
    async function fetchData() {
      await fetch(`http://127.0.0.1:8000/getUserAccessToken?code=${githubCode}&state=${state}&scope=repo`, {
        method: "GET"
      }).then(async (response) => {
        const data = await response.json();
        console.log(data.access_token);
        await fetch("https://api.github.com/user/repos", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${data.access_token}`,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            "name": "first API",
            "description": "Created from github API",
            "private": false
          })
        }).then(async (response) => {
          const data = await response.json();
          console.log("response", data);
        });
      });
    }

    fetchData();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Navigate to the editor page with the form data
    navigate('/editor', { state: { title } });
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Journal Specifications</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label style={styles.label}>Journal Title:</label>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Enter journal title"
            required
            style={styles.input}
          />
        </div>
        <p style={styles.note}>The journal will be generated based on the last 24 hours of activity.</p>
        <button type="submit" style={styles.button}>Proceed to Journal Editor</button>
      </form>
    </div>
  );
}

// Updated styles for a more modern look
const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
  },
  header: {
    textAlign: 'center',
    color: '#333',
    marginBottom: '20px'
  },
  form: {
    display: 'flex',
    flexDirection: 'column'
  },
  formGroup: {
    marginBottom: '20px'
  },
  label: {
    fontSize: '1rem',
    color: '#555',
    marginBottom: '5px',
    display: 'block'
  },
  input: {
    padding: '10px',
    fontSize: '1rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: '100%',
    boxSizing: 'border-box'
  },
  note: {
    fontSize: '0.9rem',
    color: '#666',
    marginBottom: '20px',
    fontStyle: 'italic'
  },
  button: {
    padding: '12px',
    fontSize: '1rem',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
    width: '100%'
  },
  buttonHover: {
    backgroundColor: '#218838'
  }
};

export default JournalSpecifications;