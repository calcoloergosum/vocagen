// The application plays example sentences and shows images of the words in the sentence.
// Automatically play the next sentence after the current sentence is finished.

import React, { useCallback, useEffect } from 'react';
import './App.css';
import { GoScreenFull, GoScreenNormal, GoReport } from "react-icons/go";
import { TiMediaPlayReverse, TiMediaPlay, TiMediaRewind, TiMediaFastForward, TiTimes, TiThList } from "react-icons/ti";

interface Sentence {
  id: string;  // unique identifier
  sentence1: string;  // Sentence in L1
  sentence2: string;  // Sentence in L2
  audioUrls: string[];  // first audio is L1 sentence, the rest is L2 sentence
  imageUrl: string;
  imageIsRandom: boolean;
}

const emojiMap: { [key: string]: string } = {
  'en': '🇬🇧',
  'ja': '🇯🇵',
  'hi': '🇮🇳',
  'ko': '🇰🇷'
}

function App() {
  // Select the language pair and redirect to the SentenceViewer
  const [languagePair, setLanguagePair] = React.useState<{ L1: string, L2: string } | null>(null);
  const [mode, setMode] = React.useState('sentence');
  const languagePairs = [
    { L1: 'ja', L2: 'en' },
    { L1: 'en', L2: 'hi' },
    { L1: 'en', L2: 'ko' },
    { L1: 'en', L2: 'ja' },
  ]

  const onExit = useCallback(() => {
    setLanguagePair(null);
    setMode('');  // Reset the mode
  }, [setLanguagePair, setMode]);

  if (languagePair) {
    if (!mode) {
      // Not selected yet. Do nothing.
    }
    else if (mode === 'sentence') {
      return <SentencePlayer L1={languagePair.L1} L2={languagePair.L2} />
    }
    else if (mode === 'word') {
      return <WordViewer L1={languagePair.L1} L2={languagePair.L2} onExit={onExit}/>
    }
    else {
      // ?? ... Do nothing
    }
  }
  return (
    <table>
      <thead>
        <tr>
          <th>L1</th>
          <th>L2</th>
          <th>Sentences</th>
          <th>Words</th>
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
                  <button className="link" onClick={() => { setLanguagePair(pair); setMode('sentence'); }} />
                </td>
                <td>
                  <button className="link" onClick={() => { setLanguagePair(pair); setMode('word'); }} />
                </td>
              </tr>)
          )
        }
      </tbody>
    </table>
  )
}


// Given a word, show 10 example sentences using the word.
function WordViewer({ L1, L2, onExit }: { L1: string, L2: string, onExit: () => void }) {
  const [currentWord, setCurrentWord] = React.useState<string | null>(null);
  const [currentSentenceIndex, setCurrentSentenceIndex] = React.useState(0);
  const [currentTranslation, setCurrentTranslation] = React.useState(L2);
  const [sentences, setSentences] = React.useState<Sentence[]>([]);
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  useEffect(() => {
    updateWord();
  }, []);

  useEffect(() => {
    // Keyboard event listener
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Tab") {
        setIsCollapsed((pre) => !pre);
        e.preventDefault();
      }
      if (e.key === "Escape") {
        onExit();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return function cleanup() {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, [setIsCollapsed, onExit]);

  const updateWord = useCallback(() => {
    const url = `/api/word/${L1}/${L2}/random`
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        setCurrentWord(data.word);
        setSentences(data.sentences);
        setCurrentSentenceIndex(0);
      })
      .catch((e) => {
        // Show error message in popup
        alert('Failed to load the word: ' + e);
      });
  }, [L1, L2, setCurrentWord, setSentences, setCurrentSentenceIndex]);

  const updateWordBack = () => {
    // TODO: Implement updateWordBack
    updateWord();
  }

  const updateSentenceIndex = useCallback(() => {
    if (currentSentenceIndex + 1 >= sentences.length) {
      updateWord();
      return;
    }
    setCurrentSentenceIndex((pre) => pre + 1);
  }, [L1, L2, setCurrentWord, setSentences, sentences, currentSentenceIndex, setCurrentSentenceIndex]);

  const updateSentenceIndexBack = useCallback(() => {
    if (currentSentenceIndex - 1 < 0) {
      updateWordBack();
      return;
    }
    setCurrentSentenceIndex((pre) => pre - 1);
  }, [currentSentenceIndex, setCurrentSentenceIndex]);

  // Overlay left 20% of the screen shows the word and sentence list
  // on top of the image (SentenceViewer).
  //
  // Clicking on the sentence in the list will play the sentence.
  // Highlight current sentence in the list.
  // Align the text in the middle of the screen.
  // Collapsable, opacity 0.5 when shown.
  return (
    <div>
      {currentWord && sentences && (
        <div>
          <div style={{ position: "absolute", top: 0, left: 0 }}>
            <SentenceViewer sentence={sentences[currentSentenceIndex]} onEnded={updateSentenceIndex} />
          </div>
          {
            isCollapsed ?
              <TiThList onClick={() => setIsCollapsed(!isCollapsed)} style={{ position: "absolute", backgroundColor: "rgba(255, 255, 255, 0.5)" }} /> :
              <div style={{
                position: 'absolute', width: "20vw", height: "100vh", float: "left", textAlign: "center", backgroundColor: "rgba(255, 255, 255, 0.5)",
              }}>
                <div style={{ position: "absolute", top: 0, right: 0 }}>
                  <TiTimes onClick={() => setIsCollapsed(!isCollapsed)} />
                </div>
                {/* Show L1 and L2 flags on top*/}
                <h1>
                  <span onClick={() => { setCurrentTranslation(L1) }}>{emojiMap[L1]}</span>
                  <span onClick={() => { setCurrentTranslation(L2) }}>{emojiMap[L2]}</span>
                </h1>
                {/* Show the word and list of sentences */}
                <h1>
                  <TiMediaRewind onClick={updateWordBack} />
                  <TiMediaPlayReverse onClick={updateSentenceIndexBack} />
                  {currentWord}
                  <TiMediaPlay onClick={updateSentenceIndex} />
                  <TiMediaFastForward onClick={updateWord} />
                </h1>
                <ul style={{ listStyleType: "none" }}>
                  {sentences.map((sentence, i) => (
                    <li key={sentence.id} style={{ cursor: "pointer" }} onClick={() => setCurrentSentenceIndex(i)}>
                      {i === currentSentenceIndex ?
                        <b>{currentTranslation == L1 ? sentence.sentence1 : sentence.sentence2}</b> :
                        currentTranslation == L1 ? sentence.sentence1 : sentence.sentence2}
                    </li>
                  ))}
                </ul>
              </div>
          }
        </div>
      )}
    </div>
  );
}


function SentenceViewer({ sentence, onEnded, nRepeat }: { sentence: Sentence, nRepeat?: number, onEnded: () => void }) {
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  React.useEffect(() => {
    // Keyboard event listener
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === " ")
        playToggle();
      else if (e.key === "ArrowRight")
        onEnded();
      else if (e.key === "f")
        toggleFullscreen();
      else console.log(e.key);
    }

    document.addEventListener('keydown', handleKeyDown);
    return function cleanup() {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, [onEnded]);

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

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => {
        setIsFullscreen(true);
      })
        .catch((e) => {
          // Already in fullscreen mode.
          setIsFullscreen(true);
        });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      })
        .catch((e) => {
          // Already in normal mode.
          setIsFullscreen(false);
        });
    }
  }

  return (
    <div>
      {sentence && (
        /* Image in full screen, and overlay the sentence in the middle on top of the image */
        <div>
          <img src={`${sentence?.imageUrl}`} style={{ width: "100vw", height: "100vh", objectFit: "cover", display: "block" }} onClick={playToggle} />
          {/* Text align center */}
          <div style={{ position: 'absolute', top: '50%', left: '20%', right: '20%', transform: 'translate(0%, -50%)' }} onClick={playToggle}>
            <AudioPlayer urls={sentence.audioUrls} nRepeat={nRepeat} onEnded={onEnded} audioRef={audioRef} />
            <h1 className="sentenceL1">{sentence.sentence1}</h1>
            <h1 className="sentenceL2">{sentence.sentence2}</h1>
          </div>

          {/* When clicked right 20% of the screen, skip the current sentence */}
          <div style={{ position: 'absolute', top: '0', left: '80%', right: '0', bottom: '0' }} onClick={onEnded}></div>

          {/* Show report button on left bottom */}
          <div style={{ position: 'absolute', bottom: '0', left: '0', padding: "10px", zIndex: 1000 }}>
            <ReportComponent {...sentence} />
          </div>
          {/* Show the full screen icon on the right bottom */}
          <div style={{ position: 'absolute', bottom: '0', right: '0', padding: "10px" }}>
            {
              <span onClick={toggleFullscreen}>
                {isFullscreen ? <GoScreenNormal /> : <GoScreenFull />}
              </span>
            }
          </div>
        </div>
      )}
    </div>
  );
}


interface SentencePlayerProps {
  L1: string;
  L2: string;
  nRepeat?: number;
}
function SentencePlayer({ L1, L2, nRepeat }: SentencePlayerProps) {
  const [currentSentence, setCurrentSentence] = React.useState<Sentence | null>(null);

  React.useEffect(() => {
    // Load sentences from the server
    updateCurrentSentence();
  }, []);

  const updateCurrentSentence = useCallback(
    () => {
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
    }, [setCurrentSentence]);

  return (
    <div>
      {currentSentence && <SentenceViewer sentence={currentSentence} nRepeat={nRepeat} onEnded={updateCurrentSentence} />}
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
    <div style={{background: "rgba(255, 255, 255, 0.5)"}}>
      <h2><GoReport/>&nbsp;&nbsp;&nbsp;Report</h2>
      <ul style={{ listStyleType: "none" }}>
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
                headers: { 'Content-Type': 'application/json' },
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
// ref is passed for controlling the audio player
function AudioPlayer({ urls, nRepeat, onEnded, audioRef }: { urls: string[], nRepeat?: number, onEnded: () => void, audioRef: React.RefObject<HTMLAudioElement> }) {
  const [isL1, setIsL1] = React.useState(true);  // alternate between L1 and L2
  const [audioIndexL2, setAudioIndexL2] = React.useState(0);
  const [L1audio, ...L2audios] = urls;

  // Reset the audio player when the urls change
  useEffect(() => {
    setIsL1(true);
    setAudioIndexL2(0);
  }, urls);

  return (
    <>
      {/* Play audio */}
      {
        <audio ref={audioRef}
          style={{ display: "none", width: "200px" }}
          src={`${isL1 ? L1audio : L2audios[audioIndexL2 % L2audios.length]}`}
          controls
          autoPlay
          onEnded={
            () => {
              if (isL1) {
                setIsL1(false);
                return;
              }
              // play next L2 sentence
              if (audioIndexL2 + 1 >= (nRepeat || 3)) {
                onEnded();
                setAudioIndexL2(0);
                setIsL1(true);
                return;
              }
              setIsL1(true);
              setAudioIndexL2(audioIndexL2 + 1);
            }
          } />
      }
    </>
  );
}

export default App;
