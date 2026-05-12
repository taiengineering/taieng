import { Link } from 'react-router-dom';

const cardBase =
  'block rounded-xl border border-slate-200 bg-white p-8 shadow-sm transition hover:border-blue-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500';

/** 파트너 유형 랜딩 — 카드만 선택, 이후 전용 URL */
export function PartnerLandingPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <span className="text-lg font-semibold text-slate-800">TAI 파트너</span>
          <Link to="/" className="text-sm text-slate-500 hover:text-slate-800">
            홈으로
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-16">
        <p className="text-center text-sm font-medium uppercase tracking-wide text-blue-700">
          Partner Onboarding
        </p>
        <h1 className="mt-2 text-center text-3xl font-bold tracking-tight text-slate-900">
          TAI와 함께할 파트너를 모십니다
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-center text-slate-600">
          귀하의 전문 분야에 맞는 등록 절차로 안내합니다. 아래에서 해당 유형을 선택해 주세요.
        </p>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          <Link to="/partners/repair/register" className={cardBase}>
            <span className="text-xs font-semibold text-amber-700">현장 · 시공</span>
            <h2 className="mt-2 text-xl font-bold text-slate-900">수선·시공 업체</h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              소방·전기·설비 등 수선 및 긴급 출동 역량을 등록합니다.
            </p>
            <span className="mt-6 inline-flex text-sm font-medium text-blue-700">
              등록 시작 →
            </span>
          </Link>

          <Link to="/partners/inspector/register" className={cardBase}>
            <span className="text-xs font-semibold text-indigo-700">선임 · 자격</span>
            <h2 className="mt-2 text-xl font-bold text-slate-900">선임기술자 · 선임대행</h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              개인 기술자 또는 선임 대행 사업자로 활동하시는 경우.
            </p>
            <span className="mt-6 inline-flex text-sm font-medium text-blue-700">
              등록 시작 →
            </span>
          </Link>

          <Link to="/partners/safety-agency/register" className={cardBase}>
            <span className="text-xs font-semibold text-emerald-800">기관 · 대행</span>
            <h2 className="mt-2 text-xl font-bold text-slate-900">안전관리대행 업체</h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              안전관리체계·컨설팅·위험성평가 등 기관형 서비스를 제공하시는 경우.
            </p>
            <span className="mt-6 inline-flex text-sm font-medium text-blue-700">
              등록 시작 →
            </span>
          </Link>
        </div>

        <p className="mt-12 text-center text-xs text-slate-500">
          제출하신 내용은 내부 심사 후 승인됩니다. 사실과 다른 정보는 거절 사유가 될 수 있습니다.
        </p>
      </main>
    </div>
  );
}
