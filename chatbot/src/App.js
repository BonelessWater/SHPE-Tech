import React, { useState } from 'react';

function App() {
  const [topic, setTopic] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Send the name to the Python backend
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
