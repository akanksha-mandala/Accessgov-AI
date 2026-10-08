import {LanguageCode,useAccessibility} from '../context/AccessibilityContext';
import {TRANSLATIONS,Translations} from '../i18n/translations';
export const useI18n=()=>{const {selectedLanguage}=useAccessibility();const dict:Translations=TRANSLATIONS[selectedLanguage];return {language:selectedLanguage,t:(key:keyof Translations)=>dict[key]||TRANSLATIONS.en[key]||String(key)};};
