import React, { useState, useEffect } from 'react';
import './App.css'

function TranscriptionForm() {
  const [transcribing, setTranscribing] = useState(false);
  const [transcription, setTranscription] = useState('');

  const handleStartTranscription = () => {
    setTranscribing(true);
    setTranscription('');
  };

  const handleStopTranscription = () => {
    setTranscribing(false);
  };

  useEffect(() => {
    let recognition = null;

    if (transcribing) {
      recognition = new window.webkitSpeechRecognition(); // Create speech recognition object
      recognition.continuous = true; // Continuously listen for speech
      recognition.interimResults = true; // Get interim results as the user speaks

      recognition.onresult = (event) => {
        let finalTranscription = '';
        let interimTranscription = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const { transcript, isFinal } = event.results[i][0];
          if (isFinal) {
            finalTranscription += transcript + ' ';
          } else {
            interimTranscription += transcript + ' ';
          }
        }

        setTranscription(finalTranscription + interimTranscription);
      };

      recognition.start(); // Start speech recognition
    } else {
      if (recognition) {
        recognition.stop(); // Stop speech recognition
      }
    }

    return () => {
      if (recognition) {
        recognition.stop(); // Stop speech recognition when component unmounts
      }
    };
  }, [transcribing]);

  return (
    <div>
      <h1 className='title'>
        <strong>Real Time Voice Transcription  <span className='title-icon'>🎤</span></strong>
      </h1>
      <button className='btn btn1' onClick={handleStartTranscription} disabled={transcribing}>
        Start Transcription
      </button>
      <button className='btn' onClick={handleStopTranscription} disabled={!transcribing}>
        Stop Transcription
      </button>
      <h4>Transcript :</h4><hr/>
      <p className='transcript'>{transcription}</p>
    </div>
  );
}

export default TranscriptionForm;
