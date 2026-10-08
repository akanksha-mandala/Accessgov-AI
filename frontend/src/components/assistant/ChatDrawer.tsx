import React, {
  useState,
  useRef,
  useEffect,
} from 'react';

import {
  useConversation,
  ChatMessage,
} from '../../context/ConversationContext';

import {
  useAccessibility,
  SUPPORTED_LANGUAGES,
  LanguageCode,
} from '../../context/AccessibilityContext';

import {
  useNavigate,
  useLocation,
} from 'react-router-dom';

import {
  X,
  Send,
  Mic,
  Volume2,
  RotateCcw,
  Bot,
  ArrowRight,
} from 'lucide-react';

import { apiClient } from '../../services/apiClient';
import { speechService } from '../../services/speechService';

export const ChatDrawer: React.FC<{
  isOpen: boolean;
  onClose: () => void;
}> = ({ isOpen, onClose }) => {
  const {
    messages,
    addMessage,
    clearHistory,
    isStreaming,
    setIsStreaming,
  } = useConversation();

  const {
    selectedLanguage,
    setSelectedLanguage,
  } = useAccessibility();

  const [inputText, setInputText] =
    useState('');

  const [isRecording, setIsRecording] =
    useState(false);

  const [isPlayingAudio, setIsPlayingAudio] =
    useState<string | null>(null);

  const messagesEndRef =
    useRef<HTMLDivElement>(null);

  const currentAudioRef =
    useRef<HTMLAudioElement | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  const localeMap: Record<
    LanguageCode,
    string
  > = {
    en: 'en-IN',
    ta: 'ta-IN',
    te: 'te-IN',
    hi: 'hi-IN',
    kn: 'kn-IN',
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages]);

  /*
   * Stop backend TTS when the drawer closes.
   *
   * This does NOT affect the separate Voice Assistant.
   */
  useEffect(() => {
    if (!isOpen) {
      if (currentAudioRef.current) {
        speechService.stop(
          currentAudioRef.current
        );

        currentAudioRef.current = null;
      }

      setIsPlayingAudio(null);
    }
  }, [isOpen]);

  /*
   * Clean up audio when this component unmounts.
   */
  useEffect(() => {
    return () => {
      if (currentAudioRef.current) {
        speechService.stop(
          currentAudioRef.current
        );

        currentAudioRef.current = null;
      }
    };
  }, []);

  if (!isOpen) return null;

  const handleSend = async (
    overrideText?: string
  ) => {
    const textToSend = (
      overrideText ?? inputText
    ).trim();

    if (!textToSend) return;

    setInputText('');

    addMessage(
      'user',
      textToSend,
      selectedLanguage
    );

    setIsStreaming(true);

    /*
     * --------------------------------------------------
     * LOCAL LANGUAGE SWITCHING
     * --------------------------------------------------
     *
     * These commands do not call Gemini.
     * They also do not automatically speak.
     */

    const languageMatch = textToSend
      .toLowerCase()
      .match(
        /\b(?:speak|talk|reply|respond|answer|use|change(?: the)? language to)\s+(?:in\s+)?(english|tamil|telugu|hindi|kannada)\b/i
      );

    const bareLanguage = textToSend
      .toLowerCase()
      .trim()
      .match(
        /^(english|tamil|telugu|hindi|kannada)$/i
      );

    const requested =
      languageMatch?.[1] ||
      bareLanguage?.[1];

    const languageCodes: Record<
      string,
      LanguageCode
    > = {
      english: 'en',
      tamil: 'ta',
      telugu: 'te',
      hindi: 'hi',
      kannada: 'kn',
    };

    if (requested) {
      const nextLang =
        languageCodes[
          requested.toLowerCase()
        ];

      setSelectedLanguage(nextLang);

      const confirmations: Record<
        LanguageCode,
        string
      > = {
        en: 'Language changed to English. How can I help you?',
        ta: 'மொழி தமிழாக மாற்றப்பட்டது. நான் உங்களுக்கு எப்படி உதவலாம்?',
        te: 'భాష తెలుగుకు మార్చబడింది. నేను మీకు ఎలా సహాయం చేయగలను?',
        hi: 'भाषा हिंदी में बदल दी गई है। मैं आपकी कैसे सहायता कर सकता हूँ?',
        kn: 'ಭಾಷೆಯನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?',
      };

      addMessage(
        'assistant',
        confirmations[nextLang],
        nextLang
      );

      /*
       * No automatic speech.
       * User must click Speak.
       */

      setIsStreaming(false);
      return;
    }

    /*
     * --------------------------------------------------
     * BACKEND CHAT
     * --------------------------------------------------
     */

    try {
      const sessionId =
        localStorage.getItem(
          'accessgov_session_id'
        ) ||
        `session_${Date.now()}`;

      localStorage.setItem(
        'accessgov_session_id',
        sessionId
      );

      const res = await apiClient.post(
        '/conversation/chat',
        {
          message: textToSend,
          language: selectedLanguage,
          session_id: sessionId,
          page_context:
            location.pathname,
        }
      );

      const responseText = String(
        res.data.response || ''
      ).trim();

      if (!responseText) {
        throw new Error(
          'The assistant returned an empty response.'
        );
      }

      /*
       * Store the language with the message.
       *
       * Therefore a Telugu message remains Telugu
       * even if the global language is changed later.
       */
      addMessage(
        'assistant',
        responseText,
        selectedLanguage
      );

      /*
       * ------------------------------------------------
       * NAVIGATION
       * ------------------------------------------------
       */

      const intent =
        res.data.detected_intent;

      const suggested =
        res.data.suggested_service;

      if (
        intent === 'service_discovery' &&
        suggested?.service_id &&
        /\b(open|take me|go to|show)\b/i.test(
          textToSend
        )
      ) {
        onClose();

        navigate(
          `/services/${suggested.service_id}`
        );
      } else if (
        intent ===
          'document_requirements' &&
        /\b(show|open|take me|go to)\b/i.test(
          textToSend
        )
      ) {
        onClose();

        navigate('/documents');
      } else if (
        intent === 'eligibility_check' &&
        /\b(check|start|begin|evaluate)\b/i.test(
          textToSend
        )
      ) {
        onClose();

        navigate('/eligibility');
      }

      /*
       * NO AUTOMATIC SPEECH.
       *
       * The assistant remains silent until the
       * user explicitly presses Speak.
       */
    } catch (error: any) {
      console.error(
        'Chat request failed:',
        error
      );

      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        'The assistant could not process this request. Please try again.';

      addMessage(
        'assistant',
        errorMessage,
        selectedLanguage
      );
    } finally {
      setIsStreaming(false);
    }
  };

  /*
   * --------------------------------------------------
   * SPEECH INPUT
   * --------------------------------------------------
   */

  const handleSpeechInput = async () => {
    setIsRecording(true);

    try {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any)
          .webkitSpeechRecognition;

      if (!SpeechRecognition) {
        throw new Error(
          'Speech recognition is not supported by this browser.'
        );
      }

      const recognition =
        new SpeechRecognition();

      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.lang =
        localeMap[selectedLanguage];

      recognition.onresult = (
        event: any
      ) => {
        const transcript =
          event.results?.[0]?.[0]
            ?.transcript?.trim();

        setIsRecording(false);

        if (!transcript) return;

        setInputText(transcript);

        handleSend(transcript);
      };

      recognition.onerror = (
        event: any
      ) => {
        console.error(
          'Speech recognition error:',
          event
        );

        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.start();
    } catch (error) {
      console.error(
        'Speech input failed:',
        error
      );

      setIsRecording(false);
    }
  };

  /*
   * --------------------------------------------------
   * CLEAN TEXT FOR SPEECH
   * --------------------------------------------------
   */

  const cleanTextForSpeech = (
    text: string
  ): string => {
    return text
      .replace(/\*\*/g, '')
      .replace(/__/g, '')
      .replace(/`/g, '')
      .replace(
        /\\([\*_\`])/g,
        '$1'
      )
      .replace(
        /\[(.*?)\]\(.*?\)/g,
        '$1'
      )
      .replace(
        /^\s*[-*]\s+/gm,
        ''
      )
      .replace(
        /^\s*\d+\.\s+/gm,
        (match) => {
          const number =
            match.match(/\d+/)?.[0] ||
            '';

          return `${number}. `;
        }
      )
      .replace(/\s+/g, ' ')
      .trim();
  };

  /*
   * --------------------------------------------------
   * MANUAL CHATBOT SPEAK BUTTON
   * --------------------------------------------------
   *
   * IMPORTANT:
   *
   * This uses the backend /speech/tts endpoint.
   *
   * It does NOT use browser speechSynthesis.
   *
   * Therefore setting te-IN/ta-IN/etc. is handled
   * by the backend TTS implementation rather than
   * depending on installed Chrome voices.
   */

  const handlePlayTTS = async (
    text: string,
    msgId: string,
    messageLanguage?: LanguageCode
  ) => {
    if (!text.trim()) return;

    const language =
      messageLanguage ||
      selectedLanguage;

    const speechText =
      cleanTextForSpeech(text);

    if (!speechText) return;

    /*
     * Stop currently playing chatbot audio.
     */
    if (currentAudioRef.current) {
      speechService.stop(
        currentAudioRef.current
      );

      currentAudioRef.current = null;
    }

    /*
     * Clicking the same active Speak button
     * again simply stops it.
     */
    if (isPlayingAudio === msgId) {
      setIsPlayingAudio(null);
      return;
    }

    setIsPlayingAudio(msgId);

    try {
      const audio =
        await speechService.speak(
          speechText,
          language
        );

      if (!audio) {
        console.error(
          `Chatbot TTS failed for language: ${language}`
        );

        setIsPlayingAudio(null);
        return;
      }

      currentAudioRef.current = audio;

      /*
       * speechService already handles URL cleanup.
       * We only listen for completion so the UI can
       * remove "Speaking..." state.
       */
      audio.addEventListener(
        'ended',
        () => {
          if (
            currentAudioRef.current ===
            audio
          ) {
            currentAudioRef.current = null;
            setIsPlayingAudio(null);
          }
        },
        { once: true }
      );

      audio.addEventListener(
        'error',
        () => {
          if (
            currentAudioRef.current ===
            audio
          ) {
            currentAudioRef.current = null;
            setIsPlayingAudio(null);
          }
        },
        { once: true }
      );

      console.log(
        `AccessGov chatbot TTS: ${language} (${localeMap[language]})`
      );
    } catch (error) {
      console.error(
        'Chatbot TTS playback failed:',
        error
      );

      currentAudioRef.current = null;
      setIsPlayingAudio(null);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 bg-white shadow-2xl border-l-2 border-gov-gold flex flex-col">

      {/* Header */}
      <div className="bg-gov-blue text-white p-4 flex items-center justify-between border-b-2 border-gov-gold">

        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gov-gold text-slate-900 rounded-full flex items-center justify-center font-bold">
            🤖
          </div>

          <div>
            <h3 className="font-bold text-xs sm:text-sm">
              AccessGov AI Assistant
            </h3>

            <p className="text-[10px] text-slate-200">
              Multilingual Public Service Agent
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5">

          <select
            value={selectedLanguage}
            onChange={(e) =>
              setSelectedLanguage(
                e.target
                  .value as LanguageCode
              )
            }
            className="bg-blue-900 text-white text-[11px] p-1 rounded border border-blue-700 focus:outline-none"
          >
            {SUPPORTED_LANGUAGES.map(
              (language) => (
                <option
                  key={language.code}
                  value={language.code}
                >
                  {language.nativeLabel}
                </option>
              )
            )}
          </select>

          <button
            onClick={clearHistory}
            title="Reset Chat"
            className="p-1 hover:bg-blue-800 rounded"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-200" />
          </button>

          <button
            onClick={onClose}
            title="Close Assistant"
            className="p-1 hover:bg-blue-800 rounded"
          >
            <X className="w-3.5 h-3.5 text-slate-200" />
          </button>

        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50">

        {messages.map(
          (msg: ChatMessage) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.sender === 'user'
                  ? 'justify-end'
                  : 'justify-start'
              }`}
            >

              <div
                className={`max-w-[85%] rounded-xl p-3 text-xs shadow-sm relative space-y-2 ${
                  msg.sender === 'user'
                    ? 'bg-gov-blue text-white rounded-br-none'
                    : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'
                }`}
              >

                <div className="flex items-center justify-between text-[10px] opacity-75">

                  <span className="font-semibold">
                    {msg.sender ===
                    'user'
                      ? 'You'
                      : 'AccessGov AI'}
                  </span>

                  <span>
                    {msg.timestamp}
                  </span>

                </div>

                <p className="leading-relaxed whitespace-pre-wrap">
                  {msg.text}
                </p>

                {/* Assistant controls */}
                {msg.sender ===
                  'assistant' && (
                  <div className="pt-2 border-t border-slate-100 flex flex-wrap gap-1.5">

                    <button
                      onClick={() =>
                        handlePlayTTS(
                          msg.text,
                          msg.id,
                          msg.language as
                            | LanguageCode
                            | undefined
                        )
                      }
                      className={`text-[10px] px-2 py-1 rounded font-semibold flex items-center ${
                        isPlayingAudio ===
                        msg.id
                          ? 'bg-gov-blue text-white'
                          : 'bg-slate-100 hover:bg-slate-200 text-gov-blue'
                      }`}
                    >
                      <Volume2 className="w-3 h-3 mr-1 text-gov-gold" />

                      {isPlayingAudio ===
                      msg.id
                        ? 'Speaking...'
                        : 'Speak'}
                    </button>

                    <button
                      onClick={() => {
                        onClose();

                        navigate(
                          '/eligibility'
                        );
                      }}
                      className="text-[10px] bg-blue-50 hover:bg-blue-100 text-gov-blue px-2 py-1 rounded font-semibold flex items-center"
                    >
                      Check Eligibility

                      <ArrowRight className="w-3 h-3 ml-1" />
                    </button>

                    <button
                      onClick={() => {
                        onClose();

                        navigate(
                          '/documents'
                        );
                      }}
                      className="text-[10px] bg-emerald-50 hover:bg-emerald-100 text-emerald-700 px-2 py-1 rounded font-semibold flex items-center"
                    >
                      Upload Document
                    </button>

                  </div>
                )}

              </div>
            </div>
          )
        )}

        {isStreaming && (
          <div className="flex items-center space-x-2 text-xs text-slate-500 bg-white p-2.5 rounded-lg border border-slate-200 max-w-[70%]">

            <Bot className="w-4 h-4 text-gov-blue animate-bounce" />

            <span>
              Formulating answer...
            </span>

          </div>
        )}

        <div ref={messagesEndRef} />

      </div>

      {/* Quick actions */}
      <div className="px-3 py-2 bg-slate-100 border-t border-slate-200 flex overflow-x-auto space-x-1.5 text-[11px]">

        <button
          onClick={() =>
            handleSend(
              'Scholarship Assistance'
            )
          }
          className="px-2 py-1 bg-white border border-slate-300 rounded hover:bg-blue-50 hover:border-gov-blue text-slate-700 font-medium shrink-0"
        >
          🎓 Scholarship
        </button>

        <button
          onClick={() =>
            handleSend(
              'Income Certificate'
            )
          }
          className="px-2 py-1 bg-white border border-slate-300 rounded hover:bg-blue-50 hover:border-gov-blue text-slate-700 font-medium shrink-0"
        >
          📜 Income Cert
        </button>

        <button
          onClick={() =>
            handleSend(
              'Am I eligible?'
            )
          }
          className="px-2 py-1 bg-white border border-slate-300 rounded hover:bg-blue-50 hover:border-gov-blue text-slate-700 font-medium shrink-0"
        >
          ✓ Eligibility
        </button>

      </div>

      {/* Input */}
      <div className="p-3 bg-white border-t border-slate-200 flex items-center space-x-2">

        <button
          onClick={handleSpeechInput}
          className={`p-2 rounded-full transition ${
            isRecording
              ? 'bg-red-600 text-white animate-pulse'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
          title="Voice Speech Input"
          aria-label="Activate voice speech input"
        >
          <Mic className="w-4 h-4" />
        </button>

        <input
          type="text"
          value={inputText}
          onChange={(e) =>
            setInputText(e.target.value)
          }
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSend();
            }
          }}
          placeholder="Ask about scholarship, income certificate..."
          className="flex-1 text-xs border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:border-gov-blue"
        />

        <button
          onClick={() => handleSend()}
          disabled={!inputText.trim()}
          className="p-2 bg-gov-blue text-white rounded-md hover:bg-blue-900 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>

      </div>

    </div>
  );
};

export default ChatDrawer;
