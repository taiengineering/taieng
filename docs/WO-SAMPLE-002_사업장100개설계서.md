# WO-SAMPLE-002
# 검증용 사업장 100개 설계서 (VCF-01)

**작성일:** 2026-06-23  
**상태:** 설계 완료 / DB INSERT 금지 / 승인 후 적재  

---

## 핵심 요약

### 사업장 구성 (100개)
- MFG (제조업): 40개 | VCF-01-MFG-001~040
- CON (건설업): 30개 | VCF-01-CON-001~030
- BLD (건물관리): 15개 | VCF-01-BLD-001~015
- LOG (물류/창고): 15개 | VCF-01-LOG-001~015

### KSIC 체계
- C10 식품: MFG-031~033,037~038
- C20 화학: MFG-001~010
- C24 쳊강: MFG-011~016
- C25 금속가공: MFG-017~020
- C26 전자: MFG-021~028
- C29 기계: MFG-024~030
- D35 에너지: MFG-034~036,039~040
- F41 주거건설: CON-001~010,021~029 일부
- F42 토목건설: CON-011~020,023~027
- H49 운수업: LOG-008~010
- H52 창고: LOG-001~007,011~015
- Q86 병원: BLD-011~012
- null (KSIC 없음): BLD-001~010,013~015 및 일부 CON

### 인원 분포 (경계값 망라)
```
5인   MFG-021, CON-001, CON-021, BLD-001
10인  MFG-011, CON-016, LOG-001
19인  MFG-001
20인  MFG-017, CON-009, BLD-003
30인  MFG-012, CON-003, CON-011, BLD-004
49인  MFG-006, MFG-018, CON-004, BLD-005  ← 50인 미달 경계값
50인  MFG-002, MFG-013, CON-005, BLD-006   ← 안전관리자 임계
99인  MFG-014                              ← 100인 미달 경계값
100인 MFG-003, MFG-015, CON-006, BLD-007   ← 관리규정 임계
300인 MFG-004, CON-007, LOG-006
500인 MFG-005, CON-008
1000인 MFG-005, CON-020, BLD-010
```

### Coverage Matrix (요약)

| 조건 유형 | 실혀 등장 횟수 | 목표(5회) | 달성 |
|---|---|---|---|
| THRESHOLD (인원수) | 모든 규모 등장 | 5회+ | ✓ |
| INDUSTRY (KSIC) | 12개 코드 이상 | 5회+ | ✓ |
| WORK (has_*) | 9개 필드 전체 | 3회+ | ✓ |
| EQUIPMENT (설비코드) | 타워/이동식/애저타입 실게 구분 | 5회+ | ✓ |
| COMPOUND (복합) | KSIC×THRESHOLD×WORK 교차 | 10회+ | ✓ |
| PROCESS (공정) | 정 + has_*=false 케이스 | 5회 | ✓ |

### 필수 비교쌍 (condition_mapping 햵심 검증)

| 비교 | A 사업장 | B 사업장 | 검증 목표 |
|---|---|---|---|
| 안전관리자 임계 | MFG-006 (49인) | MFG-002 (50인) | 의무 차이수 |
| 담당자 임계 | MFG-001 (19인) | MFG-017 (20인) | 의무 차이수 |
| 관리규정 임계 | MFG-014 (99인) | MFG-015 (100인) | 의무 차이수 |
| TC 유무 | CON-001 (tc=F) | CON-002 (tc=T) | 타워크레인 의무만 |
| 발파 유무 | CON-016 (blast=F) | CON-011 (blast=T) | 발파 의무만 |
| KSIC 유무 | BLD-006 (null) | MFG-008 (C20) | KSIC 효과 |

### 파이프라인 (승인 후)
```
1. 승인 후 DB INSERT (factories 100개)
2. factory_process 적재
3. equipment_assets 적재
4. facility_applicability 실행
5. 의무 발생 건수 집계
6. condition_mapping 설계 시작
```

### 누락 조건 (추후 VCF-02에서 보강)
- has_diving 단독 케이스 3회 미만
- KSIC H49 3회 미만
- KSIC Q86 2회 미만
- 공사금액/수주금액 조건
- 하수급인 관련 조건

### 판정: condition_mapping 시작 가능 (YES)
이 100개로 THRESHOLD / INDUSTRY / WORK / EQUIPMENT / COMPOUND 코어 조건 충분 커버.
has_diving/H49/Q86 부족분은 VCF-02 병행하면서 보강.
