# AlimTalk Delivery Contract

작성일: 2026-05-17
범위: 카카오 알림톡 = 비즈 전달 채널

---

## 목적

| 용도 | 예시 |
|---|---|
| Billing | 결제 성공/실패, 청구서 |
| Auth | 인증번호, 비밀번호 재설정 |
| Contract | 계약 체결/해지 |
| Subscription | 구독 만료/갱신 |
| Legal Notice | 이용약관 변경 |

---

## 포함

| 항목 | 설명 |
|---|---|
| template_key | 카카오 승인 템플릿 ID |
| fallback_sms | 알림톡 실패 시 SMS fallback |
| biz_channel | 카카오 비즈 채널 ID |
| delivery_audit | 발송 결과 기록 |
| variable_binding | 템플릿 변수 치환 |

---

## 금지

| 금지 | 이유 |
|---|---|
| Operational severity 판단 | Notification 영역 |
| Workflow 판단 | Notification 영역 |
| 친구톡 발송 | 알림톡 전용 (친구톡 API 금지) |

---

## Adapter Interface

```python
def send(message: str, context: dict) -> Tuple[bool, Optional[str]]:
    # context: {template_key, phone, variables, fallback_sms}
```

---

## 주의

카카오 알림톡은 **카카오 API**를 사용하지만, TAI 정책상 **Kakao API 사용 금지** 대상에서 제외.
알림톡은 카카오 비즈메시지 API로, 주소검색/지도/로그인 등과 다른 서비스.
사용 전 대표님 최종 확인 필수.
