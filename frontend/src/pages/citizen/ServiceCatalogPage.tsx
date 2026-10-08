import React, { useEffect, useState } from 'react';
import {
  servicesService,
  GovernmentService,
} from '../../services/servicesService';
import { Link } from 'react-router-dom';
import { Search, ArrowRight } from 'lucide-react';
import { useI18n } from '../../hooks/useI18n';

export const ServiceCatalogPage: React.FC = () => {
  const [services, setServices] = useState<GovernmentService[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] =
    useState<string>('');
  const [searchQuery, setSearchQuery] =
    useState<string>('');
  const [loading, setLoading] = useState(true);

  const { language } = useI18n();

  const labels: Record<
    string,
    Record<string, string>
  > = {
    en: {
      title: 'Government Service Catalog',
      sub: 'Search and discover central & state welfare schemes',
      search: 'Search scheme name...',
      all: 'All Schemes',
      required: 'Required Documents:',
      loading: 'Loading services...',
      empty:
        'No government schemes found matching your search.',
      view: 'View Details',
    },

    ta: {
      title: 'அரசு சேவை பட்டியல்',
      sub: 'மத்திய மற்றும் மாநில நலத்திட்டங்களைத் தேடி கண்டறியுங்கள்',
      search: 'திட்டத்தின் பெயரைத் தேடுங்கள்...',
      all: 'அனைத்து திட்டங்கள்',
      required: 'தேவையான ஆவணங்கள்:',
      loading: 'சேவைகள் ஏற்றப்படுகின்றன...',
      empty:
        'உங்கள் தேடலுக்கு பொருந்தும் அரசு திட்டங்கள் எதுவும் கிடைக்கவில்லை.',
      view: 'விவரங்களைப் பார்க்கவும்',
    },

    te: {
      title: 'ప్రభుత్వ సేవల జాబితా',
      sub: 'కేంద్ర మరియు రాష్ట్ర సంక్షేమ పథకాలను వెతికి కనుగొనండి',
      search: 'పథకం పేరును వెతకండి...',
      all: 'అన్ని పథకాలు',
      required: 'అవసరమైన పత్రాలు:',
      loading: 'సేవలు లోడ్ అవుతున్నాయి...',
      empty:
        'మీ శోధనకు సరిపోలే ప్రభుత్వ పథకాలు ఏవీ లేవు.',
      view: 'వివరాలు చూడండి',
    },

    hi: {
      title: 'सरकारी सेवा सूची',
      sub: 'केंद्र और राज्य कल्याण योजनाएं खोजें',
      search: 'योजना का नाम खोजें...',
      all: 'सभी योजनाएं',
      required: 'आवश्यक दस्तावेज:',
      loading: 'सेवाएं लोड हो रही हैं...',
      empty:
        'आपकी खोज से मेल खाने वाली कोई सरकारी योजना नहीं मिली।',
      view: 'विवरण देखें',
    },

    kn: {
      title: 'ಸರ್ಕಾರಿ ಸೇವೆಗಳ ಪಟ್ಟಿ',
      sub: 'ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ಕಲ್ಯಾಣ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ',
      search: 'ಯೋಜನೆಯ ಹೆಸರನ್ನು ಹುಡುಕಿ',
      all: 'ಎಲ್ಲಾ ಯೋಜನೆಗಳು',
      required: 'ಅಗತ್ಯ ದಾಖಲೆಗಳು:',
      loading: 'ಸೇವೆಗಳು ಲೋಡ್ ಆಗುತ್ತಿವೆ...',
      empty:
        'ನಿಮ್ಮ ಹುಡುಕಾಟಕ್ಕೆ ಹೊಂದುವ ಯಾವುದೇ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
      view: 'ವಿವರಗಳನ್ನು ನೋಡಿ',
    },
  };

  const serviceTranslations: Record<
    string,
    Record<string, string>
  > = {
    'SCHOLARSHIP': {
      en: 'Scholarship',
      ta: 'உதவித்தொகை',
      te: 'విద్యార్థి వేతనం',
      hi: 'छात्रवृत्ति',
      kn: 'ವಿದ್ಯಾರ್ಥಿವೇತನ',
    },

    'INCOME_CERTIFICATE': {
      en: 'Income Certificate',
      ta: 'வருமானச் சான்றிதழ்',
      te: 'ఆదాయ ధృవీకరణ పత్రం',
      hi: 'आय प्रमाण पत्र',
      kn: 'ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ',
    },
  };

  const categoryTranslations: Record<
    string,
    Record<string, string>
  > = {
    Education: {
      en: 'Education',
      ta: 'கல்வி',
      te: 'విద్య',
      hi: 'शिक्षा',
      kn: 'ಶಿಕ್ಷಣ',
    },

    Certificates: {
      en: 'Certificates',
      ta: 'சான்றிதழ்கள்',
      te: 'ధృవీకరణ పత్రాలు',
      hi: 'प्रमाण पत्र',
      kn: 'ಪ್ರಮಾಣ ಪತ್ರಗಳು',
    },
  };

  const getLocalizedServiceName = (
    service: GovernmentService
  ): string => {
    const translation =
      serviceTranslations[service.service_code];

    if (translation) {
      return (
        translation[language] ||
        translation.en
      );
    }

    return service.name;
  };

  const getLocalizedCategory = (
    category: string
  ): string => {
    const translation =
      categoryTranslations[category];

    if (translation) {
      return (
        translation[language] ||
        translation.en
      );
    }

    return category;
  };

  const l = labels[language] || labels.en;

  useEffect(() => {
    async function load() {
      setLoading(true);

      try {
        const [svc, cat] = await Promise.all([
          servicesService.getServices(
            selectedCategory,
            searchQuery
          ),
          servicesService.getCategories(),
        ]);

        setServices(svc);
        setCategories(cat);
      } catch (error) {
        console.error(
          'Failed to load services:',
          error
        );

        setServices([]);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [selectedCategory, searchQuery]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800">
            {l.title}
          </h1>

          <p className="text-xs text-slate-500">
            {l.sub}
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />

          <input
            type="text"
            value={searchQuery}
            onChange={(e) =>
              setSearchQuery(e.target.value)
            }
            placeholder={l.search}
            className="w-full text-xs border border-slate-300 rounded-md pl-9 pr-3 py-2 focus:outline-none focus:border-gov-blue"
          />
        </div>
      </div>

      <div className="flex items-center space-x-2 overflow-x-auto pb-2 text-xs">
        <button
          onClick={() => setSelectedCategory('')}
          className={`px-3 py-1.5 rounded-full font-medium transition shrink-0 ${
            selectedCategory === ''
              ? 'bg-gov-blue text-white font-semibold'
              : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          {l.all}
        </button>

        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() =>
              setSelectedCategory(cat)
            }
            className={`px-3 py-1.5 rounded-full font-medium transition shrink-0 ${
              selectedCategory === cat
                ? 'bg-gov-blue text-white font-semibold'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {getLocalizedCategory(cat)}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-xs text-slate-400 py-8 text-center">
          {l.loading}
        </p>
      ) : services.length === 0 ? (
        <div className="bg-white p-8 rounded-lg border border-slate-200 text-center text-xs text-slate-500">
          {l.empty}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((svc) => (
            <div
              key={svc.id}
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] bg-blue-50 text-gov-blue font-semibold px-2 py-0.5 rounded">
                    {getLocalizedCategory(
                      svc.category
                    )}
                  </span>

                  <span className="text-[10px] text-slate-400 font-mono">
                    {svc.service_code}
                  </span>
                </div>

                <h3 className="font-bold text-sm text-slate-800">
                  {getLocalizedServiceName(svc)}
                </h3>

                <p className="text-xs text-slate-500 mt-2 line-clamp-3">
                  {svc.description}
                </p>

                {svc.required_documents && (
                  <div className="mt-3 pt-3 border-t border-slate-100">
                    <p className="text-[10px] font-bold text-slate-400 uppercase">
                      {l.required}
                    </p>

                    <div className="flex flex-wrap gap-1 mt-1">
                      {svc.required_documents.map(
                        (doc, i) => (
                          <span
                            key={i}
                            className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded"
                          >
                            {doc}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[10px] text-slate-400">
                  {svc.state}
                </span>

                <Link
                  to={`/services/${svc.id}`}
                  className="text-xs text-gov-blue font-bold hover:underline flex items-center"
                >
                  {l.view}

                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ServiceCatalogPage;