import React, { useState } from 'react';

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

  // Returns an html component to the indeex.html file
  return (
    <div className="App">
      <h1>React & Flask Topic Explorer</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Enter your name:
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            required
          />
        </label>
        <button type="submit">Submit</button>
      </form>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default App;
