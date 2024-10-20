// The application plays example sentences and shows images of the words in the sentence.
// Automatically play the next sentence after the current sentence is finished.

import React from 'react';
import logo from './logo.svg';
import './App.css';
import { BACKEND } from './constants';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Link,
} from "react-router-dom";

interface Sentence {
  id: string;  // unique identifier
  sentence1: string;  // Sentence in L1
  sentence2: string;  // Sentence in L2
  audioUrls: string[];  // first audio is L1 sentence, the rest is L2 sentence
  imageUrl: string;
}


function App() {
  // Select the language pair and redirect to the SentenceViewer
  return (
    <Router>
      <Routes>
        <Route path="/" element={<div>
          <h1>Choose a language pair</h1>
          <Link to="/en/hi">Study Hindi using English</Link>
          <br />
          <Link to="/en/ko">Study Korean using English</Link>
        </div>} />
        <Route path="/en/hi" element={<SentenceViewer L1='en' L2='hi'/>} />
        <Route path="/en/ko" element={<SentenceViewer L1='en' L2='ko'/>} />
      </Routes>
    </Router>
  )
}

interface SentenceViewerProps {
  L1: string;
  L2: string;
}
function SentenceViewer({ L1, L2 }: SentenceViewerProps) {
  const [currentSentence, setCurrentSentence] = React.useState<Sentence | null>(null);
  const [audioIndex, setAudioIndex] = React.useState(0);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  const updateCurrentSentence = () => {
    fetch(`${BACKEND}/api/sentence/${L1}/${L2}/random`)
      .then(response => response.json())
      .then(data => {
        setCurrentSentence(data);
      });
  };

  // Load sentences from the server
  React.useEffect(() => {
    updateCurrentSentence();
  }, []);

  // Play the next sentence in audios when the current audio is finished
  React.useEffect(() => {
    if (!currentSentence) {
      return;
    }
  }, [currentSentence]);

  return (
    <div>
      {currentSentence && (
        /* Image in full screen, and overlay the sentence in the middle on top of the image */
        <div>
          <img src={`${BACKEND}/${currentSentence?.imageUrl}`} alt="Image" style={{ width: "100vw", height: "100vh", objectFit: "cover", display: "block"}} />
          {/* Text align center */}
          <div style={{ position: 'absolute', top: '50%', left: '10%', right: '10%', transform: 'translate(0%, -50%)' }}>

          <audio src={`${BACKEND}/${currentSentence?.audioUrls[audioIndex]}`} controls ref={audioRef} autoPlay onEnded={
              () => {
                if (audioIndex + 1 >= currentSentence.audioUrls.length) {
                  setAudioIndex(0);
                  updateCurrentSentence();
                  return;
                }
                setAudioIndex(audioIndex + 1);
                audioRef.current?.play();
              }
            } />

            {/* Button to report issues on current sentence */}
            <button onClick={() => {
              fetch(`${BACKEND}/api/report`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(currentSentence)
              }).then((resp) => {
                // Show success message in popup
                if (resp.status !== 200) {
                  alert('Failed to report the sentence');
                  return;
                }
                alert('Successfully reported the sentence');
              }).catch(() => {
                // Show error message in popup
                alert('Failed to report the sentence');
              });
            }}>Report</button>
            <h1 className="sentenceL1">{currentSentence.sentence1}</h1>
            <h1 className="sentenceL2">{currentSentence.sentence2}</h1>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
