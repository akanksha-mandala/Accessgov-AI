import { apiClient } from './apiClient';

export interface GovernmentService {
  id: number;
  service_code: string;
  name: string;
  description: string;
  category: string;
  department: string;
  state: string;
  eligibility_rules: string;
  required_documents: string[];
  benefits: string;
  is_flagship?: boolean;
  is_active: boolean;
}

export interface EligibilityResult {
  is_eligible: boolean;
  score: number;
  matched_criteria: string[];
  missing_criteria: string[];
  recommendations: string[];
  service_name: string;
  readiness_score?: number;
  eligibility_status?: string;
  missing_documents?: string[];
  estimated_processing_days?: number;
}

export const FLAGSHIP_SERVICES: GovernmentService[] = [
  {
    id: 101,
    service_code: "SCHOLARSHIP",
    name: "Post-Matric Scholarship Assistance Scheme",
    description:
      "Financial assistance for higher education tuition fees, maintenance allowance, and book grants for eligible students.",
    category: "Education",
    department: "Department of Higher Education & Social Welfare",
    state: "All India / Tamil Nadu",
    eligibility_rules:
      "For the AccessGov AI Tamil Nadu BC/MBC/DNC demo profile: applicant should be a student from an applicable community, satisfy the Tamil Nadu requirement, and have annual parental income not exceeding Rs 2,50,000. Academic marks are recorded for profile/selection context and are not treated as a universal mandatory threshold.",
    required_documents: [
      "Income Certificate",
      "Community / Caste Certificate",
      "Aadhaar Card",
      "Previous Marksheet",
      "Student ID / Bonafide Certificate",
    ],
    benefits:
      "Scholarship assistance subject to the applicable government scheme and final departmental verification.",
    is_flagship: true,
    is_active: true,
  },

  {
    id: 102,
    service_code: "INCOME_CERTIFICATE",
    name: "Official Income & Asset Certificate",
    description:
      "Revenue Department certificate used to certify annual family income and supporting asset information for applicable government services.",
    category: "Certificates",
    department: "Revenue & Disaster Management Department",
    state: "Tamil Nadu",
    eligibility_rules:
      "Resident of Tamil Nadu. Applicant provides income and supporting information for verification. There is no income ceiling for applying for an Income Certificate.",
    required_documents: [
      "Applicant Photo",
      "Address Proof",
      "Family / Smart Card",
      "Income Supporting Document",
      "Self-Declaration",
      "Latest Salary Certificate",
      "PAN Card",
    ],
    benefits:
      "Official income certification for use in government schemes, education, welfare applications, and other purposes.",
    is_flagship: true,
    is_active: true,
  },
];

export const ALL_CURATED_SERVICES: GovernmentService[] = [
  ...FLAGSHIP_SERVICES,

  {
    id: 103,
    service_code: "HLT-CM-03",
    name: "Chief Minister Comprehensive Health Insurance",
    description:
      "Cashless medical and surgical treatment coverage in empanelled hospitals.",
    category: "Healthcare",
    department: "Health & Family Welfare Department",
    state: "Tamil Nadu",
    eligibility_rules:
      "Eligibility depends on the applicable Tamil Nadu health insurance scheme and verified household records.",
    required_documents: [
      "Smart Ration Card",
      "Income Certificate",
      "Aadhaar Card",
    ],
    benefits:
      "Cashless treatment subject to the applicable scheme and hospital eligibility.",
    is_active: true,
  },

  {
    id: 104,
    service_code: "AGR-KIS-04",
    name: "PM-Kisan Samman Nidhi Farmer Support",
    description:
      "Direct income support for eligible cultivable landholding farmer families.",
    category: "Agriculture",
    department: "Ministry of Agriculture & Farmers Welfare",
    state: "All India",
    eligibility_rules:
      "Farmer families must satisfy the applicable PM-KISAN landholding and exclusion criteria.",
    required_documents: [
      "Land Revenue Record (Patta/Chitta)",
      "Aadhaar Card",
      "Bank Account Details",
    ],
    benefits:
      "Financial assistance subject to PM-KISAN eligibility and verification.",
    is_active: true,
  },

  {
    id: 105,
    service_code: "HOU-PMAY-05",
    name: "Pradhan Mantri Awas Yojana (Urban Housing)",
    description:
      "Housing assistance for eligible urban households under the applicable PMAY-U component.",
    category: "Housing",
    department: "Ministry of Housing and Urban Affairs",
    state: "All India",
    eligibility_rules:
      "Eligibility depends on the applicable PMAY-U component, household income, housing ownership, and other scheme conditions.",
    required_documents: [
      "Aadhaar Card",
      "Income Certificate",
      "Bank Passbook",
      "Land / Site Document",
    ],
    benefits:
      "Housing assistance subject to the applicable PMAY-U component.",
    is_active: true,
  },

  {
    id: 106,
    service_code: "SOC-PNS-06",
    name: "Indira Gandhi National Old Age Pension",
    description:
      "Social security pension support for eligible senior citizens.",
    category: "Social Welfare",
    department: "Social Welfare & Women Empowerment Department",
    state: "All India / Tamil Nadu",
    eligibility_rules:
      "Age and socioeconomic eligibility are verified according to the applicable pension scheme.",
    required_documents: [
      "Aadhaar Card",
      "Age Proof",
      "BPL / Household Record",
      "Bank Account",
    ],
    benefits:
      "Pension support subject to applicable government rules.",
    is_active: true,
  },

  {
    id: 107,
    service_code: "EDU-RTE-07",
    name: "RTE Free Private School Admission",
    description:
      "Admission support under the applicable Right to Education provisions.",
    category: "Education",
    department: "School Education Department",
    state: "Tamil Nadu",
    eligibility_rules:
      "Eligibility depends on child age, disadvantaged/EWS category, income and the applicable admission rules.",
    required_documents: [
      "Birth Certificate of Child",
      "Income Certificate",
      "Community Certificate",
      "Address Proof",
    ],
    benefits:
      "Admission under the applicable RTE provisions.",
    is_active: true,
  },

  {
    id: 108,
    service_code: "CERT-COMM-08",
    name: "Community & Caste Certificate",
    description:
      "Official government certificate verifying social category for applicable education, employment and welfare purposes.",
    category: "Certificates",
    department: "Revenue Department",
    state: "Tamil Nadu",
    eligibility_rules:
      "Applicant's community and supporting records are verified by the competent authority.",
    required_documents: [
      "Parents Caste Certificate / School Transfer Certificate",
      "Aadhaar Card",
      "Address Proof",
    ],
    benefits:
      "Official community certification for applicable government purposes.",
    is_active: true,
  },
];

export const servicesService = {
  async getServices(
    category?: string,
    query?: string
  ): Promise<GovernmentService[]> {
    try {
      const params: Record<string, string> = {};

      if (category) {
        params.category = category;
      }

      if (query) {
        params.query = query;
      }

      const res = await apiClient.get('/services', { params });

      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data.map(
          (service: any): GovernmentService => ({
            id: service.id,

            service_code:
              service.code ??
              service.service_code ??
              '',

            name:
              service.title ??
              service.name ??
              '',

            description:
              service.description ??
              '',

            category:
              service.category ??
              service.service_category ??
              '',

            department:
              service.department_name ??
              service.department ??
              '',

            state:
              service.state ??
              'Tamil Nadu',

            eligibility_rules:
              service.eligibility_criteria ??
              service.eligibility_rules ??
              '',

            required_documents:
              typeof service.required_documents_summary === 'string'
                ? service.required_documents_summary
                    .split(',')
                    .map((item: string) => item.trim())
                    .filter(Boolean)
                : Array.isArray(service.required_documents)
                ? service.required_documents
                : [],

            benefits:
              service.benefits ??
              '',

            is_flagship: false,

            is_active:
              service.is_active === true ||
              service.service_status === 'active',
          })
        );
      }
    } catch (error) {
      console.error(
        'Failed to load government services:',
        error
      );
    }

    let result = ALL_CURATED_SERVICES;

    if (category) {
      result = result.filter(
        (s) =>
          s.category.toLowerCase() ===
          category.toLowerCase()
      );
    }

    if (query) {
      const q = query.toLowerCase();

      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.category.toLowerCase().includes(q)
      );
    }

    return result;
  },

  async getCategories(): Promise<string[]> {
    try {
      const res = await apiClient.get(
        '/services/categories'
      );

      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data
          .map((item: any) =>
            typeof item === 'string'
              ? item
              : item.category
          )
          .filter(Boolean);
      }
    } catch (error) {
      console.error(
        'Failed to load service categories:',
        error
      );
    }

    return [
      'Education',
      'Certificates',
      'Healthcare',
      'Social Welfare',
      'Agriculture',
      'Housing',
    ];
  },

  async getServiceById(
    id: number
  ): Promise<GovernmentService> {
    try {
      const res = await apiClient.get(
        `/services/${id}`
      );

      if (res.data) {
        const service = res.data;

        return {
          id: service.id,

          service_code:
            service.code ??
            service.service_code ??
            '',

          name:
            service.title ??
            service.name ??
            '',

          description:
            service.description ??
            '',

          category:
            service.category ??
            service.service_category ??
            '',

          department:
            service.department_name ??
            service.department ??
            '',

          state:
            service.state ??
            'Tamil Nadu',

          eligibility_rules:
            service.eligibility_criteria ??
            service.eligibility_rules ??
            '',

          required_documents:
            typeof service.required_documents_summary === 'string'
              ? service.required_documents_summary
                  .split(',')
                  .map((item: string) => item.trim())
                  .filter(Boolean)
              : Array.isArray(service.required_documents)
              ? service.required_documents
              : [],

          benefits:
            service.benefits ??
            '',

          is_flagship: false,

          is_active:
            service.is_active === true ||
            service.service_status === 'active',
        };
      }
    } catch (error) {
      console.error(
        'Failed to load service details:',
        error
      );
    }

    const found =
      ALL_CURATED_SERVICES.find(
        (s) => s.id === id
      );

    return (
      found ||
      FLAGSHIP_SERVICES[0]
    );
  },

  async checkEligibility(
    serviceId: number,
    answers: Record<string, any>
  ): Promise<EligibilityResult> {
    const targetService =
      ALL_CURATED_SERVICES.find(
        (s) => s.id === serviceId
      ) ||
      FLAGSHIP_SERVICES[0];

    /*
     * IMPORTANT:
     *
     * The frontend uses curated service IDs:
     *   101 = Scholarship
     *   102 = Income Certificate
     *
     * The backend database currently uses:
     *   1 = Scholarship
     *   2 = Income Certificate
     *
     * Therefore we explicitly map the curated frontend
     * service to the backend service ID.
     */

    let backendServiceId = serviceId;

    if (targetService.service_code === 'SCHOLARSHIP') {
      backendServiceId = 1;
    } else if (
      targetService.service_code === 'INCOME_CERTIFICATE'
    ) {
      backendServiceId = 2;
    }

    /*
     * IMPORTANT:
     *
     * We also send service_code explicitly.
     *
     * This prevents the backend eligibility engine from
     * falling back to the generic-service branch if the
     * database service lookup does not resolve correctly.
     */

    const backendServiceCode =
      targetService.service_code;

    try {
      const payload = {
        service_id: backendServiceId,

        service_code:
          backendServiceCode,

        annual_income:
          answers.income ??
          answers.annual_income ??
          null,

        marks:
          answers.marks ??
          null,

        caste_category:
          answers.category ??
          answers.caste_category ??
          null,

        state:
          answers.state ??
          'Tamil Nadu',

        is_student:
          answers.is_student ??
          true,

        occupation:
          answers.occupation ??
          'Student',

        age:
          answers.age ??
          null,

        gender:
          answers.gender ??
          null,

        disability_percentage:
          answers.disability_percentage ??
          0,

        is_disabled:
          answers.is_disabled ??
          false,

        district:
          answers.district ??
          null,

        marital_status:
          answers.marital_status ??
          null,

        has_land:
          answers.has_land ??
          false,

        uploaded_document_types:
          answers.uploaded_document_types ??
          [],
      };

      console.log(
        'AccessGov eligibility request:',
        payload
      );

      console.log(
        'AccessGov eligibility service mapping:',
        {
          frontend_service_id: serviceId,
          backend_service_id: backendServiceId,
          backend_service_code: backendServiceCode,
        }
      );

      const res = await apiClient.post(
        '/services/eligibility-check',
        payload
      );

      if (res.data) {
        const data = res.data;

        console.log(
          'AccessGov eligibility response:',
          data
        );

        return {
          is_eligible:
            Boolean(data.eligible),

          score:
            Number(
              data.eligibility_score ?? 0
            ),

          matched_criteria:
            Array.isArray(
              data.matched_rules
            )
              ? data.matched_rules
              : [],

          missing_criteria: [
            ...(Array.isArray(
              data.missing_conditions
            )
              ? data.missing_conditions
              : []),

            ...(Array.isArray(
              data.missing_documents
            )
              ? data.missing_documents.map(
                  (doc: string) =>
                    `Required document missing: ${doc}`
                )
              : []),

            ...(Array.isArray(
              data.disqualification_reasons
            )
              ? data.disqualification_reasons
              : []),
          ],

          recommendations:
            Array.isArray(data.next_steps)
              ? data.next_steps
              : [],

          service_name:
            targetService.name,

          readiness_score:
            Number(
              data.readiness_score ?? 0
            ),

          eligibility_status:
            data.eligibility_status ??
            '',

          missing_documents:
            Array.isArray(
              data.missing_documents
            )
              ? data.missing_documents
              : [],

          estimated_processing_days:
            Number(
              data.estimated_processing_days ??
              0
            ),
        };
      }

      throw new Error(
        'Eligibility API returned an empty response.'
      );
    } catch (error) {
      console.error(
        'Eligibility API failed:',
        error
      );

      return {
        is_eligible: false,

        score: 0,

        matched_criteria: [],

        missing_criteria: [
          'Eligibility service could not be reached. Please retry.',
        ],

        recommendations: [
          'Check that the AccessGov AI backend is running.',
          'Retry the eligibility evaluation.',
        ],

        service_name:
          targetService.name,

        readiness_score: 0,

        eligibility_status:
          'Evaluation Unavailable',

        missing_documents: [],

        estimated_processing_days: 0,
      };
    }
  },
};
