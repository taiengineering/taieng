import { useState, type ReactNode } from 'react';
import type { PartnerCommon, RepairDetail } from '../partner-registration.types';
import { SectionCard } from './components/SectionCard';
import { StepperLayout } from './components/StepperLayout';
import { usePartnerSubmission } from './hooks/usePartnerSubmission';

const STEPS = [
  { id: 'biz', label: '사업자·연락' },
  { id: 'trade', label: '전문 분야' },
  { id: 'ops', label: '운영 조건' },
  { id: 'terms', label: '약관 동의' },
];

const initialCommon: PartnerCommon = {
  legal_name: '',
  ceo_name: '',
  manager_name: '',
  phone: '',
  email: '',
  business_number: '',
  address: '',
  service_regions: [],
  introduction: '',
  tax_invoice_available: false,
};

const initialDetail: RepairDetail = {
  trades: [],
  work_scope_description: '',
  construction_regions: [],
  emergency_dispatch: false,
  quote_method: 'REMOTE',
  as_available: false,
  insurance_enrolled: false,
};

/** 수선업체 전용 등록 — 현장·시공 톤 */
export function RepairPartnerRegisterPage() {
  const [step, setStep] = useState(0);
  const [common, setCommon] = useState<PartnerCommon>(initialCommon);
  const [detail, setDetail] = useState<RepairDetail>(initialDetail);
  const [terms, setTerms] = useState({ terms: false, privacy: false });
  const { submit, loading, error } = usePartnerSubmission('REPAIR_CONTRACTOR');

  async function handleSubmit(finalSubmit: boolean) {
    const payload = {
      partner_type: 'REPAIR_CONTRACTOR' as const,
      submit: finalSubmit,
      common: {
        ...common,
        terms_agreed_at: terms.terms ? new Date().toISOString() : undefined,
        privacy_agreed_at: terms.privacy ? new Date().toISOString() : undefined,
      },
      detail,
    };
    await submit(payload);
    alert(finalSubmit ? '접수되었습니다. 심사 후 연락드립니다.' : '임시 저장되었습니다.');
  }

  return (
    <StepperLayout
      title="수선·시공 파트너 등록"
      subtitle="긴급 출동·시공 역량을 바탕으로 현장에서 함께할 파트너를 모십니다."
      steps={STEPS}
      activeStep={step}
      footer={
        <div className="flex flex-wrap items-center justify-between gap-4">
          <button
            type="button"
            className="text-sm text-slate-600 hover:text-slate-900"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
          >
            이전
          </button>
          <div className="flex gap-3">
            {step < STEPS.length - 1 ? (
              <button
                type="button"
                className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
                onClick={() => setStep((s) => s + 1)}
              >
                다음
              </button>
            ) : (
              <>
                <button
                  type="button"
                  className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                  disabled={loading}
                  onClick={() => handleSubmit(false)}
                >
                  임시 저장
                </button>
                <button
                  type="button"
                  className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
                  disabled={loading || !terms.terms || !terms.privacy}
                  onClick={() => handleSubmit(true)}
                >
                  {loading ? '제출 중…' : '심사 요청 제출'}
                </button>
              </>
            )}
          </div>
        </div>
      }
    >
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      )}

      {step === 0 && (
        <>
          <SectionCard
            title="사업자 및 담당자"
            description="심사·연락에 사용됩니다. 사업자등록번호는 증빙 제출 시 확인합니다."
          >
            <Field label="업체명">
              <input
                className="input"
                value={common.legal_name}
                onChange={(e) => setCommon({ ...common, legal_name: e.target.value })}
              />
            </Field>
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="대표자명">
                <input
                  className="input"
                  value={common.ceo_name}
                  onChange={(e) => setCommon({ ...common, ceo_name: e.target.value })}
                />
              </Field>
              <Field label="담당자명">
                <input
                  className="input"
                  value={common.manager_name}
                  onChange={(e) => setCommon({ ...common, manager_name: e.target.value })}
                />
              </Field>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="연락처">
                <input
                  className="input"
                  value={common.phone}
                  onChange={(e) => setCommon({ ...common, phone: e.target.value })}
                />
              </Field>
              <Field label="이메일">
                <input
                  type="email"
                  className="input"
                  value={common.email}
                  onChange={(e) => setCommon({ ...common, email: e.target.value })}
                />
              </Field>
            </div>
            <Field label="사업자등록번호">
              <input
                className="input"
                value={common.business_number}
                onChange={(e) => setCommon({ ...common, business_number: e.target.value })}
              />
            </Field>
            <Field label="한 줄 소개">
              <textarea
                className="input min-h-[88px]"
                value={common.introduction}
                onChange={(e) => setCommon({ ...common, introduction: e.target.value })}
              />
            </Field>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={common.tax_invoice_available}
                onChange={(e) =>
                  setCommon({ ...common, tax_invoice_available: e.target.checked })
                }
              />
              세금계산서 발행 가능
            </label>
          </SectionCard>
        </>
      )}

      {step === 1 && (
        <SectionCard title="전문 분야" description="복수 선택 가능합니다.">
          <div className="flex flex-wrap gap-2">
            {(['FIRE', 'ELECTRIC', 'GAS', 'MECHANICAL', 'HAZMAT'] as const).map((t) => (
              <label
                key={t}
                className={`cursor-pointer rounded-full border px-3 py-1.5 text-sm ${
                  detail.trades.includes(t)
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-slate-200 text-slate-700'
                }`}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={detail.trades.includes(t)}
                  onChange={() => {
                    const set = new Set(detail.trades);
                    if (set.has(t)) set.delete(t);
                    else set.add(t);
                    setDetail({ ...detail, trades: [...set] });
                  }}
                />
                {t}
              </label>
            ))}
          </div>
          <Field label="수행 가능 공사 범위">
            <textarea
              className="input min-h-[100px]"
              value={detail.work_scope_description}
              onChange={(e) =>
                setDetail({ ...detail, work_scope_description: e.target.value })
              }
            />
          </Field>
        </SectionCard>
      )}

      {step === 2 && (
        <SectionCard title="운영 조건" description="매칭·견적 시 참고합니다.">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={detail.emergency_dispatch}
              onChange={(e) =>
                setDetail({ ...detail, emergency_dispatch: e.target.checked })
              }
            />
            긴급 출동 가능
          </label>
          <Field label="견적 방식">
            <select
              className="input"
              value={detail.quote_method}
              onChange={(e) =>
                setDetail({
                  ...detail,
                  quote_method: e.target.value as RepairDetail['quote_method'],
                })
              }
            >
              <option value="VISIT">현장 방문 견적</option>
              <option value="REMOTE">원격/서류 견적</option>
              <option value="BOTH">병행</option>
            </select>
          </Field>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={detail.as_available}
              onChange={(e) => setDetail({ ...detail, as_available: e.target.checked })}
            />
            A/S 가능
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={detail.insurance_enrolled}
              onChange={(e) =>
                setDetail({ ...detail, insurance_enrolled: e.target.checked })
              }
            />
            관련 보험 가입
          </label>
        </SectionCard>
      )}

      {step === 3 && (
        <SectionCard title="약관 동의" description="제출 시 심사 절차가 시작됩니다.">
          <label className="flex items-start gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={terms.terms}
              onChange={(e) => setTerms({ ...terms, terms: e.target.checked })}
            />
            <span>파트너 이용약관에 동의합니다. (필수)</span>
          </label>
          <label className="flex items-start gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={terms.privacy}
              onChange={(e) => setTerms({ ...terms, privacy: e.target.checked })}
            />
            <span>개인정보 수집·이용에 동의합니다. (필수)</span>
          </label>
        </SectionCard>
      )}

      <style>{`
        .input {
          width: 100%;
          border-radius: 0.5rem;
          border: 1px solid rgb(226 232 240);
          padding: 0.5rem 0.75rem;
          font-size: 0.875rem;
        }
        .input:focus {
          outline: 2px solid rgb(59 130 246);
          outline-offset: 0;
        }
      `}</style>
    </StepperLayout>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}
