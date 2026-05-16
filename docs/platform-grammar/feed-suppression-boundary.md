# Feed Suppression Boundary

작성일: 2026-05-16

---

## 구분

| 상태 | 의미 | 원인 | Feed 표시 |
|---|---|---|---|
| **Hidden** | Visibility 문제 | 권한 없음 (RLS) | 조회 자체 불가 |
| **Muted** | Preference 문제 | 사용자가 뮤트 | Feed에서 제외 |
| **Suppressed** | Delivery 정책 | cooldown/dedupe/정책 | Queue 생성 안 됨 |

## 핵심

```
Feed visibility와 Delivery suppression은 다르다
```

- **Hidden**: Identity Core / RLS 책임. Notification Engine 관여 금지.
- **Muted**: Preference Service 책임. Feed Query에서 필터링.
- **Suppressed**: Queue Manager 책임. Queue 생성 단계에서 차단.

## 현재 구현

- Hidden: Supabase RLS (기존)
- Muted: `feed_query.py` → `get_muted_sources()` 제외
- Suppressed: `queue_manager.py` → `_check_preferences()` 억제 + `runtime_notification_policy_audit` 기록
