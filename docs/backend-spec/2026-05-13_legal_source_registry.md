# Legal Source Registry
## 2026-05-13

## 목적
법제처 API에서 수집한 법령 원천 객체 저장.

## 테이블
`legal_source_registry`

## 고유 식별자
- law_source + law_id + article_id + appendix_id + form_id + revision_id
- raw_payload_hash로 변경 감지

## 상태
- ACTIVE / REVISED / REPEALED / ARCHIVED

## 변경 감지 로직
1. 수집 시 raw_payload_hash 생성
2. 기존 registry 해시와 비교
3. 해시 다르면 → legal_change_event 생성
4. 동일하면 → skip
