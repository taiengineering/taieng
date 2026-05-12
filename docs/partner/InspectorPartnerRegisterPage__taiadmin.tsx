import { useState } from 'react';
import type { InspectorDetail, PartnerCommon } from '../partner-registration.types';
import { SectionCard } from './components/SectionCard';
import { StepperLayout } from './components/StepperLayout';

const STEPS = [
  { id: 'intro', label: '등록 유형·소개' },
  { id: 'scope', label: '선임 범위' },
  { id: 'cert', label: '자격·경력' },
  { id: 'terms', label: '약관' },
];

/** 선임기술자·선임대행 — 전문직 톤 (필드는 types 기준 확장) */
export function InspectorPartnerRegisterPage() {
  const [step, setStep] = useState(0);
  const [common, setCommon] = useState<Partial<PartnerCommon>>({
    manager_name: '',
    phone: '',
    email: '',
    introduction: '',
    service_regions: [],
    tax_invoice_available: true,
  });
  const [detail, setDetail] = useState<Partial<InspectorDetail>>({
    registration_kind: 'INDIVIDUAL',
    appointment_fields: [],
    industry_segments: [],
    activity_regions: [],
    monthly_contract_ok: false,
    short_consult_ok: false,
    site_visit_ok: false,
    certificate_type: '',
    career_years: 0,
    task_scope_description: '',
  });

  return (
    <StepperLayout
      title="선임기술자 · 선임대행 등록"
      subtitle="자격과 선임 가능 범위를 등록해 주십시오. 제출 후 내부 검증을 거칩니다."
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
            className="rounded-lg bg-indigo-900 px-5 py-2.5 text-sm font-medium text-white"
            onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}
          >
            {step < STEPS.length - 1 ? '다음' : '제출 (연동 전)'}
          </button>
        </div>
      }
    >
      {step === 0 && (
        <SectionCard title="등록 유형" description="개인 기술자와 대행업체의 입력 항목이 일부 다릅니다.">
          <div className="flex gap-4">
            {(['INDIVIDUAL', 'AGENCY'] as const).map((k) => (
              <label
                key={k}
                className={`flex-1 cursor-pointer rounded-lg border p-4 ${
                  detail.registration_kind === k
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-slate-200'
                }`}
              >
                <input
                  type="radio"
                  name="kind"
                  className="sr-only"
                  checked={detail.registration_kind === k}
                  onChange={() => setDetail({ ...detail, registration_kind: k })}
                />
                <div className="font-semibold text-slate-900">
                  {k === 'INDIVIDUAL' ? '개인 기술자' : '선임 대행 업체'}
                </div>
              </label>
            ))}
          </div>
          <label className="mt-4 block text-sm">
            소개
            <textarea
              className="mt-1 w-full rounded border border-slate-200 p-2"
              rows={4}
              value={common.introduction}
              onChange={(e) => setCommon({ ...common, introduction: e.target.value })}
            />
          </label>
        </SectionCard>
      )}

      {step === 1 && (
        <SectionCard title="선임 가능 분야·지역">
          <p className="text-sm text-slate-600">
            `partner-registration.types.ts`의 AppointmentField, IndustrySegment를
            체크박스/멀티셀렉트로 매핑하세요.
          </p>
        </SectionCard>
      )}

      {step === 2 && (
        <SectionCard title="자격·경력">
          <input
            className="w-full rounded border p-2"
            placeholder="자격 종류"
            value={detail.certificate_type}
            onChange={(e) => setDetail({ ...detail, certificate_type: e.target.value })}
          />
          <input
            type="number"
            className="mt-2 w-full rounded border p-2"
            placeholder="경력 연수"
            value={detail.career_years || ''}
            onChange={(e) =>
              setDetail({ ...detail, career_years: Number(e.target.value) || 0 })
            }
          />
        </SectionCard>
      )}

      {step === 3 && (
        <SectionCard title="약관 동의">파트너 약관·개인정보 동의 체크박스 배치.</SectionCard>
      )}
    </StepperLayout>
  );
}
