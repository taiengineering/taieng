import type { ReactNode } from 'react';

export interface StepMeta {
  id: string;
  label: string;
}

interface StepperLayoutProps {
  title: string;
  subtitle: string;
  steps: StepMeta[];
  activeStep: number;
  children: ReactNode;
  footer?: ReactNode;
}

/** B2B 단계형 레이아웃 — 좌측 스텝(데스크톱) */
export function StepperLayout({
  title,
  subtitle,
  steps,
  activeStep,
  children,
  footer,
}: StepperLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <a href="/partners" className="text-sm text-slate-500 hover:text-slate-800">
            ← 유형 선택
          </a>
          <span className="text-sm font-medium text-slate-600">TAI 파트너 등록</span>
        </div>
      </header>

      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 lg:grid-cols-[220px_1fr]">
        <aside className="hidden lg:block">
          <nav className="sticky top-24 space-y-1">
            {steps.map((s, i) => (
              <div
                key={s.id}
                className={`rounded-lg px-3 py-2 text-sm ${
                  i === activeStep
                    ? 'bg-blue-50 font-semibold text-blue-900'
                    : 'text-slate-600'
                }`}
              >
                <span className="mr-2 text-slate-400">{String(i + 1).padStart(2, '0')}</span>
                {s.label}
              </div>
            ))}
          </nav>
        </aside>

        <div>
          <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
          <p className="mt-2 text-slate-600">{subtitle}</p>

          {/* 모바일: 상단 스텝 인디케이터 */}
          <div className="mt-6 flex gap-2 lg:hidden">
            {steps.map((s, i) => (
              <div
                key={s.id}
                className={`h-1 flex-1 rounded-full ${
                  i <= activeStep ? 'bg-blue-600' : 'bg-slate-200'
                }`}
                title={s.label}
              />
            ))}
          </div>

          <div className="mt-8 space-y-8">{children}</div>

          {footer && <div className="mt-10 border-t border-slate-200 pt-8">{footer}</div>}
        </div>
      </div>
    </div>
  );
}
