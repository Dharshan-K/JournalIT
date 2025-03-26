import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown'; // Install via npm: npm install react-markdown

function JournalEditor() {
  const location = useLocation();
  const { title, startDate, endDate } = location.state || {};
  const [markdown, setMarkdown] = useState('');
  const [preview, setPreview] = useState(false);

  const handleSave = () => {
    // Here, you would implement the API call to save the markdown to GitHub
    console.log('Saving journal entry:', { title, startDate, endDate, markdown });
    alert('Journal entry saved (simulate API call)!');
  };

  return (
    <div style={styles.container}>
      <h1>{title || 'Journal Editor'}</h1>
      <p>Timeframe: {startDate} to {endDate}</p>
      <div style={styles.editorSection}>
        <button onClick={() => setPreview(!preview)} style={styles.toggleButton}>
          {preview ? 'Edit Markdown' : 'Preview Markdown'}
        </button>
        {preview ? (
          <div style={styles.preview}>
            <ReactMarkdown>{markdown}</ReactMarkdown>
          </div>
        ) : (
          <textarea
            value={markdown}
            onChange={e => setMarkdown(e.target.value)}
            placeholder="Write your journal entry in Markdown..."
            style={styles.textarea}
          />
        )}
      </div>
      <button onClick={handleSave} style={styles.button}>Save Journal Entry</button>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif'
  },
  form: {
    display: 'flex',
    flexDirection: 'column'
  },
  formGroup: {
    marginBottom: '15px'
  },
  input: {
    padding: '8px',
    fontSize: '1rem',
    marginTop: '5px'
  },
  button: {
    padding: '10px',
    fontSize: '1rem',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    cursor: 'pointer'
  },
  editorSection: {
    marginTop: '20px'
  },
  toggleButton: {
    padding: '8px 12px',
    fontSize: '0.9rem',
    marginBottom: '10px'
  },
  textarea: {
    width: '100%',
    height: '200px',
    padding: '10px',
    fontFamily: 'monospace'
  },
  preview: {
    border: '1px solid #ccc',
    padding: '10px',
    minHeight: '200px'
  }
};

export default JournalEditor