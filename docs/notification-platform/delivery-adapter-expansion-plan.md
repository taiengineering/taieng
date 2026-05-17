# Delivery Adapter Expansion Plan

작성일: 2026-05-17
범위: Adapter 확장 계획

---

## 현재 Adapter

| Adapter | 파일 | 상태 | 단계 |
|---|---|---|---|
| IN_APP | `adapters/in_app.py` | ✅ Active | **operational** |
| SMS | `adapters/sms.py` | ✅ Active | **compat** |
| TELEGRAM | `adapters/telegram.py` | ✅ Active | **compat** |
| PUSH | `adapters/push.py` v2.0 | ✅ Active | **compat** |

---

## 추가 예정

| Adapter | 파일 | 단계 | 의존성 |
|---|---|---|---|
| Gmail | `adapters/gmail.py` | **phase2** | smtplib + Gmail App Password |
| AlimTalk | `adapters/alimtalk.py` | **phase2** | 카카오 비즈메시지 API |
| Slack | `adapters/slack.py` | **phase2** | Slack Incoming Webhook |

---

## Adapter 단계

| 단계 | 설명 |
|---|---|
| compat | 기존 infra 위임 |
| operational | 독립 동작 + retry + audit |
| platformized | channel_registry + fallback + metrics |

---

## 공통 Interface

```python
def send(message: str, context: dict) -> Tuple[bool, Optional[str]]:
```

모든 adapter는 이 interface 준수 필수.
