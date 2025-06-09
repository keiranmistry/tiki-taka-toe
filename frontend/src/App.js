import React, { useEffect, useState } from 'react';

function App() {
  const [clubs, setClubs] = useState([]);
  const [countries, setCountries] = useState([]);
  const [guesses, setGuesses] = useState({});
  const [clubInput, setClubInput] = useState('');
  const [countryInput, setCountryInput] = useState('');
  const [playerInput, setPlayerInput] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch("http://127.0.0.1:5000/generate-grid")
      .then(res => res.json())
      .then(data => {
        setClubs(data.clubs);
        setCountries(data.countries);
      });
  }, []);

  const handleGuess = () => {
    fetch("http://127.0.0.1:5000/submit-guess", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        club: clubInput,
        country: countryInput,
        player: playerInput
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.result === "correct") {
        const key = `${clubInput}|${countryInput}`;
        setGuesses({ ...guesses, [key]: data.player });
        setMessage("✅ Correct!");
      } else {
        setMessage("❌ Incorrect");
      }
    });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>⚽ Soccer Tic Tac Toe</h1>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th></th>
            {countries.map(country => <th key={country}>{country}</th>)}
          </tr>
        </thead>
        <tbody>
          {clubs.map(club => (
            <tr key={club}>
              <td><strong>{club}</strong></td>
              {countries.map(country => {
                const key = `${club}|${country}`;
                return <td key={key}>{guesses[key] || "___"}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Enter Your Guess</h2>
      <input placeholder="Club" value={clubInput} onChange={e => setClubInput(e.target.value)} />
      <input placeholder="Country" value={countryInput} onChange={e => setCountryInput(e.target.value)} />
      <input placeholder="Player" value={playerInput} onChange={e => setPlayerInput(e.target.value)} />
      <button onClick={handleGuess}>Submit</button>

      <p>{message}</p>
    </div>
  );
}

export default App;
