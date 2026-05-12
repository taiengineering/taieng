/**
 * TAI 파트너 등록 — 공통 + 유형별 상세
 * DB: partner_submissions.partner_type + common 컬럼(또는 JSON) + detail JSON
 */

export type PartnerType = 'REPAIR_CONTRACTOR' | 'APPOINTED_EXPERT' | 'SAFETY_AGENCY';

export type SubmissionStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'NEEDS_SUPPLEMENT'
  | 'APPROVED'
  | 'REJECTED';

/** ── 공통 (모든 유형) ── */
export interface PartnerCommon {
  legal_name: string;
  ceo_name?: string;
  manager_name: string;
  phone: string;
  email: string;
  business_number?: string;
  address?: string;
  address_detail?: string;
  service_regions: string[];
  website_url?: string;
  introduction: string;
  logo_url?: string;
  profile_image_url?: string;
  tax_invoice_available: boolean;
  terms_agreed_at?: string; // ISO
  privacy_agreed_at?: string;
}

/** ── 수선업체 상세 ── */
export type RepairTrade =
  | 'FIRE'
  | 'ELECTRIC'
  | 'GAS'
  | 'ARCHITECTURE_FACILITY'
  | 'MECHANICAL'
  | 'HAZMAT'
  | 'OTHER';

export interface RepairDetail {
  trades: RepairTrade[];
  other_trade_label?: string;
  work_scope_description: string;
  construction_regions: string[];
  emergency_dispatch: boolean;
  quote_method: 'VISIT' | 'REMOTE' | 'BOTH';
  as_available: boolean;
  work_hours_description?: string;
  license_file_urls?: string[];
  insurance_enrolled: boolean;
  technical_staff_count?: number;
  major_achievements?: string;
  portfolio_image_urls?: string[];
  avg_price_range?: { min: number; max: number; currency: 'KRW' };
  minimum_dispatch_fee?: number;
}

/** ── 선임기술자 / 선임대행 ── */
export type InspectorRegistrationKind = 'INDIVIDUAL' | 'AGENCY';

export type AppointmentField =
  | 'SAFETY'
  | 'HEALTH'
  | 'FIRE'
  | 'ELECTRIC'
  | 'GAS'
  | 'BUILDING'
  | 'ENERGY'
  | 'OTHER';

export type IndustrySegment =
  | 'MANUFACTURING'
  | 'CONSTRUCTION'
  | 'BUILDING'
  | 'SPECIAL_FACILITY'
  | 'OTHER';

export interface InspectorDetail {
  registration_kind: InspectorRegistrationKind;
  appointment_fields: AppointmentField[];
  industry_segments: IndustrySegment[];
  activity_regions: string[];
  monthly_contract_ok: boolean;
  short_consult_ok: boolean;
  site_visit_ok: boolean;
  certificate_type: string;
  certificate_number?: string;
  certificate_obtained_at?: string;
  career_years: number;
  affiliation?: string;
  task_scope_description: string;
  monthly_facility_capacity?: number;
  avg_contract_price_range?: { min: number; max: number; currency: 'KRW' };
  career_highlights?: string;
}

/** ── 안전관리대행업체 ── */
export type SafetyAgencyKind =
  | 'AGENCY_INSTITUTION'
  | 'CONSULTING'
  | 'RISK_ASSESSMENT'
  | 'EDUCATION_COMBO'
  | 'OTHER';

export type ContractForm = 'MONTHLY' | 'QUARTERLY' | 'PROJECT';

export interface SafetyAgencyDetail {
  agency_kind: SafetyAgencyKind;
  agency_kind_other_label?: string;
  services_offered: string[];
  target_industries: string[];
  service_regions: string[];
  contract_forms: ContractForm[];
  registration_proof_file_urls?: string[];
  total_staff_count?: number;
  dedicated_engineer_count?: string;
  qualification_summary?: string;
  education_available?: boolean;
  insurance_enrolled?: boolean;
  monthly_facility_capacity?: number;
  avg_response_hours?: number;
  periodic_visit_per_month?: number;
  online_management_ok?: boolean;
  report_provided?: boolean;
  saas_integration_ok?: boolean;
  avg_price_range?: { min: number; max: number; currency: 'KRW' };
  major_client_industries?: string;
  case_study_summary?: string;
  brochure_pdf_url?: string;
}

export type PartnerDetail = RepairDetail | InspectorDetail | SafetyAgencyDetail;

/** ── 제출 루트 엔티티 ── */
export interface PartnerSubmission<T extends PartnerDetail = PartnerDetail> {
  id: string;
  partner_type: PartnerType;
  status: SubmissionStatus;
  common: PartnerCommon;
  detail: T;
  schema_version: number;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

/** 관리자 전용 (API에서 role 기반 분리) */
export interface PartnerSubmissionAdmin extends PartnerSubmission {
  admin_note?: string;
  supplement_requested_fields?: string[];
  supplement_note?: string;
  reject_reason?: string;
  reviewer_id?: string;
}

/** 생성/수정 요청 (클라이언트) */
export interface CreatePartnerSubmissionRequest {
  partner_type: PartnerType;
  common: PartnerCommon;
  detail: PartnerDetail;
  submit?: boolean;
}

export interface PatchPartnerSubmissionRequest {
  common?: Partial<PartnerCommon>;
  detail?: Partial<PartnerDetail>;
  submit?: boolean;
}
