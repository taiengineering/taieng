import { useCallback, useState } from 'react';
import type { CreatePartnerSubmissionRequest, PartnerType } from '../../partner-registration.types';

const API = import.meta.env?.VITE_API_URL ?? 'https://api.taieng.co.kr';

/**
 * 최소 기능: POST 제출
 * 추후: draft 저장, PATCH 보완, 업로드 프리사인 연동
 */
export function usePartnerSubmission(partnerType: PartnerType) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(
    async (body: CreatePartnerSubmissionRequest) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API}/api/v1/partner-submissions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(localStorage.getItem('access_token')
              ? { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
              : {}),
          },
          body: JSON.stringify({ ...body, partner_type: partnerType }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || err.message || `HTTP ${res.status}`);
        }
        return await res.json();
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : '제출에 실패했습니다.';
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [partnerType]
  );

  return { submit, loading, error };
}
