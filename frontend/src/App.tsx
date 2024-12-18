// The application plays example sentences and shows images of the words in the sentence.
// Automatically play the next sentence after the current sentence is finished.

import React, { useCallback, useEffect } from 'react';
import './App.css';
import { GoScreenFull, GoScreenNormal, GoReport } from "react-icons/go";
import { TiMediaPlayReverse, TiMediaPlay, TiMediaRewind, TiMediaFastForward, TiTimes, TiThList } from "react-icons/ti";
import { AlternatingAudioPlayer, SequentialAudioPlayer } from './AudioPlayers';
import { Link, Route, Routes, useNavigate, useParams } from 'react-router-dom';
import { hash } from 'bcryptjs';


interface Sentence {
  id: string;  // unique identifier
  sentence1: string;  // Sentence in L1
  sentence2: string;  // Sentence in L2
  audioUrls: string[];  // first audio is L1 sentence, the rest is L2 sentence
  imageUrlHorizontal: string;
  imageUrlVertical?: string;
  imageIsRandom: boolean;
}

const emojiMap: { [key: string]: string } = {
  'en': '🇬🇧',
  'ja': '🇯🇵',
  'hi': '🇮🇳',
  'ko': '🇰🇷',
  'ru': '🇷🇺',
}

function App() {
  return (
    <Routes>
      <Route key='main-page' path="/" element={<MainPage />} />
      <Route key='login-page' path="/login" element={<LoginPage />} />
      <Route key='register' path="/register" element={<RegisterPage />} />
      <Route key='statistics' path="/statistics" element={<StatisticsPage />} />
      {LANGUAGE_PAIRS.map((pair, i) => (
        <>
          <Route key={`sentence-${i}-random`} path={`/sentence/${pair.L1}/${pair.L2}/random`} element={<SentencePlayer L1={pair.L1} L2={pair.L2} mode='random' />} />
          <Route key={`sentence-${i}-length`} path={`/sentence/${pair.L1}/${pair.L2}/length`} element={<SentencePlayer L1={pair.L1} L2={pair.L2} mode='length' />} />
          <Route key={`sentence-${i}-length-n`} path={`/sentence/${pair.L1}/${pair.L2}/length/:n`} element={<SentencePlayer L1={pair.L1} L2={pair.L2} mode='length' />} />
        </>
      ))}
      {LANGUAGE_PAIRS.map((pair, i) => (
        <Route key={`word-${i}`} path={`/word/${pair.L1}/${pair.L2}`} element={<SentenceListViewer L1={pair.L1} L2={pair.L2} />} />
      ))}
    </Routes>
  )
}


const LANGUAGE_PAIRS = [
  { L1: 'ja', L2: 'en' },
  { L1: 'en', L2: 'hi' },
  { L1: 'en', L2: 'ko' },
  { L1: 'en', L2: 'ja' },
  { L1: 'en', L2: 'ru' },
]


function MainPage() {
  // Select the language pair and redirect to the SentenceViewer
  return (
    <>
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
            LANGUAGE_PAIRS.map(
              (pair, i) => (
                <tr key={`lang-pair-${i}`}>
                  <td>{emojiMap[pair.L1]}{pair.L1}</td>
                  <td>{emojiMap[pair.L2]}{pair.L2}</td>
                  <td>
                    <Link to={`/sentence/${pair.L1}/${pair.L2}/random`}>O</Link>
                    <Link to={`/sentence/${pair.L1}/${pair.L2}/length`}>O</Link>
                  </td>
                  <td>
                    <Link to={`/word/${pair.L1}/${pair.L2}`}>O</Link>
                  </td>
                </tr>)
            )
          }
        </tbody>
      </table>
      <Link to="/statistics">Statistics</Link>
    </>
  )
}


function LoginPage() {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");

  const handleLogin = useCallback(() => {
    if (email === "" || password === "") {
      alert('Email and password cannot be empty');
      return;
    }
    const hashed = hash('voca-gen.com' + email + password, 10);
    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: hashed })
    }).then((resp) => {
      if (resp.status !== 200) {
        alert('Failed to login');
        return;
      }
      alert('Successfully logged in');
    }).catch(() => {
      // Show error message in popup
      alert('Failed to login');
    });
  }, [email, password]);

  return (
    <>
      <h1>Login</h1>
      <input type="text" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <br />
      <input type="password" placeholder="Password" value={password}
        onChange={(e) => setPassword(e.target.value)}
        onKeyDown={(e) => { e.key === "Enter" && handleLogin(); }} />
      <br />
      <button onClick={handleLogin}>Login</button>
      <br />
      <Link to="/register">Don't have an account? Register</Link>
    </>
  );
};


function RegisterPage() {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const navigate = useNavigate();

  const handleRegister = useCallback(() => {
    if (email === "" || password === "") {
      alert('Email and password cannot be empty');
      return;
    }
    const hashed = hash('voca-gen.com' + email + password, 10);
    fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: hashed })
    }).then((resp) => {
      if (resp.status !== 200) {
        alert('Failed to register');
        return;
      }
      alert('Successfully registered');
      navigate("/");
    }).catch(() => {
      // Show error message in popup
      alert('Failed to register');
    });
  }, [email, password, navigate]);

  return (
    <>
      <h1>Register</h1>
      <input type="text" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <br />
      <input type="password" placeholder="Password" value={password}
        onChange={(e) => setPassword(e.target.value)}
        onKeyDown={(e) => { e.key === "Enter" && handleRegister(); }} />
      <br />
      <button onClick={handleRegister}>Register</button>
    </>
  );
};


interface Statistics {
  email: string;
  nReports: number;
  perLanguagePair: { string: { string: LanguagePairStatistics } };
  achievements: string[];
}

interface LanguagePairStatistics {
  L1: string;
  L2: string;
  totalSeconds: number;
  nSentences: number;
}

function StatisticsPage() {
  const [statistics, setStatistics] = React.useState<Statistics | null>(null);
  const navigate = useNavigate();

  // Redirect to login page, alert of show statistics
  useEffect(() => {
    fetch('/api/statistics')
      .then((response) => response.json())
      .then((data) => {
        setStatistics(data);
      })
      .catch((e) => {
        // Show error message in popup
        alert('Failed to load statistics: ' + e);
        navigate("/login");
      });
  }, [navigate]);

  return (
    statistics && (
      <>
        <h1>Statistics</h1>
        <h2>Contribution</h2>
        <table>
          <tbody>
            <tr>
              <td>Reports</td>
              <td>{statistics.nReports}</td>
            </tr>
          </tbody>
        </table>

        <h2>Study</h2>
        <table>
          <thead>
            <tr>
              <th>L1</th>
              <th>L2</th>
              <th>Total Sentences</th>
              <th>Total Seconds</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(statistics.perLanguagePair).map(
              ([L1, _d], i) => (
                Object.entries(_d).map(([L2, value], j) => (
                  <tr key={`statistics-${i}-${j}`}>
                    <td>{L1}</td>
                    <td>{L2}</td>
                    <td>{value.nSentences}</td>
                    <td>{value.totalSeconds}</td>
                  </tr>
                ))))}
          </tbody>
        </table>
      </>
    )
  );
}

// Given a word, show 10 example sentences using the word.
function SentenceListViewer({ L1, L2, onExit }: { L1: string, L2: string, onExit?: () => void }) {
  const [title, setTitle] = React.useState<string | null>(null);
  const [currentSentenceIndex, setCurrentSentenceIndex] = React.useState(0);
  const [currentTranslation, setCurrentTranslation] = React.useState(L2);
  const [sentences, setSentences] = React.useState<Sentence[]>([]);
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const [hideL1, setHideL1] = React.useState(false);
  const [randomState, setRandomState] = React.useState<number | null>(null);

  useEffect(() => {
    // Keyboard event listener
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Tab") {
        setIsCollapsed((pre) => !pre);
        e.preventDefault();
      }
      if (e.key === "Escape") {
        if (onExit) onExit();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return function cleanup() {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, [setIsCollapsed, onExit]);

  const updateWord = useCallback((state: number | null, action: 'next' | 'prev') => {
    const url = (
      state ?
        `/api/word/${L1}/${L2}/random?seed=${state}&action=${action}` :
        `/api/word/${L1}/${L2}/random?action=${action}`
    )
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        setTitle(data.word);
        setSentences(data.sentences);
        setCurrentSentenceIndex(0);
        setRandomState(data.state);
      })
      .catch((e) => {
        // Show error message in popup
        alert('Failed to load the word: ' + e);
      });
  }, [L1, L2, setTitle, setSentences, setCurrentSentenceIndex, setRandomState]);

  useEffect(() => {
    updateWord(null, "next");
  }, [updateWord]);

  const updateSentenceIndex = useCallback(() => {
    if (currentSentenceIndex + 1 >= sentences.length) {
      updateWord(randomState, 'next');
      return;
    }
    setCurrentSentenceIndex((pre) => pre + 1);
  }, [updateWord, currentSentenceIndex, setCurrentSentenceIndex, sentences, randomState]);

  const updateSentenceIndexBack = useCallback(() => {
    if (currentSentenceIndex - 1 < 0) {
      updateWord(randomState, 'prev');
      return;
    }
    setCurrentSentenceIndex((pre) => pre - 1);
  }, [currentSentenceIndex, setCurrentSentenceIndex, randomState, updateWord]);

  // Overlay left 20% of the screen shows the word and sentence list
  // on top of the image (SentenceViewer).
  //
  // Clicking on the sentence in the list will play the sentence.
  // Highlight current sentence in the list.
  // Align the text in the middle of the screen.
  // Collapsable, opacity 0.5 when shown.
  return (
    <div>
      {title && sentences && (
        <div>
          <div style={{ position: "absolute", top: 0, left: 0 }}>
            <SentenceViewer sentence={sentences[currentSentenceIndex]} hideL1={hideL1}
              onPreviousRequest={updateSentenceIndexBack}
              onNextRequest={updateSentenceIndex} />
          </div>
          {/* Toggle button for showing L1 language */}
          <div style={{ position: "absolute", top: 0, right: 0 }}>
            <label className="switch">
              <input type="checkbox" onChange={(e) => {
                setHideL1(e.target.checked);
              }} />
              <span className="slider round"></span>
            </label>
          </div>
          {
            isCollapsed ?
              <TiThList onClick={() => setIsCollapsed(!isCollapsed)} style={{ position: "absolute", backgroundColor: "rgba(255, 255, 255, 0.5)", height: "100vh" }} /> :
              <div style={{
                position: 'absolute', width: "20vw", height: "100vh", float: "left", textAlign: "center", backgroundColor: "rgba(255, 255, 255, 0.5)",
                overflow: "auto",
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
                  <TiMediaRewind onClick={() => updateWord(randomState, "prev")} />
                  <TiMediaPlayReverse onClick={updateSentenceIndexBack} />
                  {title}
                  <TiMediaPlay onClick={updateSentenceIndex} />
                  <TiMediaFastForward onClick={() => updateWord(randomState, "next")} />
                </h1>
                <ul style={{ listStyleType: "none" }}>
                  {sentences.map((sentence, i) => (
                    <li key={i} style={{ cursor: "pointer" }} onClick={() => setCurrentSentenceIndex(i)}>
                      {i === currentSentenceIndex ?
                        <b>{currentTranslation === L1 ? sentence.sentence1 : sentence.sentence2}</b> :
                        currentTranslation === L1 ? sentence.sentence1 : sentence.sentence2}
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

function SentenceViewer({ sentence, onPreviousRequest, onNextRequest, hideL1, nRepeat }:
  {
    sentence: Sentence, hideL1: boolean, nRepeat?: number, onNextRequest: () => void,
    onPreviousRequest: () => void
  }) {
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  React.useEffect(() => {
    // Keyboard event listener
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === " ")
        playToggle();
      else if (e.key === "ArrowRight")
        onNextRequest();
      else if (e.key === "ArrowLeft")
        onPreviousRequest();
      else if (e.key === "f")
        toggleFullscreen();
      else console.log("Unknown key", e.key);
    }

    document.addEventListener('keydown', handleKeyDown);
    return function cleanup() {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, [onNextRequest, onPreviousRequest]);

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
          <img key='img-horizontal' alt={sentence.sentence1} className="image-horizontal" src={`${sentence?.imageUrlHorizontal}`} style={{
            width: "100vw", height: "100vh", objectFit: "cover"
          }} onClick={playToggle} />
          <img key='img-vertical' alt={sentence.sentence1} className="image-vertical" src={`${sentence?.imageUrlVertical || sentence?.imageUrlHorizontal}`} style={{
            width: "100vw", height: "100vh", objectFit: "cover"
          }} onClick={playToggle} />
          {/* Text align center */}
          <div style={{ position: 'absolute', bottom: '50%', left: '20%', right: '20%', transform: 'translate(0%, 50%)' }} onClick={playToggle}>
            {
              hideL1 ?
                <SequentialAudioPlayer urls={sentence.audioUrls.slice(1)} nRepeat={nRepeat} onEnded={onNextRequest} audioRef={audioRef} />
                :
                <AlternatingAudioPlayer urls={sentence.audioUrls} nRepeat={nRepeat} onEnded={onNextRequest} audioRef={audioRef} />
            }
            <div className="sentences">
              <h1 className="sentenceL2">{sentence.sentence2}</h1>
              {
                hideL1 ? null : <h1 className="sentenceL1">{sentence.sentence1}</h1>
              }
            </div>
          </div>

          {/* When clicked right 20% of the screen, skip the current sentence */}
          <div style={{ position: 'absolute', top: '0', left: '80%', right: '0', bottom: '0' }} onClick={onNextRequest}></div>

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
  mode: 'random' | 'length';
}

function SentencePlayer({ L1, L2, nRepeat, mode }: SentencePlayerProps) {
  const [currentSentence, setCurrentSentence] = React.useState<Sentence | null>(null);
  const { n } = useParams();
  const [randomState, setRandomState] = React.useState<string | null>(mode == 'random'? (n || null): (n || '0'));

  const updateCurrentSentence = useCallback(
    () => {
      if (mode === 'random') {
        const url = `/api/sentence/${L1}/${L2}/random?seed=${randomState}&action=next`
        fetch(url)
          .then((response) => response.json())
          .then((data) => {
            setCurrentSentence(data.sentence);
            setRandomState(data.state);
          })
          .catch((e) => {
            // Show error message in popup
            alert('Failed to load the sentence: ' + e);
          });
      } else {
        const url = `/api/sentence/${L1}/${L2}/length?seed=${randomState}&action=next`
        fetch(url)
          .then((response) => response.json())
          .then((data) => {
            setCurrentSentence(data.sentence);
            setRandomState(data.state);
          })
          .catch((e) => {
            // Show error message in popup
            alert('Failed to load the sentence: ' + e);
          });
      }
    }, [setCurrentSentence, setRandomState, L1, L2, randomState, mode]);

  React.useEffect(() => {
    // Load sentences from the server
    updateCurrentSentence();
  }, []);

  return (
    <>
      <div>
        {currentSentence && <SentenceViewer hideL1={false}
          sentence={currentSentence} nRepeat={nRepeat}
          onPreviousRequest={updateCurrentSentence}
          onNextRequest={updateCurrentSentence} />}
      </div>
    </>
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
      <span onClick={() => {
        if (!currentSentence) return;
        if (currentSentence.imageIsRandom) return;
        setIsReportDialogOpen(true);
      }} style={{ color: (currentSentence.imageIsRandom ? 'red' : 'black') }}>
        <GoReport />
      </span>
    );
  }

  return (
    <div style={{ background: "rgba(255, 255, 255, 0.5)" }}>
      <h2><GoReport />&nbsp;&nbsp;&nbsp;Report</h2>
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

export default App;
