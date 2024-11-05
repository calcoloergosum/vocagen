import React, { useCallback } from "react";


// Audio player component
// First audio is L1 sentence, the rest is L2 sentence
// ref is passed for controlling the audio player
export function AlternatingAudioPlayer({ urls, nRepeat, onEnded, audioRef }: { urls: string[], nRepeat?: number, onEnded: () => void, audioRef: React.RefObject<HTMLAudioElement> }) {
    const [whichAudio, setWhichAudio] = React.useState({ isL1: true, audioIndexL2: 0 });
    const [L1audio, ...L2audios] = urls;

    // Reset the audio player when the urls change
    React.useEffect(() => {
        setWhichAudio({ isL1: true, audioIndexL2: 0 });
        audioRef.current?.load();
    }, [urls, audioRef]);

    return (
        <>
            {/* Play audio */}
            {
                <audio ref={audioRef}
                    style={{ display: "none", width: "200px" }}
                    src={`${whichAudio.isL1 ? L1audio : L2audios[whichAudio.audioIndexL2 % L2audios.length]}`}
                    controls
                    onLoadedData={() => {
                        audioRef.current?.play().catch(console.error);
                    }}
                    onEnded={
                        () => {
                            if (whichAudio.isL1) {
                                // L1 finished playing.
                                setWhichAudio((pre) => { return { isL1: false, audioIndexL2: pre.audioIndexL2 } });
                                return;
                            }
                            if (whichAudio.audioIndexL2 + 1 >= (nRepeat || 3)) {
                                // L2 finished playing nRepeat times.
                                // Pause for a second and call Ended callback.
                                setTimeout(() => {
                                    audioRef.current?.pause();
                                    setWhichAudio({ isL1: true, audioIndexL2: 0 });
                                    onEnded();
                                }, 1000);
                                return;
                            }
                            // L2 finished playing.
                            // Pause for a second and play L1 sentence.
                            setTimeout(() => {
                                setWhichAudio((pre) => { return { isL1: true, audioIndexL2: pre.audioIndexL2 + 1 } });
                            }, 1000);
                        }
                    } />
            }
        </>
    );
}


export function SequentialAudioPlayer({ urls, nRepeat, onEnded: onEndedOuter, audioRef }: { urls: string[], nRepeat?: number, onEnded: () => void, audioRef: React.RefObject<HTMLAudioElement> }) {
    const [audioIndex, setAudioIndex] = React.useState(0);

    // Reset the audio player when the urls change
    React.useEffect(() => {
        setAudioIndex(0);
    }, [urls, setAudioIndex]);

    const onEnded = useCallback(() => {
        // Play the next audio
        // Pause for a second and call Ended callback.
        const hasEnded = audioIndex + 1 >= (nRepeat || 3);
        if (hasEnded) {
            // All audios finished playing nRepeat times.
            audioRef.current?.pause();
            onEndedOuter();
            setTimeout(() => {
                audioRef.current?.play().catch(console.error);
            }, 1000);
            return;
        }
        audioRef.current?.pause();
        setTimeout(() => {
            setAudioIndex((pre) => pre + 1);
            audioRef.current?.play().catch(console.error);
        }, 1000);
    }, [audioIndex, setAudioIndex, nRepeat, onEndedOuter, audioRef]);

    return (
        <>
            {/* Play audio */}
            {
                <audio ref={audioRef}
                    style={{ display: "none", width: "200px" }}
                    src={urls[audioIndex % urls.length]}
                    controls
                    onLoadedData={() => {
                        audioRef.current?.play().catch(console.error);
                    }}
                    onEnded={onEnded} />
            }
        </>
    );
}
