# Gmail Delivery Contract

작성일: 2026-05-17
범위: Gmail = Delivery Channel only

---

## 역할

**Gmail은 전달 채널이다.** 지능 금지.

---

## 포함

| 항목 | 설명 |
|---|---|
| SMTP / Gmail API | 메일 발송 전송 |
| Retry | 발송 실패 시 재시도 (Runtime retry 사용) |
| Timeout | SMTP 연결 timeout |
| Audit | delivery result 기록 (timeline + policy_audit) |
| Template Projection | payload.title + payload.body → HTML 본문 |

---

## 금지

| 금지 | 이유 |
|---|---|
| Inbox read | 수신함 읽기 금지 |
| Mail intelligence | AI 메일 분석 금지 |
| Threading truth | 메일 스레드 관리 금지 |
| Operator state | 운영 상태 판단 금지 |

---

## 용도

- Digest 요약 메일 (일간/주간)
- 공식 공지 (이용약관, 정책 변경)
- 청구서/영수증
- 계약서 발송

---

## Adapter Interface

```python
def send(message: str, context: dict) -> Tuple[bool, Optional[str]]:
    # context: {to_email, subject, html_body, attachments}
```
