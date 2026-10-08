import { LanguageCode } from '../context/AccessibilityContext';

export interface Translations {
  // Navigation
  home: string;
  services: string;
  myApplications: string;
  myDocuments: string;
  applicationStatus: string;
  helpAccessibility: string;
  adminDashboard: string;
  analytics: string;
  accessibility: string;
  documents: string;
  districtInsights: string;
  
  // Hero & Core Copy
  heroTitle: string;
  heroSub: string;
  findService: string;
  checkEligibility: string;
  uploadDocuments: string;
  askAssistant: string;
  startVoiceAccess: string;
  readPage: string;
  stopSpeaking: string;

  // Journey Steps
  discover: string;
  understandEligibility: string;
  checkDocuments: string;
  accessibleGuidance: string;

  // Eligibility Outcomes
  eligibleTitle: string;
  eligibleSub: string;
  notEligibleTitle: string;
  notEligibleSub: string;
  moreInfoRequiredTitle: string;
  moreInfoRequiredSub: string;

  // Common UI
  requiredDocuments: string;
  readinessScore: string;
  saveDraft: string;
  continueApplication: string;
  disclaimer: string;
}

export const TRANSLATIONS: Record<LanguageCode, Translations> = {
  en: {
    home: "Home",
    services: "Services",
    myApplications: "My Applications",
    myDocuments: "My Documents",
    applicationStatus: "Application Status",
    helpAccessibility: "Help & Accessibility",
    adminDashboard: "Admin Dashboard",
    analytics: "Analytics",
    accessibility: "Accessibility",
    documents: "Documents",
    districtInsights: "District Insights",

    heroTitle: "Access government services with confidence.",
    heroSub: "Find services, understand eligibility, verify documents, and interact with government information through accessible voice and text assistance.",
    findService: "Find a Service",
    checkEligibility: "Check My Eligibility",
    uploadDocuments: "Upload Documents",
    askAssistant: "Ask AccessGov AI",
    startVoiceAccess: "Start Voice Access",
    readPage: "Read Page",
    stopSpeaking: "Stop Speaking",

    discover: "1. Discover",
    understandEligibility: "2. Understand Eligibility",
    checkDocuments: "3. Check Documents",
    accessibleGuidance: "4. Get Accessible Guidance",

    eligibleTitle: "YOU APPEAR ELIGIBLE BASED ON THE INFORMATION PROVIDED",
    eligibleSub: "Your profile satisfies the official revenue and academic conditions configured for this scheme.",
    notEligibleTitle: "YOU DO NOT CURRENTLY MEET ELIGIBILITY CONDITIONS",
    notEligibleSub: "Based on declared parameters, one or more eligibility rules were not satisfied.",
    moreInfoRequiredTitle: "MORE INFORMATION REQUIRED TO DETERMINE ELIGIBILITY",
    moreInfoRequiredSub: "Please provide the missing parameters (e.g., examination percentage or income certificate) to complete evaluation.",

    requiredDocuments: "Required Documents",
    readinessScore: "Document Readiness Score",
    saveDraft: "Save Application Draft",
    continueApplication: "Continue Application",
    disclaimer: "Notice: AccessGov AI provides eligibility, requirement, document-readiness, and application guidance. Official certificate issuance and submission are handled by the government department."
  },

  ta: {
    home: "முகப்பு",
    services: "சேவைகள்",
    myApplications: "என் விண்ணப்பங்கள்",
    myDocuments: "என் ஆவணங்கள்",
    applicationStatus: "விண்ணப்ப நிலை",
    helpAccessibility: "உதவி & அணுகல்தன்மை",
    adminDashboard: "நிர்வாகி டாஷ்போர்டு",
    analytics: "பகுப்பாய்வு",
    accessibility: "அணுகல்தன்மை",
    documents: "ஆவணங்கள்",
    districtInsights: "மாவட்ட தகவல்கள்",

    heroTitle: "அரசு சேவைகளை நம்பிக்கையுடன் அணுகுங்கள்.",
    heroSub: "சேவைகளைக் கண்டறியவும், தகுதியைப் புரிந்து கொள்ளவும், ஆவணங்களைச் சரிபார்க்கவும், குரல் மற்றும் உரை உதவி மூலம் அரசுத் தகவல்களுடன் உரையாடவும்.",
    findService: "சேவையைக் கண்டறி",
    checkEligibility: "என் தகுதியைச் சரிபார்",
    uploadDocuments: "ஆவணங்களை பதிவேற்று",
    askAssistant: "AccessGov AI-யிடம் கேள்",
    startVoiceAccess: "குரல் அணுகலைத் தொடங்கு",
    readPage: "பக்கத்தைப் படி",
    stopSpeaking: "பேசுவதை நிறுத்து",

    discover: "1. கண்டறி",
    understandEligibility: "2. தகுதியைப் புரிந்துகொள்",
    checkDocuments: "3. ஆவணங்களைச் சரிபார்",
    accessibleGuidance: "4. குரல் வழிகாட்டுதல் பெறு",

    eligibleTitle: "வழங்கப்பட்ட தகவலின் அடிப்படையில் நீங்கள் தகுதியுடையவர்",
    eligibleSub: "உங்கள் சுயவிவரம் இத்திட்டத்திற்கான அதிகாரப்பூர்வ வருவாய் மற்றும் கல்வி நிபந்தனைகளைப் பூர்த்தி செய்கிறது.",
    notEligibleTitle: "தற்போது நீங்கள் தகுதி நிபந்தனைகளைப் பூர்த்தி செய்யவில்லை",
    notEligibleSub: "அறிவிக்கப்பட்ட அளவுகோல்களின் அடிப்படையில் ஒன்று அல்லது அதற்கு மேற்பட்ட தகுதி விதிகள் பூர்த்தி செய்யப்படவில்லை.",
    moreInfoRequiredTitle: "தகுதியைத் தீர்மானிக்க கூடுதல் தகவல் தேவைப்படுகிறது",
    moreInfoRequiredSub: "மதிப்பீட்டை முடிக்க விடுபட்ட தகவல்களை வழங்கவும்.",

    requiredDocuments: "தேவையான ஆவணங்கள்",
    readinessScore: "ஆவண தயார்நிலை மதிப்பெண்",
    saveDraft: "விண்ணப்ப வரைவைச் சேமி",
    continueApplication: "விண்ணப்பத்தைத் தொடர்",
    disclaimer: "அறிவிப்பு: AccessGov AI தகுதி, ஆவணத் தயார்நிலை மற்றும் வழிகாட்டுதலை வழங்குகிறது. அதிகாரப்பூர்வ சான்றிதழ் வழங்கல் அரசுத் துறையால் கையாளப்படுகிறது."
  },

  te: {
    home: "హోమ్",
    services: "సేవలు",
    myApplications: "నా దరఖాస్తులు",
    myDocuments: "నా పత్రాలు",
    applicationStatus: "దరఖాస్తు స్థితి",
    helpAccessibility: "సహాయం & లభ్యత",
    adminDashboard: "అడ్మిన్ డాష్‌బోర్డ్",
    analytics: "విశ్లేషణలు",
    accessibility: "లభ్యత",
    documents: "పత్రాలు",
    districtInsights: "జిల్లా సమాచారం",

    heroTitle: "నమ్మకంతో ప్రభుత్వ సేవలను పొందండి.",
    heroSub: "సేవలను కనుగొనండి, అర్హతను అర్థం చేసుకోండి, పత్రాలను తనిఖీ చేయండి మరియు వాయిస్ ద్వారా సంభాషించండి.",
    findService: "సేవను కనుగొనండి",
    checkEligibility: "నా అర్హతను తనిఖీ చేయండి",
    uploadDocuments: "పత్రాలను అప్‌లోడ్ చేయండి",
    askAssistant: "AccessGov AI ని అడగండి",
    startVoiceAccess: "వాయిస్ యాక్సెస్ ప్రారంభించండి",
    readPage: "పేజీ చదవండి",
    stopSpeaking: "మాట్లాడటం ఆపండి",

    discover: "1. కనుగొనండి",
    understandEligibility: "2. అర్హత అర్థం చేసుకోండి",
    checkDocuments: "3. పత్రాలు తనిఖీ చేయండి",
    accessibleGuidance: "4. వాయిస్ మార్గదర్శకత్వం పొందండి",

    eligibleTitle: "సమాచారం ఆధారంగా మీరు అర్హులుగా కనిపిస్తున్నారు",
    eligibleSub: "మీ ప్రొఫైల్ ఈ పథకానికి నిర్దేశించిన అధికారిక ఆదాయ మరియు విద్యా నిబంధనలను పూర్తి చేసింది.",
    notEligibleTitle: "మీరు ప్రస్తుతం అర్హత నిబంధనలను పూర్తి చేయలేదు",
    notEligibleSub: "తెలిపిన పారామితుల ఆధారంగా ఒకటి లేదా అంతకంటే ఎక్కువ నిబంధనలు నెరవేరలేదు.",
    moreInfoRequiredTitle: "అర్హత నిర్ణయించడానికి మరింత సమాచారం అవసరం",
    moreInfoRequiredSub: "అంచనాను పూర్తి చేయడానికి మిగిలిన సమాచారాన్ని అందించండి.",

    requiredDocuments: "అవసరమైన పత్రాలు",
    readinessScore: "పత్రం సన్నద్ధత స్కోరు",
    saveDraft: "ఖరారు కాని దరఖాస్తును దాచండి",
    continueApplication: "దరఖాస్తును కొనసాగించండి",
    disclaimer: "గమనిక: AccessGov AI అర్హత, పత్రాల సన్నద్ధత మరియు దరఖాస్తు మార్గదర్శకత్వాన్ని అందిస్తుంది. అధికారిక ధృవీకరణ పత్రాల జారీ ప్రభుత్వ శాఖ ద్వారా జరుగుతుంది."
  },

  hi: {
    home: "मुख्य पृष्ठ",
    services: "सेवाएं",
    myApplications: "मेरे आवेदन",
    myDocuments: "मेरे दस्तावेज",
    applicationStatus: "आवेदन की स्थिति",
    helpAccessibility: "सहायता और सुगम्यता",
    adminDashboard: "एडमिन डैशबोर्ड",
    analytics: "विश्लेषण",
    accessibility: "सुगम्यता",
    documents: "दस्तावेज",
    districtInsights: "जिला जानकारी",

    heroTitle: "आत्मविश्वास के साथ सरकारी सेवाओं का लाभ उठाएं।",
    heroSub: "सेवाएं खोजें, पात्रता समझें, दस्तावेजों का सत्यापन करें और आवाज तथा पाठ सहायता के माध्यम से सरकारी जानकारी प्राप्त करें।",
    findService: "सेवा खोजें",
    checkEligibility: "पात्रता जांचें",
    uploadDocuments: "दस्तावेज अपलोड करें",
    askAssistant: "AccessGov AI से पूछें",
    startVoiceAccess: "वॉइस एक्सेस शुरू करें",
    readPage: "पृष्ठ पढ़ें",
    stopSpeaking: "बोलना बंद करें",

    discover: "1. खोजें",
    understandEligibility: "2. पात्रता समझें",
    checkDocuments: "3. दस्तावेज जांचें",
    accessibleGuidance: "4. सुगम मार्गदर्शन प्राप्त करें",

    eligibleTitle: "दी गई जानकारी के आधार पर आप पात्र प्रतीत होते हैं",
    eligibleSub: "आपका प्रोफ़ाइल इस योजना के लिए निर्धारित आधिकारिक आय और शैक्षणिक शर्तों को पूरा करता है।",
    notEligibleTitle: "आप वर्तमान में पात्रता शर्तों को पूरा नहीं करते हैं",
    notEligibleSub: "घोषित मापदंडों के आधार पर एक या अधिक पात्रता नियम पूरे नहीं हुए हैं।",
    moreInfoRequiredTitle: "पात्रता निर्धारित करने के लिए अधिक जानकारी आवश्यक है",
    moreInfoRequiredSub: "मूल्यांकन पूरा करने के लिए कृपया लापता जानकारी प्रदान करें।",

    requiredDocuments: "आवश्यक दस्तावेज",
    readinessScore: "दस्तावेज तत्परता स्कोर",
    saveDraft: "ड्राफ्ट सहेजें",
    continueApplication: "आवेदन जारी रखें",
    disclaimer: "सूचना: AccessGov AI पात्रता, दस्तावेज तत्परता और मार्गदर्शन प्रदान करता है। आधिकारिक प्रमाण पत्र जारी करना सरकारी विभाग द्वारा संभाला जाता है।"
  },

  kn: {
    home: "ಮುಖ್ಯ ಪುಟ",
    services: "ಸೇವೆಗಳು",
    myApplications: "ನನ್ನ ಅರ್ಜಿಗಳು",
    myDocuments: "ನನ್ನ ದಾಖಲೆಗಳು",
    applicationStatus: "ಅರ್ಜಿಯ ಸ್ಥಿತಿ",
    helpAccessibility: "ಸಹಾಯ ಮತ್ತು ಸುಲಭ್ಯತೆ",
    adminDashboard: "ಅಡ್ಮಿನ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    analytics: "ವಿಶ್ಲೇಷಣೆ",
    accessibility: "ಸುಲಭ್ಯತೆ",
    documents: "ದಾಖಲೆಗಳು",
    districtInsights: "ಜಿಲ್ಲಾ ಮಾಹಿತಿ",

    heroTitle: "ಆತ್ಮವಿಶ್ವಾಸದಿಂದ ಸರ್ಕಾರಿ ಸೇವೆಗಳನ್ನು ಪಡೆಯಿರಿ.",
    heroSub: "ಸೇವೆಗಳನ್ನು ಹುಡುಕಿ, ಅರ್ಹತೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ, ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಧ್ವನಿ ನೆರವಿನ ಮೂಲಕ ಸಂವಹನ ನಡೆಸಿ.",
    findService: "ಸೇವೆಯನ್ನು ಹುಡುಕಿ",
    checkEligibility: "ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ",
    uploadDocuments: "ದಾಖಲೆಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
    askAssistant: "AccessGov AI ಕೇಳಿ",
    startVoiceAccess: "ಧ್ವನಿ ಪ್ರವೇಶ ಪ್ರಾರಂಭಿಸಿ",
    readPage: "ಪುಟ ಓದಿ",
    stopSpeaking: "ಮಾತನಾಡುವುದನ್ನು ನಿಲ್ಲಿಸಿ",

    discover: "1. ಹುಡುಕಿ",
    understandEligibility: "2. ಅರ್ಹತೆ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ",
    checkDocuments: "3. ದಾಖಲೆ ಪರಿಶೀಲಿಸಿ",
    accessibleGuidance: "4. ಸುಲಭ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ",

    eligibleTitle: "ನೀಡಿದ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ನೀವು ಅರ್ಹರಾಗಿದ್ದೀರಿ",
    eligibleSub: "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಈ ಯೋಜನೆಗೆ ನಿಗದಿಪಡಿಸಿದ ಅಧಿಕೃತ ಆದಾಯ ಮತ್ತು ಶೈಕ್ಷಣಿಕ ಷರತ್ತುಗಳನ್ನು ಪೂರೈಸುತ್ತದೆ.",
    notEligibleTitle: "ನೀವು ಪ್ರಸ್ತುತ ಅರ್ಹತಾ ಷರತ್ತುಗಳನ್ನು ಪೂರೈಸುವುದಿಲ್ಲ",
    notEligibleSub: "ಘೋಷಿತ ಪಾರಾಮೀಟರ್‌ಗಳ ಆಧಾರದ ಮೇಲೆ ಒಂದು ಅಥವಾ ಹೆಚ್ಚಿನ ನಿಯಮಗಳು ಪೂರೈಸಲ್ಪಟ್ಟಿಲ್ಲ.",
    moreInfoRequiredTitle: "ಅರ್ಹತೆ ನಿರ್ಧರಿಸಲು ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಅಗತ್ಯವಿದೆ",
    moreInfoRequiredSub: "ಮೌಲ್ಯಮಾಪನ ಪೂರ್ಣಗೊಳಿಸಲು ದಯವಿಟ್ಟು ಬಾಕಿ ಇರುವ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸಿ.",

    requiredDocuments: "ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು",
    readinessScore: "ದಾಖಲೆ ಸಿದ್ಧತೆಯ స్కోరు",
    saveDraft: "ಕರಡು ಅರ್ಜಿಯನ್ನು ಉಳಿಸಿ",
    continueApplication: "ಅರ್ಜಿಯನ್ನು ಮುಂದುವರಿಸಿ",
    disclaimer: "ಸೂಚನೆ: AccessGov AI ಅರ್ಹತೆ, ದಾಖಲೆ ಸಿದ್ಧತೆ ಮತ್ತು ಮಾರ್ಗದರ್ಶನವನ್ನು ನೀಡುತ್ತದೆ. ಅಧಿಕೃತ ಪ್ರಮಾಣಪತ್ರ ನೀಡಿಕೆಯನ್ನು ಸರ್ಕಾರಿ ಇಲಾಖೆ ನಿರ್ವಹಿಸುತ್ತದೆ."
  }
};
