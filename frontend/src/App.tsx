// The application plays example sentences and shows images of the words in the sentence.
// Automatically play the next sentence after the current sentence is finished.

import React, { useEffect } from 'react';
import './App.css';
import { GoScreenFull, GoScreenNormal, GoReport } from "react-icons/go";

interface Sentence {
  id: string;  // unique identifier
  sentence1: string;  // Sentence in L1
  sentence2: string;  // Sentence in L2
  audioUrls: string[];  // first audio is L1 sentence, the rest is L2 sentence
  imageUrl: string;
  imageIsRandom: boolean;
}


function App() {
  // Select the language pair and redirect to the SentenceViewer
  const [languagePair, setLanguagePair] = React.useState<{ L1: string, L2: string } | null>(null);
  const languagePairs = [
    { L1: 'ja', L2: 'en' },
    { L1: 'en', L2: 'hi' },
    { L1: 'en', L2: 'ko' },
    { L1: 'en', L2: 'ja' },
  ]
  const emojiMap: { [key: string]: string } = {
    'en': '🇬🇧',
    'ja': '🇯🇵',
    'hi': '🇮🇳',
    'ko': '🇰🇷'
  }
  return (
    languagePair ? <SentenceViewer L1={languagePair.L1} L2={languagePair.L2} /> :
      (
        <table>
          <thead>
            <tr>
              <th>L1</th>
              <th>L2</th>
              <th>Go</th>
            </tr>
          </thead>
          <tbody>
            {
              languagePairs.map(
                (pair, i) => (
                  <tr key={`lang-pair-${i}`}>
                    <td>{emojiMap[pair.L1]}{pair.L1}</td>
                    <td>{emojiMap[pair.L2]}{pair.L2}</td>
                    <td>
                      <button className="link" onClick={() => { setLanguagePair(pair); }} />
                    </td>
                  </tr>)
              )
            }
          </tbody>
        </table>
      )
  )
}


interface SentenceViewerProps {
  L1: string;
  L2: string;
}
function SentenceViewer({ L1, L2 }: SentenceViewerProps) {
  const [currentSentence, setCurrentSentence] = React.useState<Sentence | null>(null);
  const audioRef = React.useRef<HTMLAudioElement>(null);
  const [isFullscreen, setIsFullscreen] = React.useState(false);

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

  React.useEffect(() => {
    // Load sentences from the server
    updateCurrentSentence();
    console.log("Loaded sentence");

    // Keyboard event listener
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === " ")
        playToggle();
    }

    document.addEventListener('keydown', handleKeyDown);
    return function cleanup() {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, []);

  const playToggle = () => {
    if (audioRef.current) {
      if (audioRef.current.paused) {
        audioRef.current.play().catch(() => {
          // Already playing, or interrupted by another play request.
          // Do nothing.
        });
      } else {
        audioRef.current.pause();
        // Pause raises no error. Do nothing.
      }
    }
  }
  return (
    <div>
      {currentSentence && (
        /* Image in full screen, and overlay the sentence in the middle on top of the image */
        <div>
          <img src={`${currentSentence?.imageUrl}`} style={{ width: "100vw", height: "100vh", objectFit: "cover", display: "block" }} onClick={playToggle} />
          {/* Text align center */}
          <div style={{ position: 'absolute', top: '50%', left: '10%', right: '10%', transform: 'translate(0%, -50%)' }} onClick={playToggle}>
            <AudioPlayer urls={currentSentence.audioUrls} onEnded={updateCurrentSentence} audioRef={audioRef} />
            <h1 className="sentenceL1">{currentSentence.sentence1}</h1>
            <h1 className="sentenceL2">{currentSentence.sentence2}</h1>
          </div>

          {/* When clicked right 20% of the screen, skip the current sentence */}
          <div style={{ position: 'absolute', top: '0', left: '80%', right: '0', bottom: '0' }} onClick={updateCurrentSentence}></div>

          {/* Show report button on left bottom */}
          <div style={{ position: 'absolute', bottom: '0', left: '0', padding: "10px" }}>
            <ReportComponent {...currentSentence} />
          </div>
          {/* Show the full screen icon on the right bottom */}
          <div style={{ position: 'absolute', bottom: '0', right: '0', padding: "10px" }}>
            {
              <button onClick={
                async () => {
                  if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen().then(() => {
                      setIsFullscreen(true);
                    })
                      .catch((e) => {
                        // Already in fullscreen mode.
                        setIsFullscreen(true);
                      });
                  } else {
                    console.log(document.fullscreenElement);
                    document.exitFullscreen().then(() => {
                      setIsFullscreen(false);
                    })
                      .catch((e) => {
                        // Already in normal mode.
                        setIsFullscreen(false);
                      });
                  }
                }
              }>
                {isFullscreen ? <GoScreenNormal /> : <GoScreenFull />}
              </button>
            }
          </div>
        </div>
      )}
    </div>
  );
}

function ReportComponent(currentSentence: Sentence) {
  // Pop up a dialog to ask for reason and confirm the report.
  // Reasons include:
  // - The sentence is incorrect
  // - The sentence is inappropriate
  // - The image is not related to the sentence
  // - The image is inappropriate
  const [isReportDialogOpen, setIsReportDialogOpen] = React.useState(false);
  const reasons = [
    "The sentence is incorrect",
    "The sentence is inappropriate",
    "The image is not related to the sentence",
    "The image is inappropriate"];

  if (!isReportDialogOpen) {
    return (
      <button disabled={currentSentence.imageIsRandom} onClick={() => {
        if (!currentSentence) return;
        if (currentSentence.imageIsRandom) return;
        setIsReportDialogOpen(true);
      }}>
        <GoReport />
      </button>
    );
  }

  return (
    <div>
      <h1>Report</h1>
      <ul>
        {reasons.map((reason, i) => (
          <li key={i}>
            <button onClick={() => {
              setIsReportDialogOpen(false);

              if (!currentSentence) return;
              if (currentSentence.imageIsRandom) return;
              let report = JSON.parse(JSON.stringify(currentSentence));
              report.reason = reason;
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
            }}>{reason}</button>
          </li>
        ))}
        <li>
          <button onClick={() => setIsReportDialogOpen(false)}>Cancel</button>
        </li>
      </ul>
    </div>
  );
}

// Audio player component
// First audio is L1 sentence, the rest is L2 sentence
function AudioPlayer({ urls, onEnded, audioRef }: { urls: string[], onEnded: () => void, audioRef: React.RefObject<HTMLAudioElement> }) {
  const [isL1, setIsL1] = React.useState(true);  // alternate between L1 and L2
  const [audioIndex, setAudioIndex] = React.useState(1);

  // Reset the audio player when the urls change
  useEffect(() => {
    setIsL1(true);
    setAudioIndex(1);
  }, urls);

  return (
    <>
      {/* Play audio */}
      {
        urls.length >= 2 && (
          <audio style={{ display: "none", width: "200px" }} src={`${isL1 ? urls[0] : urls[audioIndex]}`} controls ref={audioRef} autoPlay
            onEnded={
              () => {
                if (isL1) {
                  setIsL1(false);
                  return;
                }
                // play next L2 sentence
                if (audioIndex + 2 >= urls.length) {
                  onEnded();
                  setAudioIndex(1);
                  setIsL1(true);
                  return;
                }
                setIsL1(true);
                setAudioIndex(audioIndex + 1);
              }
            } />
        )
      }
    </>
  );
}

export default App;
