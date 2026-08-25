# WP-PERSISTENCE-02A STEP-3 — EVIDENCE IDENTITY BOUNDARY

- 작성일: 2026-08-25
- 성격: 지시서 §10. 점검 사진/파일 evidence 의 source 와 경계 확정. DB SELECT only.

---

## 1. evidence source 실측 (§10)

safety_inspection_results 에 evidence 연결 컬럼이 **결과 행 자체에** 존재:
```
photo_url   text    ← 단일 파일 URL
photo_urls  jsonb   ← 복수 파일 URL 배열
```
실측 채움: 현재 8행 모두 비어있음(no). 그러나 **컬럼 구조는 존재** → evidence 연결
슬롯이 이미 결과 모델에 내장되어 있다. 새 evidence subsystem 불필요.

(추가 evidence 전용 테이블 존재 여부: 결과 행에 photo 컬럼이 이미 있어 이번 GENERAL
계약은 그것으로 충족. 별도 evidence 테이블을 새로 요구하지 않는다 — §10 "새 evidence
subsystem 금지" 준수.)

---

## 2. 두 층 분리 (지시서 §10)

```
A. RESULT DATA   = inspection_results (multi_row 배열, RESULT_PAYLOAD_CONTRACT)
B. EVIDENCE OBJECT = photo/file (URL/경로 참조)
```

- A 는 "무엇을 점검했고 결과가 무엇인가"(구조화된 결과 데이터).
- B 는 "그 근거 파일이 어디 있는가"(스토리지 객체 참조).
- 두 층을 섞지 않는다. evidence 는 **참조(URL/path)만** 저장한다.

---

## 3. binary 금지 (지시서 §10)

- 파일 binary 를 runtime_data_json 에 넣지 않는다.
- payload 에는 photo_url(text) / photo_urls(jsonb) 의 **참조 문자열만** 저장.
- 실제 파일 객체는 기존 스토리지(Supabase Storage 등)에 있고, payload 는 그 URL 을 가리킨다.

---

## 4. evidence 위치 (v1 = result item 레벨만)

evidence 참조는 result item 레벨에만 두고, 참조만 저장:
```
result item 레벨 — inspection_results[i].photo_url / photo_urls
     = 개별 점검항목의 근거 사진 (source: safety_inspection_results 행)
```
- source truth = safety_inspection_results 의 photo_url/photo_urls. GENERAL v1 payload 는
  이를 그대로 보존.
- **문서 레벨 evidence 필드는 v1 에서 만들지 않는다.** evidence_count 는 실측상
  runtime_evidence_field row 수와 일치하는 개념이고(STD-INSPECT-001/STD-FIRE-001 모두
  evidence_count=2 ↔ 실제 evidence_field 2), 일반 runtime_field(input_type=file)와 다르다.
  v1 은 runtime_evidence_field 를 만들지 않으므로 **evidence_count = 0**.
- 문서 전체 첨부가 향후 필요하면 기존 evidence_vault_link 경로 사용. 새 evidence field
  발명 금지(§10 "새 evidence subsystem 금지").

---

## 5. EVIDENCE CONTRACT 판정

```
evidence source 존재(photo_url/photo_urls, 결과 행 내장)   → 확인
binary 미저장(참조만)                                       → 계약 준수
기존 mechanism 재사용(새 subsystem 없음)                    → 준수
result 층 / evidence 층 분리                                 → 준수
v1 evidence_count = 0 (runtime_evidence_field 미생성)         → 정합
→ EVIDENCE CONTRACT = PASS
```

주: 현재 production 데이터에 실제 photo 가 0건이지만, 이는 "아직 사진 첨부 점검이
없었다"는 뜻이지 구조 부재가 아니다. result 행에 photo 컬럼 계약이 존재하므로 evidence
연결은 가능. SCHEMA GAP 아님.
