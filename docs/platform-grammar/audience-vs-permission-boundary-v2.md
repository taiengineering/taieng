# Audience vs Permission Boundary v2

작성일: 2026-05-17
범위: Notification Engine · 책임 경계

---

## 영역 구분

| 영역 | 책임 | 소유자 |
|---|---|---|
| **Audience** | 전달 대상 결정 | Notification Engine |
| **Permission** | 접근 허용 판단 | Identity Core (Phase 2) |
| **Visibility** | 조회 가능 범위 | RLS / Tenant Layer |

---

## 핵심 원칙

**받는다고 해서 모두 볼 수 있는 것은 아니다.**

---

## 예시

| 상황 | Audience | Permission | 결과 |
|---|---|---|---|
| 안전관리자에게 점검 알림 | ✅ 전달 | ✅ 조회 가능 | 정상 |
| 작업자에게 결제 알림 | ✅ 전달 | ❌ 결제 조회 불가 | 알림만 수신, 상세 접근 불가 |
| 타 회사 사용자 | ❌ 전달 대상 아님 | ❌ | 미수신 |

---

## Notification Engine의 책임 한계

- ✅ audience_key → actor list resolve
- ✅ tenant_id 기반 필터링
- ❌ role 권한 계산
- ❌ 데이터 접근 제어
- ❌ RLS 정책 설정
