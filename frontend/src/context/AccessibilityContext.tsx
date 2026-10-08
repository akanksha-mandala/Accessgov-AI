import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from 'react';

import { apiClient } from '../services/apiClient';
import { speechService } from '../services/speechService';

export type LanguageCode =
  | 'en'
  | 'ta'
  | 'te'
  | 'hi'
  | 'kn';

export interface LanguageOption {
  code: LanguageCode;
  label: string;
  nativeLabel: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  {
    code: 'en',
    label: 'English',
    nativeLabel: 'English',
  },
  {
    code: 'ta',
    label: 'Tamil',
    nativeLabel: 'தமிழ்',
  },
  {
    code: 'te',
    label: 'Telugu',
    nativeLabel: 'తెలుగు',
  },
  {
    code: 'hi',
    label: 'Hindi',
    nativeLabel: 'हिंदी',
  },
  {
    code: 'kn',
    label: 'Kannada',
    nativeLabel: 'ಕನ್ನಡ',
  },
];

interface AccessibilityContextType {
  fontScale: number;
  setFontScale: (scale: number) => void;

  highContrast: boolean;
  setHighContrast: (contrast: boolean) => void;

  screenReaderEnabled: boolean;
  setScreenReaderEnabled: (enabled: boolean) => void;

  voiceAccessEnabled: boolean;
  setVoiceAccessEnabled: (enabled: boolean) => void;

  speakResponsesAloud: boolean;
  setSpeakResponsesAloud: (speak: boolean) => void;

  selectedLanguage: LanguageCode;
  setSelectedLanguage: (lang: LanguageCode) => void;

  announcement: string;
  speakAnnouncement: (text: string) => void;

  readPageContentAloud: () => void;

  stopSpeaking: () => void;
  stopPageReading: () => void;

  isSpeaking: boolean;

  resetAccessibility: () => void;
}

const AccessibilityContext =
  createContext<AccessibilityContextType | undefined>(
    undefined
  );

const SPEECH_LANGUAGES: Record<LanguageCode, string> = {
  en: 'en-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  hi: 'hi-IN',
  kn: 'kn-IN',
};

export const AccessibilityProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [fontScale, setFontScaleState] =
    useState<number>(() => {
      const saved = localStorage.getItem(
        'accessgov_font_scale'
      );

      return saved ? parseInt(saved, 10) : 100;
    });

  const [highContrast, setHighContrastState] =
    useState<boolean>(() => {
      return (
        localStorage.getItem(
          'accessgov_high_contrast'
        ) === 'true'
      );
    });

  const [
    screenReaderEnabled,
    setScreenReaderEnabledState,
  ] = useState<boolean>(() => {
    return (
      localStorage.getItem(
        'accessgov_screen_reader'
      ) === 'true'
    );
  });

  const [
    voiceAccessEnabled,
    setVoiceAccessEnabledState,
  ] = useState<boolean>(() => {
    return (
      localStorage.getItem(
        'accessgov_voice_access'
      ) === 'true'
    );
  });

  const [
    speakResponsesAloud,
    setSpeakResponsesAloudState,
  ] = useState<boolean>(() => {
    return (
      localStorage.getItem(
        'accessgov_speak_responses'
      ) === 'true'
    );
  });

  const [
    selectedLanguage,
    setSelectedLanguageState,
  ] = useState<LanguageCode>(() => {
    const saved =
      localStorage.getItem(
        'accessgov_language'
      ) as LanguageCode | null;

    if (
      saved === 'en' ||
      saved === 'ta' ||
      saved === 'te' ||
      saved === 'hi' ||
      saved === 'kn'
    ) {
      return saved;
    }

    return 'en';
  });

  const [announcement, setAnnouncement] =
    useState<string>('');

  const [isSpeaking, setIsSpeaking] =
    useState<boolean>(false);

  /**
   * Page Reader has its own audio instance.
   * It is separate from Voice Assistant speech.
   */
  const pageReaderAudioRef =
    useRef<HTMLAudioElement | null>(null);

  /**
   * Every Read Page request gets a new ID.
   * This prevents an older translation/TTS request
   * from playing after navigation or Stop.
   */
  const pageReaderRequestRef =
    useRef<number>(0);

  /**
   * Tracks the last browser route seen by the
   * accessibility provider.
   *
   * This lets us detect React Router navigation
   * without requiring changes to VoiceAccessBar.
   */
  const lastPathRef =
    useRef<string>(
      window.location.pathname
    );

  /**
   * Prevents multiple automatic Page Reader
   * calls for the same navigation.
   */
  const autoReadTimerRef =
    useRef<number | null>(null);

  useEffect(() => {
    localStorage.setItem(
      'accessgov_font_scale',
      fontScale.toString()
    );

    document.documentElement.style.fontSize =
      `${fontScale}%`;
  }, [fontScale]);

  useEffect(() => {
    localStorage.setItem(
      'accessgov_high_contrast',
      highContrast.toString()
    );

    if (highContrast) {
      document.body.classList.add(
        'high-contrast'
      );
    } else {
      document.body.classList.remove(
        'high-contrast'
      );
    }
  }, [highContrast]);

  useEffect(() => {
    localStorage.setItem(
      'accessgov_screen_reader',
      screenReaderEnabled.toString()
    );
  }, [screenReaderEnabled]);

  useEffect(() => {
    localStorage.setItem(
      'accessgov_voice_access',
      voiceAccessEnabled.toString()
    );
  }, [voiceAccessEnabled]);

  useEffect(() => {
    localStorage.setItem(
      'accessgov_speak_responses',
      speakResponsesAloud.toString()
    );
  }, [speakResponsesAloud]);

  useEffect(() => {
    localStorage.setItem(
      'accessgov_language',
      selectedLanguage
    );
  }, [selectedLanguage]);

  const logTelemetry = useCallback(
    async (
      eventType: string,
      details?: Record<string, any>
    ) => {
      try {
        await apiClient.post(
          '/accessibility/event',
          {
            event_type: eventType,
            font_scale: fontScale,
            contrast_mode: highContrast
              ? 'high-contrast'
              : 'normal',
            screen_reader_enabled:
              screenReaderEnabled,
            ...(details || {}),
          }
        );
      } catch {
        // Accessibility telemetry is non-critical.
      }
    },
    [
      fontScale,
      highContrast,
      screenReaderEnabled,
    ]
  );

  /**
   * Generic announcement speech.
   *
   * Voice Assistant continues using this function.
   * It is NOT automatically triggered by ordinary
   * page navigation.
   */
  const speakAnnouncement =
    useCallback(
      (text: string) => {
        const cleanText = text
          .replace(/\s+/g, ' ')
          .trim();

        if (!cleanText) {
          return;
        }

        setAnnouncement(cleanText);

        if (
          !('speechSynthesis' in window)
        ) {
          return;
        }

        window.speechSynthesis.cancel();

        const utterance =
          new SpeechSynthesisUtterance(
            cleanText
          );

        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        utterance.lang =
          SPEECH_LANGUAGES[
            selectedLanguage
          ] || 'en-IN';

        utterance.onstart = () => {
          setIsSpeaking(true);
        };

        utterance.onend = () => {
          setIsSpeaking(false);
        };

        utterance.onerror = () => {
          setIsSpeaking(false);
        };

        window.speechSynthesis.speak(
          utterance
        );
      },
      [selectedLanguage]
    );

  /**
   * Stop browser speech.
   *
   * This is kept separate from Page Reader audio.
   */
  const stopSpeaking = useCallback(
    () => {
      if (
        'speechSynthesis' in window
      ) {
        window.speechSynthesis.cancel();
      }

      setIsSpeaking(false);
    },
    []
  );

  /**
   * Stop ONLY Page Reader.
   */
  const stopPageReading = useCallback(
    () => {
      pageReaderRequestRef.current += 1;

      if (
        pageReaderAudioRef.current
      ) {
        speechService.stop(
          pageReaderAudioRef.current
        );

        pageReaderAudioRef.current =
          null;
      }

      setIsSpeaking(false);
    },
    []
  );

  /**
   * Read the currently visible page.
   *
   * This can be triggered manually by the
   * Read Page button OR automatically after
   * Voice Assistant navigation.
   */
  const readPageContentAloud =
    useCallback(async () => {
      logTelemetry('read_page');

      /**
       * Stop existing Page Reader playback.
       */
      if (
        pageReaderAudioRef.current
      ) {
        speechService.stop(
          pageReaderAudioRef.current
        );

        pageReaderAudioRef.current =
          null;
      }

      /**
       * Invalidate previous asynchronous work.
       */
      const requestId =
        ++pageReaderRequestRef.current;

      /**
       * Give React Router/page components time
       * to finish rendering.
       */
      await new Promise<void>(
        (resolve) => {
          window.setTimeout(
            resolve,
            300
          );
        }
      );

      if (
        requestId !==
        pageReaderRequestRef.current
      ) {
        return;
      }

      /**
       * Prefer explicitly marked readable page.
       */
      const markedPage =
        document.querySelector(
          '[data-speech-page="true"]'
        );

      const mainElem =
        markedPage ||
        document.querySelector('main');

      /**
       * Fallback when no readable page exists.
       */
      if (!mainElem) {
        const fallback =
          'AccessGov AI Public Service Portal.';

        setAnnouncement(fallback);

        const audio =
          await speechService.speak(
            fallback,
            SPEECH_LANGUAGES[
              selectedLanguage
            ]
          );

        if (
          requestId !==
          pageReaderRequestRef.current
        ) {
          if (audio) {
            speechService.stop(audio);
          }

          return;
        }

        pageReaderAudioRef.current =
          audio;

        if (audio) {
          setIsSpeaking(true);

          audio.onended = () => {
            if (
              pageReaderAudioRef.current ===
              audio
            ) {
              pageReaderAudioRef.current =
                null;

              setIsSpeaking(false);
            }
          };
        }

        return;
      }

      /**
       * Clone the page so the real DOM is never modified.
       */
      const cloned =
        mainElem.cloneNode(
          true
        ) as HTMLElement;

      /**
       * Remove controls and elements that
       * should never be spoken.
       */
      const elementsToRemove =
        cloned.querySelectorAll(
          [
            'script',
            'style',
            'svg',
            'noscript',
            'button',
            'input',
            'textarea',
            'select',
            'option',
            'a',
            '[aria-hidden="true"]',
            '.sr-only',
            '[data-speech-ignore="true"]',
          ].join(',')
        );

      elementsToRemove.forEach(
        (element) => {
          element.remove();
        }
      );

      /**
       * Extract visible text.
       */
      const pageText =
        cloned.innerText
          .replace(/\s+/g, ' ')
          .trim();

      /**
       * Keep Page Reader output reasonably sized.
       */
      const readableText =
        pageText.slice(0, 2500);

      if (!readableText) {
        setAnnouncement(
          'AccessGov AI Portal. There is no readable page content available.'
        );

        return;
      }

      let textToSpeak =
        readableText;

      /**
       * Translate actual page content when
       * a non-English language is selected.
       */
      if (
        selectedLanguage !== 'en'
      ) {
        try {
          const response =
            await apiClient.post(
              '/services/translate',
              {
                text: readableText,
                source_language: 'en',
                target_language:
                  selectedLanguage,
              }
            );

          if (
            requestId !==
            pageReaderRequestRef.current
          ) {
            return;
          }

          const translated =
            response.data?.text;

          if (
            typeof translated ===
              'string' &&
            translated.trim()
          ) {
            textToSpeak =
              translated.trim();
          }
        } catch (error) {
          console.error(
            'Page translation failed:',
            error
          );

          /**
           * Do not pretend English is the
           * selected language when translation fails.
           */
          setIsSpeaking(false);

          return;
        }
      }

      if (
        requestId !==
        pageReaderRequestRef.current
      ) {
        return;
      }

      setAnnouncement(
        textToSpeak
      );

      /**
       * Backend TTS uses the selected language.
       */
      const audio =
        await speechService.speak(
          textToSpeak,
          SPEECH_LANGUAGES[
            selectedLanguage
          ]
        );

      if (
        requestId !==
        pageReaderRequestRef.current
      ) {
        if (audio) {
          speechService.stop(audio);
        }

        return;
      }

      if (!audio) {
        setIsSpeaking(false);
        return;
      }

      pageReaderAudioRef.current =
        audio;

      setIsSpeaking(true);

      audio.onended = () => {
        if (
          pageReaderAudioRef.current ===
          audio
        ) {
          pageReaderAudioRef.current =
            null;

          setIsSpeaking(false);
        }
      };
    }, [
      logTelemetry,
      selectedLanguage,
    ]);

  /**
   * =====================================================
   * AUTOMATIC PAGE READING AFTER VOICE NAVIGATION
   * =====================================================
   *
   * When Voice Assistant is enabled, watch for route
   * changes. React Router's programmatic navigation does
   * not always emit a native popstate event, so a small
   * pathname check is used instead.
   *
   * Voice Assistant OFF:
   *     No automatic reading.
   *
   * Voice Assistant ON:
   *     Route changes -> wait for page render ->
   *     automatically read the new page.
   */
  useEffect(() => {
    if (!voiceAccessEnabled) {
      return;
    }

    const checkForNavigation = () => {
      const currentPath =
        window.location.pathname;

      if (
        currentPath ===
        lastPathRef.current
      ) {
        return;
      }

      lastPathRef.current =
        currentPath;

      /**
       * Stop previous Page Reader audio before
       * reading the newly navigated page.
       */
      stopPageReading();

      /**
       * Give React Router and the destination
       * component enough time to render.
       */
      if (
        autoReadTimerRef.current !== null
      ) {
        window.clearTimeout(
          autoReadTimerRef.current
        );
      }

      autoReadTimerRef.current =
        window.setTimeout(() => {
          readPageContentAloud();
        }, 700);
    };

    /**
     * Polling is intentional here because it catches
     * React Router navigate()/pushState navigation too.
     */
    const intervalId =
      window.setInterval(
        checkForNavigation,
        250
      );

    return () => {
      window.clearInterval(
        intervalId
      );

      if (
        autoReadTimerRef.current !== null
      ) {
        window.clearTimeout(
          autoReadTimerRef.current
        );

        autoReadTimerRef.current =
          null;
      }
    };
  }, [
    voiceAccessEnabled,
    readPageContentAloud,
    stopPageReading,
  ]);

  const setFontScale = (
    scale: number
  ) => {
    setFontScaleState(scale);

    logTelemetry(
      'font_scale_change',
      {
        scale,
      }
    );
  };

  const setHighContrast = (
    contrast: boolean
  ) => {
    setHighContrastState(
      contrast
    );

    logTelemetry(
      'contrast_toggle',
      {
        contrast,
      }
    );
  };

  const setScreenReaderEnabled = (
    enabled: boolean
  ) => {
    setScreenReaderEnabledState(
      enabled
    );

    logTelemetry(
      'screen_reader_toggle',
      {
        enabled,
      }
    );
  };

  const setVoiceAccessEnabled = (
    enabled: boolean
  ) => {
    setVoiceAccessEnabledState(
      enabled
    );

    logTelemetry(
      'voice_access_toggle',
      {
        enabled,
      }
    );

    if (!enabled) {
      stopSpeaking();
      stopPageReading();

      if (
        autoReadTimerRef.current !== null
      ) {
        window.clearTimeout(
          autoReadTimerRef.current
        );

        autoReadTimerRef.current =
          null;
      }
    }
  };

  const setSpeakResponsesAloud = (
    speak: boolean
  ) => {
    setSpeakResponsesAloudState(
      speak
    );

    logTelemetry(
      'speech_output_toggle',
      {
        enabled: speak,
      }
    );

    if (!speak) {
      stopSpeaking();
    }
  };

  const setSelectedLanguage = (
    lang: LanguageCode
  ) => {
    setSelectedLanguageState(
      lang
    );

    logTelemetry(
      'language_change',
      {
        lang,
      }
    );
  };

  const resetAccessibility =
    () => {
      setFontScaleState(100);
      setHighContrastState(false);
      setScreenReaderEnabledState(
        false
      );
      setVoiceAccessEnabledState(
        false
      );
      setSpeakResponsesAloudState(
        false
      );
      setSelectedLanguageState(
        'en'
      );

      stopPageReading();
      stopSpeaking();

      logTelemetry(
        'accessibility_reset'
      );
    };

  return (
    <AccessibilityContext.Provider
      value={{
        fontScale,
        setFontScale,

        highContrast,
        setHighContrast,

        screenReaderEnabled,
        setScreenReaderEnabled,

        voiceAccessEnabled,
        setVoiceAccessEnabled,

        speakResponsesAloud,
        setSpeakResponsesAloud,

        selectedLanguage,
        setSelectedLanguage,

        announcement,
        speakAnnouncement,

        readPageContentAloud,

        stopSpeaking,
        stopPageReading,

        isSpeaking,

        resetAccessibility,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility =
  () => {
    const context = useContext(
      AccessibilityContext
    );

    if (!context) {
      throw new Error(
        'useAccessibility must be used within AccessibilityProvider'
      );
    }

    return context;
  };