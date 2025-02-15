import React, { useState } from 'react';
import "./App.css";
import RoboGator from "./media/RoboGator.png";
import { parseContent } from './parser';

function App() { 
  const [topic, setTopic] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  // Takes input from the user
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Send the topic to the Python backend and waits for a response
    const response = await fetch('http://127.0.0.1:5000/api/greet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic }),
    });

    // Get the JSON response from the server
    const data = await response.json();
    setResponseMessage(data.message);
  };

  // Returns an html component to the index.html file
  return (
    <div className="App">
      <img className="RoboGator" src={RoboGator}></img>
      <div className= "TextBox">
      {responseMessage ? <p>{parseContent(responseMessage)}</p> : <p>Ready to start learning about Data Structures and Algorithms? Ask a question, and lets get started.</p>}
      </div>
      <div className="Triangle-wrapper">
        <div className="Triangle"></div>
      </div>
      <form onSubmit={handleSubmit}>
      <div className='Input'>
        <input
              placeholder="Enter your topic here"
              className="input-field"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
            />
        <button className="button" type="submit">↑</button>
      </div>
      </form>
    </div>
  );
}

export default App;
