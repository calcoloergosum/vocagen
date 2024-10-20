// The application plays example sentences and shows images of the words in the sentence.
// Automatically play the next sentence after the current sentence is finished.

import React from 'react';
import './App.css';

interface Sentence {
  id: string;  // unique identifier
  sentence1: string;  // Sentence in L1
  sentence2: string;  // Sentence in L2
  audioUrls: string[];  // first audio is L1 sentence, the rest is L2 sentence
  imageUrl: string;
}


function App() {
  // Select the language pair and redirect to the SentenceViewer
  const [languagePair, setLanguagePair] = React.useState<{ L1: string, L2: string } | null>(null);

  return (
    languagePair ? <SentenceViewer L1={languagePair.L1} L2={languagePair.L2} /> :
    <>
      <button className="link" onClick={() => {
        setLanguagePair({ L1: 'en', L2: 'hi' });
      }}>Hindi for English speaker</button>
      <button className="link" onClick={() => {
        setLanguagePair({ L1: 'en', L2: 'ko' });
      }}>Korean for English speaker</button>
    </>
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
    const url = `/api/sentence/${L1}/${L2}/random`
    fetch(url)
    .then((response) => response.json())
    .then((data) => {
      setCurrentSentence(data);
    })
    .catch((e) => {
        // Show error message in popup
        alert('Failed to load the sentence: ' + e);
      });
  };

  // Load sentences from the server
  React.useEffect(() => {
    updateCurrentSentence();
    console.log("Loaded sentence");
  }, []);

  return (
    <div>
      {currentSentence && (
        /* Image in full screen, and overlay the sentence in the middle on top of the image */
        <div>
          <img src={`${currentSentence?.imageUrl}`} style={{ width: "100vw", height: "100vh", objectFit: "cover", display: "block"}} />
          {/* Text align center */}
          <div style={{ position: 'absolute', top: '50%', left: '10%', right: '10%', transform: 'translate(0%, -50%)' }}>

          <audio src={`${currentSentence?.audioUrls[audioIndex]}`} controls ref={audioRef} autoPlay onEnded={
              () => {
                if (audioIndex + 1 >= currentSentence.audioUrls.length) {
                  audioRef.current?.pause();
                  setAudioIndex(0);
                  updateCurrentSentence();
                  return;
                }
                audioRef.current?.pause();
                setAudioIndex(audioIndex + 1);
              }
            } />

            {/* Button to report issues on current sentence */}
            <button onClick={() => {
              if (!currentSentence) return;
              let report = JSON.parse(JSON.stringify(currentSentence));
              report.reason = "image";
              fetch(`/api/report`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(report)
              }).then((resp) => {
                // Show success message in popup
                if (resp.status !== 200) {
                  alert('Failed to report the image');
                  return;
                }
                alert('Successfully reported the image');
              }).catch(() => {
                // Show error message in popup
                alert('Failed to report the image');
              });
            }}>Report Image</button>

            <button onClick={() => {
              if (!currentSentence) return;
              let report = JSON.parse(JSON.stringify(currentSentence));
              report.reason = "sentence";
              fetch(`/api/report`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(report)
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
            }}>Report sentence</button>

            <h1 className="sentenceL1">{currentSentence.sentence1}</h1>
            <h1 className="sentenceL2">{currentSentence.sentence2}</h1>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
