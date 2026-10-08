import React, { useEffect, useRef, useState } from 'react';
import {
  useAccessibility,
  LanguageCode,
} from '../../context/AccessibilityContext';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../../services/apiClient';
import {
  servicesService,
  ALL_CURATED_SERVICES,
  GovernmentService,
} from '../../services/servicesService';
import {
  Mic,
  MicOff,
  Volume2,
  Square,
  HelpCircle,
  AlertCircle,
} from 'lucide-react';

export const VoiceAccessBar: React.FC = () => {
  const {
    voiceAccessEnabled,
    setVoiceAccessEnabled,
    speakAnnouncement,
    stopSpeaking,
    stopPageReading,
    isSpeaking,
    setSelectedLanguage,
    selectedLanguage,
    readPageContentAloud,
  } = useAccessibility();

  const navigate = useNavigate();

  const recognitionRef = useRef<any>(null);
  const activeRef = useRef(false);
  const busyRef = useRef(false);

  const [isListening, setIsListening] = useState(false);
  const [lastCommand, setLastCommand] = useState('');
  const [permissionError, setPermissionError] = useState('');
  const [showHelp, setShowHelp] = useState(false);

  const langMap: Record<LanguageCode, string> = {
    en: 'en-IN',
    ta: 'ta-IN',
    te: 'te-IN',
    hi: 'hi-IN',
    kn: 'kn-IN',
  };

  const VOICE_TEXT: Record<
    LanguageCode,
    {
      home: string;
      servicesOpened: string;
      noServices: string;
      servicePrompt: string;
      applicationStatus: string;
      applications: string;
      documents: string;
      eligibility: string;
      back: string;
      languageReady: string;
      unknown: string;
      backendError: string;
      help: string;
      stopHelp: string;
      pageOpened: string;
      serviceOpened: string;
      sayEligibility: string;
      sayDocuments: string;
      sayApplications: string;
      sayBack: string;
    }
  > = {
    en: {
      home: 'Home dashboard opened.',
      servicesOpened: 'Services page opened.',
      noServices:
        'Services page opened. There are currently no government services available.',
      servicePrompt:
        'Say the name of a service to open it. Say stop to stop voice access.',
      applicationStatus: 'Application Status page opened.',
      applications: 'My Applications page opened.',
      documents: 'Documents page opened.',
      eligibility: 'Eligibility Checker opened.',
      back: 'Returned to the previous page.',
      languageReady:
        'Language changed to English. I am ready.',
      unknown:
        'I could not find an answer for that request.',
      backendError:
        'The voice assistant could not reach the backend.',
      help:
        'You can say Services, Scholarship, Income Certificate, Health Insurance, PM Kisan, Housing, Pension, RTE, Community Certificate, Applications, Documents, Eligibility, Read Page, Home, Back, Stop Reading, or Stop.',
      stopHelp:
        'Say stop to stop voice access. Say stop reading to stop only page reading.',
      pageOpened: 'page opened.',
      serviceOpened: 'opened.',
      sayEligibility:
        'Say eligibility to start the eligibility check,',
      sayDocuments:
        'say documents to hear the required documents again,',
      sayApplications:
        'say applications to open My Applications,',
      sayBack:
        'or say back to return to Services.',
    },

    ta: {
      home: 'முகப்புப் பலகை திறக்கப்பட்டது.',
      servicesOpened: 'அரசு சேவைகள் பக்கம் திறக்கப்பட்டது.',
      noServices:
        'அரசு சேவைகள் பக்கம் திறக்கப்பட்டது. தற்போது அரசு சேவைகள் எதுவும் இல்லை.',
      servicePrompt:
        'ஒரு சேவையைத் திறக்க அதன் பெயரைச் சொல்லுங்கள். குரல் அணுகலை நிறுத்த நிறுத்து என்று சொல்லுங்கள்.',
      applicationStatus:
        'விண்ணப்ப நிலைப் பக்கம் திறக்கப்பட்டது.',
      applications:
        'எனது விண்ணப்பங்கள் பக்கம் திறக்கப்பட்டது.',
      documents: 'ஆவணங்கள் பக்கம் திறக்கப்பட்டது.',
      eligibility:
        'தகுதி சரிபார்ப்பு பக்கம் திறக்கப்பட்டது.',
      back: 'முந்தைய பக்கத்திற்குத் திரும்பிவிட்டோம்.',
      languageReady:
        'மொழி தமிழாக மாற்றப்பட்டது. நான் தயாராக இருக்கிறேன்.',
      unknown:
        'அந்த கோரிக்கைக்கான பதிலை என்னால் கண்டறிய முடியவில்லை.',
      backendError:
        'குரல் உதவியாளரால் சேவையகத்தை அணுக முடியவில்லை.',
      help:
        'சேவைகள், உதவித்தொகை, வருமானச் சான்றிதழ், மருத்துவக் காப்பீடு, பிஎம் கிசான், வீட்டுவசதி, ஓய்வூதியம், ஆர்டிஇ, சமூகச் சான்றிதழ், விண்ணப்பங்கள், ஆவணங்கள், தகுதி, பக்கத்தைப் படி, முகப்பு, பின் செல், படிப்பதை நிறுத்து அல்லது நிறுத்து என்று சொல்லலாம்.',
      stopHelp:
        'குரல் அணுகலை நிறுத்த நிறுத்து என்று சொல்லுங்கள். பக்கத்தை மட்டும் நிறுத்த படிப்பதை நிறுத்து என்று சொல்லுங்கள்.',
      pageOpened: 'பக்கம் திறக்கப்பட்டது.',
      serviceOpened: 'திறக்கப்பட்டது.',
      sayEligibility:
        'தகுதி சரிபார்ப்பைத் தொடங்க தகுதி என்று சொல்லுங்கள்,',
      sayDocuments:
        'தேவையான ஆவணங்களை மீண்டும் கேட்க ஆவணங்கள் என்று சொல்லுங்கள்,',
      sayApplications:
        'எனது விண்ணப்பங்களைத் திறக்க விண்ணப்பங்கள் என்று சொல்லுங்கள்,',
      sayBack:
        'அல்லது சேவைகள் பக்கத்திற்குத் திரும்ப பின் செல் என்று சொல்லுங்கள்.',
    },

    te: {
      home: 'హోమ్ డాష్‌బోర్డ్ తెరవబడింది.',
      servicesOpened: 'ప్రభుత్వ సేవల పేజీ తెరవబడింది.',
      noServices:
        'ప్రభుత్వ సేవల పేజీ తెరవబడింది. ప్రస్తుతం ప్రభుత్వ సేవలు అందుబాటులో లేవు.',
      servicePrompt:
        'సేవను తెరవడానికి దాని పేరును చెప్పండి. వాయిస్ యాక్సెస్‌ను ఆపడానికి ఆపండి అని చెప్పండి.',
      applicationStatus:
        'దరఖాస్తు స్థితి పేజీ తెరవబడింది.',
      applications:
        'నా దరఖాస్తుల పేజీ తెరవబడింది.',
      documents: 'పత్రాల పేజీ తెరవబడింది.',
      eligibility:
        'అర్హత తనిఖీ పేజీ తెరవబడింది.',
      back: 'మునుపటి పేజీకి తిరిగి వెళ్లాము.',
      languageReady:
        'భాష తెలుగుకు మార్చబడింది. నేను సిద్ధంగా ఉన్నాను.',
      unknown:
        'ఆ అభ్యర్థనకు సమాధానాన్ని కనుగొనలేకపోయాను.',
      backendError:
        'వాయిస్ అసిస్టెంట్ బ్యాక్‌ఎండ్‌ను చేరుకోలేకపోయింది.',
      help:
        'సేవలు, విద్యార్థి వేతనం, ఆదాయ ధృవీకరణ పత్రం, ఆరోగ్య బీమా, పీఎం కిసాన్, గృహం, పెన్షన్, ఆర్‌టీఈ, కమ్యూనిటీ సర్టిఫికేట్, దరఖాస్తులు, పత్రాలు, అర్హత, పేజీ చదువు, హోమ్, వెనక్కి, చదవడం ఆపు లేదా ఆపండి అని చెప్పవచ్చు.',
      stopHelp:
        'వాయిస్ యాక్సెస్‌ను ఆపడానికి ఆపండి అని చెప్పండి. పేజీ చదవడాన్ని మాత్రమే ఆపడానికి చదవడం ఆపు అని చెప్పండి.',
      pageOpened: 'పేజీ తెరవబడింది.',
      serviceOpened: 'తెరవబడింది.',
      sayEligibility:
        'అర్హత తనిఖీని ప్రారంభించడానికి అర్హత అని చెప్పండి,',
      sayDocuments:
        'అవసరమైన పత్రాలను మళ్లీ వినడానికి పత్రాలు అని చెప్పండి,',
      sayApplications:
        'నా దరఖాస్తులను తెరవడానికి దరఖాస్తులు అని చెప్పండి,',
      sayBack:
        'లేదా సేవల పేజీకి తిరిగి వెళ్లడానికి వెనక్కి అని చెప్పండి.',
    },

    hi: {
      home: 'होम डैशबोर्ड खुल गया है।',
      servicesOpened: 'सरकारी सेवाओं का पेज खुल गया है।',
      noServices:
        'सरकारी सेवाओं का पेज खुल गया है। अभी कोई सरकारी सेवा उपलब्ध नहीं है।',
      servicePrompt:
        'किसी सेवा को खोलने के लिए उसका नाम बोलें। वॉइस एक्सेस बंद करने के लिए रुकें बोलें।',
      applicationStatus:
        'आवेदन स्थिति का पेज खुल गया है।',
      applications:
        'मेरे आवेदन का पेज खुल गया है।',
      documents: 'दस्तावेज़ का पेज खुल गया है।',
      eligibility:
        'पात्रता जांच का पेज खुल गया है।',
      back: 'पिछले पेज पर वापस आ गए हैं।',
      languageReady:
        'भाषा हिंदी में बदल दी गई है। मैं तैयार हूँ।',
      unknown:
        'मुझे उस अनुरोध का उत्तर नहीं मिला।',
      backendError:
        'वॉइस असिस्टेंट बैकएंड से संपर्क नहीं कर सका।',
      help:
        'आप सेवाएं, छात्रवृत्ति, आय प्रमाण पत्र, स्वास्थ्य बीमा, पीएम किसान, आवास, पेंशन, आरटीई, जाति प्रमाण पत्र, आवेदन, दस्तावेज़, पात्रता, पेज पढ़ो, होम, वापस, पढ़ना बंद करो या रुकें कह सकते हैं।',
      stopHelp:
        'वॉइस एक्सेस बंद करने के लिए रुकें कहें। केवल पेज पढ़ना बंद करने के लिए पढ़ना बंद करो कहें।',
      pageOpened: 'पेज खुल गया है।',
      serviceOpened: 'खुल गया है।',
      sayEligibility:
        'पात्रता जांच शुरू करने के लिए पात्रता कहें,',
      sayDocuments:
        'आवश्यक दस्तावेज़ फिर से सुनने के लिए दस्तावेज़ कहें,',
      sayApplications:
        'मेरे आवेदन खोलने के लिए आवेदन कहें,',
      sayBack:
        'या सेवाओं पर वापस जाने के लिए वापस कहें।',
    },

    kn: {
      home: 'ಮುಖಪುಟ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ತೆರೆಯಲಾಗಿದೆ.',
      servicesOpened: 'ಸರ್ಕಾರಿ ಸೇವೆಗಳ ಪುಟ ತೆರೆಯಲಾಗಿದೆ.',
      noServices:
        'ಸರ್ಕಾರಿ ಸೇವೆಗಳ ಪುಟ ತೆರೆಯಲಾಗಿದೆ. ಪ್ರಸ್ತುತ ಯಾವುದೇ ಸರ್ಕಾರಿ ಸೇವೆಗಳು ಲಭ್ಯವಿಲ್ಲ.',
      servicePrompt:
        'ಸೇವೆಯನ್ನು ತೆರೆಯಲು ಅದರ ಹೆಸರನ್ನು ಹೇಳಿ. ಧ್ವನಿ ಪ್ರವೇಶವನ್ನು ನಿಲ್ಲಿಸಲು ನಿಲ್ಲಿಸಿ ಎಂದು ಹೇಳಿ.',
      applicationStatus:
        'ಅರ್ಜಿಯ ಸ್ಥಿತಿ ಪುಟ ತೆರೆಯಲಾಗಿದೆ.',
      applications:
        'ನನ್ನ ಅರ್ಜಿಗಳ ಪುಟ ತೆರೆಯಲಾಗಿದೆ.',
      documents: 'ದಾಖಲೆಗಳ ಪುಟ ತೆರೆಯಲಾಗಿದೆ.',
      eligibility:
        'ಅರ್ಹತೆ ಪರಿಶೀಲನೆ ಪುಟ ತೆರೆಯಲಾಗಿದೆ.',
      back: 'ಹಿಂದಿನ ಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಲಾಗಿದೆ.',
      languageReady:
        'ಭಾಷೆಯನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ. ನಾನು ಸಿದ್ಧವಾಗಿದ್ದೇನೆ.',
      unknown:
        'ಆ ವಿನಂತಿಗೆ ಉತ್ತರವನ್ನು ಕಂಡುಹಿಡಿಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.',
      backendError:
        'ಧ್ವನಿ ಸಹಾಯಕವು ಬ್ಯಾಕೆಂಡ್ ಅನ್ನು ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.',
      help:
        'ಸೇವೆಗಳು, ವಿದ್ಯಾರ್ಥಿವೇತನ, ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ, ಆರೋಗ್ಯ ವಿಮೆ, ಪಿಎಂ ಕಿಸಾನ್, ವಸತಿ, ಪಿಂಚಣಿ, ಆರ್‌ಟಿಇ, ಜಾತಿ ಪ್ರಮಾಣ ಪತ್ರ, ಅರ್ಜಿಗಳು, ದಾಖಲೆಗಳು, ಅರ್ಹತೆ, ಪುಟ ಓದಿ, ಮುಖಪುಟ, ಹಿಂದೆ, ಓದುವುದನ್ನು ನಿಲ್ಲಿಸಿ ಅಥವಾ ನಿಲ್ಲಿಸಿ ಎಂದು ಹೇಳಬಹುದು.',
      stopHelp:
        'ಧ್ವನಿ ಪ್ರವೇಶವನ್ನು ನಿಲ್ಲಿಸಲು ನಿಲ್ಲಿಸಿ ಎಂದು ಹೇಳಿ. ಪುಟ ಓದುವುದನ್ನು ಮಾತ್ರ ನಿಲ್ಲಿಸಲು ಓದುವುದನ್ನು ನಿಲ್ಲಿಸಿ ಎಂದು ಹೇಳಿ.',
      pageOpened: 'ಪುಟ ತೆರೆಯಲಾಗಿದೆ.',
      serviceOpened: 'ತೆರೆಯಲಾಗಿದೆ.',
      sayEligibility:
        'ಅರ್ಹತೆ ಪರಿಶೀಲನೆ ಪ್ರಾರಂಭಿಸಲು ಅರ್ಹತೆ ಎಂದು ಹೇಳಿ,',
      sayDocuments:
        'ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಮತ್ತೆ ಕೇಳಲು ದಾಖಲೆಗಳು ಎಂದು ಹೇಳಿ,',
      sayApplications:
        'ನನ್ನ ಅರ್ಜಿಗಳನ್ನು ತೆರೆಯಲು ಅರ್ಜಿಗಳು ಎಂದು ಹೇಳಿ,',
      sayBack:
        'ಅಥವಾ ಸೇವೆಗಳ ಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಲು ಹಿಂದೆ ಎಂದು ಹೇಳಿ.',
    },
  };

  const currentVoiceText = VOICE_TEXT[selectedLanguage];

  const SERVICE_NAMES: Record<
    LanguageCode,
    string[]
  > = {
    en: [
      'Scholarship',
      'Income Certificate',
      'Health Insurance',
      'PM Kisan',
      'Housing',
      'Pension',
      'RTE',
      'Community Certificate',
    ],
    ta: [
      'உதவித்தொகை',
      'வருமானச் சான்றிதழ்',
      'மருத்துவக் காப்பீடு',
      'பிஎம் கிசான்',
      'வீட்டுவசதி',
      'ஓய்வூதியம்',
      'ஆர்டிஇ',
      'சமூகச் சான்றிதழ்',
    ],
    te: [
      'విద్యార్థి వేతనం',
      'ఆదాయ ధృవీకరణ పత్రం',
      'ఆరోగ్య బీమా',
      'పీఎం కిసాన్',
      'గృహం',
      'పెన్షన్',
      'ఆర్‌టీఈ',
      'కమ్యూనిటీ సర్టిఫికేట్',
    ],
    hi: [
      'छात्रवृत्ति',
      'आय प्रमाण पत्र',
      'स्वास्थ्य बीमा',
      'पीएम किसान',
      'आवास',
      'पेंशन',
      'आरटीई',
      'जाति प्रमाण पत्र',
    ],
    kn: [
      'ವಿದ್ಯಾರ್ಥಿವೇತನ',
      'ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ',
      'ಆರೋಗ್ಯ ವಿಮೆ',
      'ಪಿಎಂ ಕಿಸಾನ್',
      'ವಸತಿ',
      'ಪಿಂಚಣಿ',
      'ಆರ್‌ಟಿಇ',
      'ಜಾತಿ ಪ್ರಮಾಣ ಪತ್ರ',
    ],
  };

  const getLocalizedServiceName = (
    service: GovernmentService
  ): string => {
    const index =
      ALL_CURATED_SERVICES.findIndex(
        (item) => item.id === service.id
      );

    if (
      index >= 0 &&
      SERVICE_NAMES[selectedLanguage][index]
    ) {
      return SERVICE_NAMES[selectedLanguage][index];
    }

    return service.name;
  };

  const restart = () => {
    if (
      !voiceAccessEnabled ||
      busyRef.current ||
      activeRef.current
    ) {
      return;
    }

    try {
      recognitionRef.current?.start();
    } catch {}
  };

  const pauseRecognition = () => {
    try {
      recognitionRef.current?.stop();
    } catch {}

    activeRef.current = false;
    setIsListening(false);
  };

  const speakVoiceResponse = (text: string) => {
    if (!text.trim()) {
      busyRef.current = false;
      restart();
      return;
    }

    pauseRecognition();

    speakAnnouncement(text);

    const words = Math.max(
      1,
      text.trim().split(/\s+/).length
    );

    const delay = Math.min(
      12000,
      Math.max(1800, words * 115)
    );

    window.setTimeout(() => {
      busyRef.current = false;
      restart();
    }, delay);
  };

  const readPageInSelectedLanguage = async () => {
    if (busyRef.current) {
      return;
    }

    busyRef.current = true;
    pauseRecognition();

    try {
      await readPageContentAloud();
    } finally {
      busyRef.current = false;

      if (!isSpeaking) {
        restart();
      }
    }
  };

  const findServiceFromCommand = (
    text: string
  ): GovernmentService | null => {
    const lower = text.toLowerCase();

    const aliases: Array<{
      service: GovernmentService;
      words: string[];
    }> = [
      {
        service: ALL_CURATED_SERVICES[0],
        words: [
          'scholarship',
          'scholarships',
          'post matric',
          'student scholarship',
          'student scholarships',
          'உதவித்தொகை',
          'மாணவர் உதவித்தொகை',
          'ஸ்காலர்ஷிப்',
          'విద్యార్థి వేతనం',
          'విద్యార్థి స్కాలర్‌షిప్',
          'స్కాలర్‌షిప్',
          'छात्रवृत्ति',
          'स्कॉलरशिप',
          'ವಿದ್ಯಾರ್ಥಿವೇತನ',
          'ಸ್ಕಾಲರ್‌ಶಿಪ್',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[1],
        words: [
          'income certificate',
          'income certificates',
          'income',
          'income and asset certificate',
          'வருமானச் சான்றிதழ்',
          'வருமான சான்றிதழ்',
          'வருமானம்',
          'ஆதாயச் சான்றிதழ்',
          'ఆదాయ ధృవీకరణ పత్రం',
          'ఆదాయ ధృవీకరణ',
          'ఆదాయ ధ్రువీకరణ పత్రం',
          'ఆదాయ సర్టిఫికేట్',
          'आय प्रमाण पत्र',
          'आय प्रमाणपत्र',
          'आय प्रमाण',
          'आय सर्टिफिकेट',
          'ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ',
          'ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[2],
        words: [
          'health insurance',
          'health',
          'chief minister health',
          'மருத்துவ காப்பீடு',
          'மருத்துவக் காப்பீடு',
          'சுகாதார காப்பீடு',
          'சுகாதாரம்',
          'ఆరోగ్య బీమా',
          'ఆరోగ్య భీమా',
          'ఆరోగ్యం',
          'स्वास्थ्य बीमा',
          'स्वास्थ्य',
          'हेल्थ इंश्योरेंस',
          'ಆರೋಗ್ಯ ವಿಮೆ',
          'ಆರೋಗ್ಯ',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[3],
        words: [
          'pm kisan',
          'pmkisan',
          'kisan',
          'farmer support',
          'farmer',
          'பிஎம் கிசான்',
          'பிரதமர் கிசான்',
          'விவசாயி',
          'விவசாயிகள்',
          'పీఎం కిసాన్',
          'పిఎం కిసాన్',
          'రైతు',
          'రైతులు',
          'पीएम किसान',
          'किसान',
          'किसानों',
          'ಪಿಎಂ ಕಿಸಾನ್',
          'ಪಿಎಮ್ ಕಿಸಾನ್',
          'ರೈತ',
          'ರೈತರು',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[4],
        words: [
          'housing',
          'pmay',
          'awas',
          'house',
          'வீட்டுவசதி',
          'வீடு',
          'பிரதம மந்திரி ஆவாஸ்',
          'గృహ',
          'ఇల్లు',
          'ప్రధాన మంత్రి ఆవాస్',
          'आवास',
          'घर',
          'प्रधानमंत्री आवास',
          'ವಸತಿ',
          'ಮನೆ',
          'ಪ್ರಧಾನ ಮಂತ್ರಿ ಆವಾಸ್',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[5],
        words: [
          'old age pension',
          'pension',
          'senior citizen',
          'முதியோர் ஓய்வூதியம்',
          'ஓய்வூதியம்',
          'முதியோர்',
          'వృద్ధాప్య పెన్షన్',
          'పెన్షన్',
          'వృద్ధులు',
          'वृद्धावस्था पेंशन',
          'पेंशन',
          'वरिष्ठ नागरिक',
          'ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿ',
          'ಪಿಂಚಣಿ',
          'ಹಿರಿಯ ನಾಗರಿಕ',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[6],
        words: [
          'rte',
          'school admission',
          'private school',
          'right to education',
          'ஆர்டிஇ',
          'பள்ளி சேர்க்கை',
          'பள்ளி அனுமதி',
          'கல்வி உரிமை',
          'ఆర్‌టీఈ',
          'పాఠశాల ప్రవేశం',
          'పాఠశాల అడ్మిషన్',
          'విద్యా హక్కు',
          'आरटीई',
          'स्कूल प्रवेश',
          'विद्यालय प्रवेश',
          'शिक्षा का अधिकार',
          'ಆರ್‌ಟಿಇ',
          'ಶಾಲಾ ಪ್ರವೇಶ',
          'ಶಿಕ್ಷಣದ ಹಕ್ಕು',
        ],
      },
      {
        service: ALL_CURATED_SERVICES[7],
        words: [
          'community certificate',
          'caste certificate',
          'community and caste',
          'caste',
          'சமூகச் சான்றிதழ்',
          'சமூக சான்றிதழ்',
          'சாதிச் சான்றிதழ்',
          'சாதி சான்றிதழ்',
          'சாதி',
          'కమ్యూనిటీ సర్టిఫికేట్',
          'కుల ధృవీకరణ పత్రం',
          'కుల ధ్రువీకరణ పత్రం',
          'కులం',
          'समुदाय प्रमाण पत्र',
          'जाति प्रमाण पत्र',
          'जाति प्रमाणपत्र',
          'जाति',
          'ಸಮುದಾಯ ಪ್ರಮಾಣ ಪತ್ರ',
          'ಜಾತಿ ಪ್ರಮಾಣ ಪತ್ರ',
          'ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ',
          'ಜಾತಿ',
        ],
      },
    ];

    for (const item of aliases) {
      if (
        item.words.some((word) =>
          lower.includes(word.toLowerCase())
        )
      ) {
        return item.service;
      }
    }

    return null;
  };

  const containsAny = (
    text: string,
    words: string[]
  ) => {
    const lower = text.toLowerCase();

    return words.some((word) =>
      lower.includes(word.toLowerCase())
    );
  };

  const announceServices = async () => {
    try {
      const services =
        await servicesService.getServices('', '');

      if (!services.length) {
        speakVoiceResponse(
          currentVoiceText.noServices
        );
        return;
      }

      const names = services
        .map((service) =>
          getLocalizedServiceName(service)
        )
        .filter(Boolean);

      const announcement =
        `${currentVoiceText.servicesOpened} ` +
        `${currentVoiceText.servicePrompt} ` +
        `${names.join(', ')}. ` +
        `${currentVoiceText.stopHelp}`;

      speakVoiceResponse(announcement);
    } catch {
      const names =
        SERVICE_NAMES[selectedLanguage].join(', ');

      speakVoiceResponse(
        `${currentVoiceText.servicesOpened} ${names}. ${currentVoiceText.servicePrompt}`
      );
    }
  };

  const announceService = (
    service: GovernmentService
  ) => {
    const localizedName =
      getLocalizedServiceName(service);

    const announcement =
      `${localizedName} ${currentVoiceText.serviceOpened} ` +
      `${currentVoiceText.sayEligibility} ` +
      `${currentVoiceText.sayDocuments} ` +
      `${currentVoiceText.sayApplications} ` +
      `${currentVoiceText.sayBack}`;

    speakVoiceResponse(announcement);
  };

  const openService = (
    service: GovernmentService
  ) => {
    pauseRecognition();

    navigate(`/services/${service.id}`);

    announceService(service);
  };

  const processVoiceCommand = async (
    cmd: string
  ) => {
    const text = cmd.trim();

    if (!text || busyRef.current) {
      return;
    }

    busyRef.current = true;

    const lower = text.toLowerCase();

    if (
      containsAny(lower, [
        'stop listening',
        'be quiet',
        'quiet',
        'silence',
        'stop',
        'நிறுத்து',
        'அமைதி',
        'கேட்பதை நிறுத்து',
        'ఆపండి',
        'నిశ్శబ్దం',
        'వినడం ఆపు',
        'रुको',
        'चुप',
        'सुनना बंद करो',
        'ನಿಲ್ಲಿಸಿ',
        'ಮೌನ',
        'ಕೇಳುವುದನ್ನು ನಿಲ್ಲಿಸಿ',
      ])
    ) {
      busyRef.current = false;
      stopSpeaking();
      stopPageReading();
      pauseRecognition();
      setVoiceAccessEnabled(false);
      return;
    }

    if (
      containsAny(lower, [
        'stop reading',
        'stop page reading',
        'stop reading page',
        'படிப்பதை நிறுத்து',
        'பக்கத்தைப் படிப்பதை நிறுத்து',
        'చదవడం ఆపు',
        'పేజీ చదవడం ఆపు',
        'पढ़ना बंद करो',
        'पेज पढ़ना बंद करो',
        'ಓದುವುದನ್ನು ನಿಲ್ಲಿಸಿ',
        'ಪುಟ ಓದುವುದನ್ನು ನಿಲ್ಲಿಸಿ',
      ])
    ) {
      busyRef.current = false;
      stopPageReading();
      return;
    }

    if (
      containsAny(lower, [
        'read page',
        'read this page',
        'read the page',
        'read page aloud',
        'பக்கத்தை படி',
        'இந்த பக்கத்தை படி',
        'பக்கத்தை வாசி',
        'పేజీ చదువు',
        'ఈ పేజీ చదువు',
        'పేజీని చదవండి',
        'पेज पढ़ो',
        'यह पेज पढ़ो',
        'पृष्ठ पढ़ें',
        'ಪುಟವನ್ನು ಓದು',
        'ಈ ಪುಟವನ್ನು ಓದು',
        'ಪುಟ ಓದಿ',
      ])
    ) {
      busyRef.current = false;
      await readPageInSelectedLanguage();
      return;
    }

    const languageMatches: Array<{
      code: LanguageCode;
      words: string[];
      response: string;
    }> = [
      {
        code: 'en',
        words: [
          'english',
          'ஆங்கிலம்',
          'ஆங்கில',
          'ఇంగ్లీష్',
          'ఆంగ్లం',
          'अंग्रेजी',
          'अंग्रेज़ी',
          'ಇಂಗ್ಲಿಷ್',
          'ಆಂಗ್ಲ',
        ],
        response: VOICE_TEXT.en.languageReady,
      },
      {
        code: 'ta',
        words: [
          'tamil',
          'தமிழ்',
          'தமிழில்',
        ],
        response: VOICE_TEXT.ta.languageReady,
      },
      {
        code: 'te',
        words: [
          'telugu',
          'తెలుగు',
          'తెలుగులో',
        ],
        response: VOICE_TEXT.te.languageReady,
      },
      {
        code: 'hi',
        words: [
          'hindi',
          'हिंदी',
          'हिन्दी',
        ],
        response: VOICE_TEXT.hi.languageReady,
      },
      {
        code: 'kn',
        words: [
          'kannada',
          'ಕನ್ನಡ',
          'ಕನ್ನಡದಲ್ಲಿ',
        ],
        response: VOICE_TEXT.kn.languageReady,
      },
    ];

    const languageMatch =
      languageMatches.find((item) =>
        item.words.some((word) =>
          lower.includes(word.toLowerCase())
        )
      );

    if (languageMatch) {
      setSelectedLanguage(languageMatch.code);
      speakVoiceResponse(languageMatch.response);
      return;
    }

    /*
     * Check the specific scheme BEFORE the generic
     * "services" command.
     *
     * This makes:
     *   Scholarship -> /services/1
     *   Income Certificate -> /services/2
     *
     * even when the user does not say "services".
     */
    const requestedService =
      findServiceFromCommand(text);

    if (requestedService) {
      openService(requestedService);
      return;
    }

    if (
      containsAny(lower, [
        'home',
        'dashboard',
        'go home',
        'முகப்பு',
        'முகப்புப் பக்கம்',
        'டாஷ்போர்டு',
        'హోమ్',
        'ముఖ్య పేజీ',
        'డాష్‌బోర్డ్',
        'होम',
        'मुख्य पृष्ठ',
        'डैशबोर्ड',
        'ಮುಖಪುಟ',
        'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
      ])
    ) {
      navigate('/');
      speakVoiceResponse(
        currentVoiceText.home
      );
      return;
    }

    if (
      containsAny(lower, [
        'services',
        'service',
        'சேவைகள்',
        'சேவை',
        'சேவைகளை',
        'సేవలు',
        'సేవ',
        'सेवाएं',
        'सेवा',
        'ಸೇವೆಗಳು',
        'ಸೇವೆ',
      ])
    ) {
      navigate('/services');
      await announceServices();
      return;
    }

    if (
      containsAny(lower, [
        'application status',
        'status',
        'விண்ணப்ப நிலை',
        'விண்ணப்பத்தின் நிலை',
        'விண்ணப்ப நிலையை',
        'దరఖాస్తు స్థితి',
        'అప్లికేషన్ స్టేటస్',
        'आवेदन की स्थिति',
        'आवेदन स्थिति',
        'ಅರ್ಜಿಯ ಸ್ಥಿತಿ',
        'ಅಪ್ಲಿಕೇಶನ್ ಸ್ಥಿತಿ',
      ])
    ) {
      navigate('/status');

      speakVoiceResponse(
        currentVoiceText.applicationStatus
      );

      return;
    }

    if (
      containsAny(lower, [
        'applications',
        'my applications',
        'application',
        'விண்ணப்பங்கள்',
        'எனது விண்ணப்பங்கள்',
        'விண்ணப்பம்',
        'దరఖాస్తులు',
        'నా దరఖాస్తులు',
        'आवेदन',
        'मेरे आवेदन',
        'ಅರ್ಜಿಗಳು',
        'ನನ್ನ ಅರ್ಜಿಗಳು',
      ])
    ) {
      navigate('/applications');

      speakVoiceResponse(
        currentVoiceText.applications
      );

      return;
    }

    if (
      containsAny(lower, [
        'documents',
        'document',
        'ஆவணங்கள்',
        'ஆவணம்',
        'எனது ஆவணங்கள்',
        'పత్రాలు',
        'పత్రం',
        'నా పత్రాలు',
        'दस्तावेज',
        'दस्तावेज़',
        'मेरे दस्तावेज',
        'ದಾಖಲೆಗಳು',
        'ದಾಖಲೆ',
        'ನನ್ನ ದಾಖಲೆಗಳು',
      ])
    ) {
      navigate('/documents');

      speakVoiceResponse(
        currentVoiceText.documents
      );

      return;
    }

    if (
      containsAny(lower, [
        'eligibility',
        'check eligibility',
        'start eligibility',
        'தகுதி',
        'தகுதியை சரிபார்',
        'தகுதி சரிபார்ப்பு',
        'అర్హత',
        'అర్హతను తనిఖీ చేయండి',
        'पात्रता',
        'पात्रता जांच',
        'ಅರ್ಹತೆ',
        'ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಿ',
      ])
    ) {
      navigate('/eligibility');

      speakVoiceResponse(
        currentVoiceText.eligibility
      );

      return;
    }

    if (
      containsAny(lower, [
        'help',
        'what can i say',
        'voice commands',
        'உதவி',
        'என்ன சொல்லலாம்',
        'సహాయం',
        'నేను ఏమి చెప్పగలను',
        'मदद',
        'मैं क्या कह सकता हूं',
        'ಸಹಾಯ',
        'ನಾನು ಏನು ಹೇಳಬಹುದು',
      ])
    ) {
      speakVoiceResponse(
        currentVoiceText.help
      );

      return;
    }

    if (
      containsAny(lower, [
        'back',
        'go back',
        'previous page',
        'பின் செல்',
        'பின்னால்',
        'முந்தைய பக்கம்',
        'వెనక్కి',
        'వెనుకకు వెళ్ళు',
        'మునుపటి పేజీ',
        'वापस',
        'पीछे जाएं',
        'पिछला पृष्ठ',
        'ಹಿಂದೆ',
        'ಹಿಂದಕ್ಕೆ ಹೋಗಿ',
        'ಹಿಂದಿನ ಪುಟ',
      ])
    ) {
      navigate(-1);

      speakVoiceResponse(
        currentVoiceText.back
      );

      return;
    }

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

      const res =
        await apiClient.post(
          '/conversation/chat',
          {
            message: text,
            language: selectedLanguage,
            session_id: sessionId,
            page_context:
              window.location.pathname,
          }
        );

      const answer = String(
        res.data.response || ''
      ).trim();

      speakVoiceResponse(
        answer ||
          currentVoiceText.unknown
      );
    } catch (e: any) {
      const detail =
        e?.response?.data?.detail ||
        currentVoiceText.backendError;

      speakVoiceResponse(detail);
    }
  };

  useEffect(() => {
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SR) {
      setPermissionError(
        'Speech recognition is not supported here. Use Chrome or Edge and allow microphone access.'
      );
      return;
    }

    const r = new SR();

    r.continuous = false;
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.lang = langMap[selectedLanguage];

    r.onstart = () => {
      activeRef.current = true;
      setIsListening(true);
      setPermissionError('');
    };

    r.onresult = (e: any) => {
      const transcript =
        e.results?.[0]?.[0]?.transcript?.trim();

      if (transcript) {
        setLastCommand(transcript);
        processVoiceCommand(transcript);
      }
    };

    r.onerror = (e: any) => {
      activeRef.current = false;
      setIsListening(false);

      if (
        e.error === 'not-allowed' ||
        e.error === 'permission-denied'
      ) {
        setPermissionError(
          'Microphone permission is blocked. Allow microphone access for this site.'
        );

        setVoiceAccessEnabled(false);
      } else if (
        e.error === 'audio-capture'
      ) {
        setPermissionError(
          'No microphone was detected. Check the selected Windows microphone.'
        );
      }
    };

    r.onend = () => {
      activeRef.current = false;
      setIsListening(false);

      if (
        voiceAccessEnabled &&
        !busyRef.current
      ) {
        setTimeout(restart, 250);
      }
    };

    recognitionRef.current = r;

    if (
      voiceAccessEnabled &&
      !busyRef.current
    ) {
      setTimeout(restart, 150);
    }

    return () => {
      activeRef.current = false;

      try {
        r.stop();
      } catch {}

      recognitionRef.current = null;
    };
  }, [
    selectedLanguage,
    voiceAccessEnabled,
  ]);

  return (
    <div className="bg-slate-900 text-white border-b-2 border-gov-gold px-4 py-2 flex flex-wrap items-center justify-between text-xs">
      <div className="flex items-center gap-3">
        <button
          onClick={() =>
            setVoiceAccessEnabled(
              !voiceAccessEnabled
            )
          }
          className={`flex items-center px-3 py-1.5 rounded-full font-bold ${
            voiceAccessEnabled
              ? 'bg-red-600 text-white'
              : 'bg-gov-gold text-slate-900'
          }`}
        >
          {voiceAccessEnabled ? (
            <>
              <Mic className="w-3.5 h-3.5 mr-1.5" />
              Voice Access ON
            </>
          ) : (
            <>
              <MicOff className="w-3.5 h-3.5 mr-1.5" />
              Start Voice Access
            </>
          )}
        </button>

        {isListening && (
          <span className="text-[11px] text-gov-gold">
            Listening…
            {lastCommand &&
              ` Recognized: "${lastCommand}"`}
          </span>
        )}

        {permissionError && (
          <span className="text-[11px] text-red-300 flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5" />
            {permissionError}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={readPageInSelectedLanguage}
          className="px-2.5 py-1 bg-blue-800 rounded flex items-center"
        >
          <Volume2 className="w-3.5 h-3.5 mr-1 text-gov-gold" />
          Read Page
        </button>

        {isSpeaking && (
          <button
            onClick={() => {
              stopPageReading();
              stopSpeaking();
            }}
            className="px-2.5 py-1 bg-red-800 rounded flex items-center"
          >
            <Square className="w-3.5 h-3.5 mr-1" />
            Stop Speaking
          </button>
        )}

        <button
          onClick={() =>
            setShowHelp(!showHelp)
          }
          className="p-1"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>

      {showHelp && (
        <div className="w-full mt-2 bg-slate-800 p-3 rounded-lg">
          Activate Voice Access once. Speak one request at a time.
          The microphone pauses while AccessGov AI speaks so it
          cannot hear its own response. Say stop to stop voice
          access. Say stop reading to stop only page reading.
          Read Page is manual only.
        </div>
      )}
    </div>
  );
};

export default VoiceAccessBar;