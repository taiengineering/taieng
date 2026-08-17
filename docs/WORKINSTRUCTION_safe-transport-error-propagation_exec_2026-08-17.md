# 실행 지시서 — safe 전송부 ㉮ 예외 전파 (Cursor/Claude Code)

> 2026-08-17 · 승인: DECISION_transport-a-approved · 근거: WORKORDER_safe-transport-error-propagation rev.2
> 대상 `taiengineering/tai-admin` · `vue3/src/...` (safe.taieng.co.kr, main)
> **원자적 변경** — 전송부와 이관 4파일을 한 커밋으로. 따로 배포하면 위험성평가 409 가 깨진다.
> 착수 조건: safe 전송부용 **별도 Goal** 을 연 뒤 시작(엔진/헬프센터 Goal 밖).

---

## 1. 전송부 — `vue3/src/composables/useTaiApi.ts`

### `request()` 마지막 반환부 교체
```ts
// 변경 전
    return res.json().catch(() => undefined)

// 변경 후
    const data = await res.json().catch(() => undefined)
    if (!res.ok) {
      const detail = (data as any)?.detail
      const msg =
        (detail && typeof detail === 'object' && detail.message) ||
        (typeof detail === 'string' && detail) ||
        (data as any)?.message ||
        `요청이 실패했습니다 (${res.status})`
      throw Object.assign(new Error(msg), { status: res.status, body: data })
    }
    return data
```
- 401 조기 반환·`DEMO_READONLY` throw·토큰 없음 분기는 **그대로**.
- 메시지 우선순위: `body.detail.message` → `body.detail`(문자열) → `body.message` → 상태코드 기본문구.

### `upload()` — 동일 적용
`fetch` 뒤에 `if (!res.ok)` 이면 본문 파싱해 위와 같은 형태로 throw. (지금은 실패가 성공으로 보임)

### `download()` — **손대지 말 것** (이미 `if (!res.ok) return false`)

### 계약 주석 갱신 (승인됨)
```ts
// 공개 계약: request(method, endpoint, body?) -> Promise<any>
//   실패(res.ok=false) 시 Error 를 throw 한다 { status, body }. list(endpoint) -> Promise<{items,total}>
```

## 2. 이관 4파일 — 인라인 `res?.detail` → `catch (e) { e.body?.detail }`

㉮ 이후 실패 시 `res` 가 반환되지 않고 throw 되므로, 아래 4곳의 인라인 detail 판독을 catch 로 옮긴다.
**나머지 `res?.data` 44곳/30파일은 손대지 않는다** — 기존 catch 가 자동 소생.

### ① `pages/risk-assessment-detail/useRiskAssessmentDetail.ts` 【회귀 금지 — 안전장치】
```ts
// 변경 전 (성공 경로 안에서 인라인 판독)
if (res?.detail) {
  completeBlock.value = typeof res.detail === 'object' ? res.detail : { message: String(res.detail) }
  toast.show('warning', completeBlock.value?.message || '아직 완료할 수 없습니다.')
  return
}

// 변경 후 (해당 요청의 catch 로 이동)
catch (e: any) {
  if (e.message === 'DEMO_READONLY') return
  const detail = e.body?.detail
  if (detail) {
    completeBlock.value = typeof detail === 'object' ? detail : { message: String(detail) }
    toast.show('warning', completeBlock.value?.message || '아직 완료할 수 없습니다.')
    return
  }
  toast.show('error', e.message || '완료 처리에 실패했습니다.')
}
```
→ [평가 완료 처리] 시 **고시 제12조제3항 미해결 요인 목록이 버튼 아래에 지금과 동일하게** 나와야 함(완료판정 2번).

### ②③④ 나머지 3파일 — 같은 패턴(거절 사유를 `e.body?.detail` 에서 읽어 표기)
- `pages/risk-assessment-scale/useRiskAssessmentScale.ts` — 척도 저장 거절 사유
- `pages/risk-assessment-list/useRiskAssessmentList.ts` — 목록 단계 거절 사유
- `pages/holiday-calendar/useHolidayCalendar.ts` — 휴일 등록 거절 사유

## 3. DEMO_READONLY 노출 차단 — `pages/education-list/useEducationAssignPanel.ts`
`submit()` 의 catch 에서 `err?.message` 를 토스트에 그대로 띄우므로, 데모 도메인에서 `DEMO_READONLY` 가 노출됨.
```ts
catch (err: any) {
  if (err?.message === 'DEMO_READONLY') return   // 이미 안내된 차단 — 조용히 삼킴
  showToast('error', err?.message || '배정에 실패했습니다.')
}
```
(이 catch 는 ㉮ 이후 저절로 살아나 서버 거절도 표기하게 됨 — 별도 이관 불필요.)

## 4. 완료 판정 — 라이브 관측 3, 셋 다 만족
1. 교육 이수 처리에서 서버 거절 → **실패 문구** 표기(「완료되었습니다」 안 뜸).
2. 위험성평가 미해결 요인 남기고 [완료 처리] → **경고 + 버튼 아래 미해결 요인 목록**(지금과 동일 — 안전장치).
3. 목록 조회 실패 상태로 점검 캘린더·평가 척도 설정 열기 → 빈/첫사용 화면이 아니라 **오류 표시**.

**2번이 안전장치다. 1·3만 되고 2가 깨지면 완료 아님.**

## 5. 반영 후 헬프센터 통지
- `TASK-education-assign` 의 danger 경고(「성공 문구는 보증이 아니다」) 제거
- 각 화면 문서의 「실패와 빈 결과 구분 불가」 안내 제거
- 계약 대조 탈락 6화면 재대조 대상 전환
