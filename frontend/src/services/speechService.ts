import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api/v1';

const LANGUAGE_LOCALE_MAP: Record<string, string> = {
  en: 'en-IN',
  'en-IN': 'en-IN',

  ta: 'ta-IN',
  'ta-IN': 'ta-IN',

  te: 'te-IN',
  'te-IN': 'te-IN',

  hi: 'hi-IN',
  'hi-IN': 'hi-IN',

  kn: 'kn-IN',
  'kn-IN': 'kn-IN',
};

const normalizeLanguage = (language: string): string => {
  return (
    LANGUAGE_LOCALE_MAP[language] ||
    language ||
    'en-IN'
  );
};

export const speechService = {
  /**
   * Convert speech audio into text.
   */
  async transcribeAudio(
    file: File,
    language: string = 'en-IN'
  ): Promise<string> {
    try {
      const formData = new FormData();

      formData.append('file', file);
      formData.append(
        'language',
        normalizeLanguage(language)
      );

      const response = await axios.post(
        `${API_BASE_URL}/speech/stt`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data.transcript || '';
    } catch (error) {
      console.error(
        'Speech transcription failed:',
        error
      );

      return '';
    }
  },

  /**
   * Generate speech audio from text.
   *
   * This uses the AccessGov backend TTS endpoint.
   * It does NOT depend on Chrome's installed voices.
   */
  async synthesizeSpeech(
    text: string,
    language: string = 'en-IN'
  ): Promise<string> {
    if (!text.trim()) {
      return '';
    }

    try {
      const normalizedLanguage =
        normalizeLanguage(language);

      const response = await axios.post(
        `${API_BASE_URL}/speech/tts`,
        {
          text,
          language: normalizedLanguage,
        },
        {
          responseType: 'blob',
        }
      );

      if (
        !response.data ||
        response.data.size === 0
      ) {
        console.error(
          'TTS returned an empty audio response.'
        );

        return '';
      }

      return URL.createObjectURL(
        response.data
      );
    } catch (error) {
      console.error(
        'Speech synthesis failed:',
        error
      );

      return '';
    }
  },

  /**
   * Generate and immediately play speech.
   *
   * Returns the HTMLAudioElement so the caller
   * can stop playback when required.
   */
  async speak(
    text: string,
    language: string = 'en-IN'
  ): Promise<HTMLAudioElement | null> {
    if (!text.trim()) {
      return null;
    }

    try {
      const audioUrl =
        await this.synthesizeSpeech(
          text,
          language
        );

      if (!audioUrl) {
        return null;
      }

      const audio =
        new Audio(audioUrl);

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();

      return audio;
    } catch (error) {
      console.error(
        'Audio playback failed:',
        error
      );

      return null;
    }
  },

  /**
   * Stop an audio element returned by speak().
   */
  stop(
    audio: HTMLAudioElement | null
  ) {
    if (!audio) {
      return;
    }

    try {
      audio.pause();
      audio.currentTime = 0;

      if (audio.src.startsWith('blob:')) {
        URL.revokeObjectURL(audio.src);
      }
    } catch (error) {
      console.error(
        'Unable to stop speech:',
        error
      );
    }
  },

  /**
   * Convert the global language code into
   * the backend TTS locale.
   */
  getLocale(
    language: string
  ): string {
    return normalizeLanguage(language);
  },
};