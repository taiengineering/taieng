import { useState } from 'react';
import type { PartnerCommon, SafetyAgencyDetail } from '../partner-registration.types';
import { SectionCard } from './components/SectionCard';
import { StepperLayout } from './components/StepperLayout';

const STEPS = [
  { id: 'org', label: '기관 소개' },
  { id: 'svc', label: '서비스·대상' },
  { id: 'compliance', label: '인력·증빙' },
  { id: 'terms', label: '약관' },
];

/** 안전관리대행업체 — 기관·컨설팅 톤 */
export function SafetyAgencyRegisterPage() {
  const [step, setStep] = useState(0);
  const [common, setCommon] = useState<Partial<PartnerCommon>>({});
  const [detail, setDetail] = useState<Partial<SafetyAgencyDetail>>({
    agency_kind: 'AGENCY_INSTITUTION',
    services_offered: [],
    target_industries: [],
    service_regions: [],
    contract_forms: ['MONTHLY'],
  });

  return (
    <StepperLayout
      title="안전관리대행 파트너 등록"
      subtitle="안전관리체계 구축·대행·컨설팅 등을 제공하는 기관·법인을 모십니다."
      steps={STEPS}
      activeStep={step}
      footer={
        <div className="flex justify-between">
          <button
            type="button"
            className="text-sm text-slate-600"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
          >
            이전
          </button>
          <button
            type="button"
            className="rounded-lg bg-emerald-900 px-5 py-2.5 text-sm font-medium text-white"
            onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}
          >
            {step < STEPS.length - 1 ? '다음' : '제출 (연동 전)'}
          </button>
        </div>
      }
    >
      {step === 0 && (
        <SectionCard title="기관 유형·소개">
          <select
            className="w-full rounded border p-2"
            value={detail.agency_kind}
            onChange={(e) =>
              setDetail({
                ...detail,
                agency_kind: e.target.value as SafetyAgencyDetail['agency_kind'],
              })
            }
          >
            <option value="AGENCY_INSTITUTION">안전관리대행기관</option>
            <option value="CONSULTING">컨설팅</option>
            <option value="RISK_ASSESSMENT">위험성평가</option>
            <option value="EDUCATION_COMBO">교육 병행</option>
            <option value="OTHER">기타</option>
          </select>
          <textarea
            className="mt-4 w-full rounded border p-2"
            rows={5}
            placeholder="기관 소개 (심사·고객 안내용)"
            value={common.introduction}
            onChange={(e) => setCommon({ ...common, introduction: e.target.value })}
          />
        </SectionCard>
      )}
      {step === 1 && (
        <SectionCard title="제공 서비스·대상 업종">
          <p className="text-sm text-slate-600">
            `services_offered`, `target_industries`, `service_regions`를 태그 입력 또는
            멀티 셀렉트로 구현하세요.
          </p>
        </SectionCard>
      )}
      {step === 2 && (
        <SectionCard title="인력·등록 증빙">
          파일 업로드는 presign URL 후 `registration_proof_file_urls`에 저장.
        </SectionCard>
      )}
      {step === 3 && <SectionCard title="약관 동의">동의 체크박스.</SectionCard>}
    </StepperLayout>
  );
}
