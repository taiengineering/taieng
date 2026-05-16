# Notification Surface Density

작성일: 2026-05-17
범위: Notification Engine · UX Density

---

## 목표

빠르게 훑기 가능해야 한다.

운영자가 Feed를 3초 이내에 파악할 수 있어야 한다.

---

## Density 규칙

1. Feed 카드 높이: 최대 80px (2줄 본문 포함)
2. Severity badge: 최소 크기 (10px font)
3. 시간 표시: 상대시간 (방금 전, 3분 전)
4. 본문: 2줄 말줄임 (ellipsis)
5. trace_id: 숨김 (터치 시 타임라인 진입)

---

## 금지

- 과도한 blinking/pulse
- 색상 과다 사용 (3색 이내: red/orange/blue)
- Alert fatigue 유발
- 각 카드에 액션 버튼 과다 배치
- Health 위젯 과도 확대
