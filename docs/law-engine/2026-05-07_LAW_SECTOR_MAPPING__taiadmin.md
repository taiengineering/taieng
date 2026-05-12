# LAW SECTOR MAPPING 2026-05-07

> 366 법령 → sectors[] 다중 매핑 완료. master_rule_v2 설계의 base.

## 작업 종합

### 표준 sector 4개 (사용자 확정)

| 코드 | 한글명 | 의미 | 활성 |
|---|---|---|---|
| `BUILDING` | 건물 | 건축법, 화재안전법, 시설안전 | ✓ |
| `INDUSTRIAL` | 공장 | 제조업, 화학물질, 위험물 | ✓ |
| `CONSTRUCTION` | 건설 | 건설안전법, KCSC | ✓ |
| `SPECIAL_FACILITY` | 특수시설 | 의료/학교/철도 등 | 비활성 (고도화 예정) |

→ "공용"은 별도 카테고리 아님. **sectors[] 배열에 다중 값** = 여러 sector 동시 적용 = 공용 의미.

### 표준화 작업 결과

| # | 대상 | 변경 |
|---|---|---|
| 1 | `system_codes.sector` | INDUSTRY → INDUSTRIAL, SPECIAL → SPECIAL_FACILITY (4개 표준) |
| 2 | `factories.sector` | INDUSTRY → INDUSTRIAL (15 rows), CHECK 제약 추가 |
| 3 | `law_sector_mapping` | **신규 테이블 생성** + 366 법령 INSERT |

---

## law_sector_mapping 테이블 스키마

```sql
CREATE TABLE law_sector_mapping (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  law_id UUID NOT NULL REFERENCES law_master(id) ON DELETE CASCADE,
  law_name TEXT NOT NULL,
  sectors TEXT[],  -- NULL 허용 (비활성), 다중 값 = "공용"
  confidence TEXT NOT NULL CHECK (confidence IN ('HIGH','MEDIUM','LOW','INACTIVE')),
  mapping_method TEXT NOT NULL  -- 'auto_regex' | 'manual_verified' | 'web_search_verified'
    DEFAULT 'auto_regex',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (law_id),
  CHECK (sectors IS NULL OR sectors <@ ARRAY['BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY']),
  CHECK (sectors IS NULL OR array_length(sectors, 1) >= 1)
);

CREATE INDEX idx_law_sector_mapping_sectors ON law_sector_mapping USING GIN(sectors);
CREATE INDEX idx_law_sector_mapping_confidence ON law_sector_mapping(confidence);
```

---

## 매핑 통계 (366 법령, 58,495 clauses)

### 신뢰도별 분포

| 신뢰도 | 법령 수 | 의미절 수 | 비율 |
|---|---|---|---|
| HIGH (자동 정규식) | 331 (90.4%) | 55,739 | 95.3% |
| MEDIUM (외부 검색 검증) | 28 (7.7%) | 2,733 | 4.7% |
| INACTIVE (비활성, sectors=NULL) | 7 (1.9%) | 23 | 0.04% |
| **합계** | **366** | **58,495** | **100%** |

### sector별 적용 분포 (다중 매핑 unnest 후)

| sector | 적용 법령 | 적용 의미절 |
|---|---|---|
| BUILDING (건물) | 175 | 30,314 |
| INDUSTRIAL (공장) | 158 | 29,955 |
| CONSTRUCTION (건설) | 130 | 28,302 |
| SPECIAL_FACILITY (비활성) | 113 | 13,504 |

### 매핑 다중성 분포

| 매핑 패턴 | 법령 수 |
|---|---|
| 단일 sector | 162 (HIGH) + 28 (MEDIUM) = 190 |
| 다중 sector ("공용") | 169 (HIGH) |
| NULL (비활성) | 7 (INACTIVE) |

---

## 자동 매핑 룰 (정규식, AI 0%)

```python
LAW_SECTOR_MAPPING_RULES = [
    # === BUILDING 단독 (건축물 관련) ===
    (r'^건축법|^건축물관리법|^건축사법|^건축기본법|^건축서비스산업|^건축물의 (피난|구조|설비|분양)|'
     r'^건축물대장|^한옥 등 건축자산|^녹색건축|^지능형건축물|^제로에너지건축물|^재건축초과이익|'
     r'^공사중단 장기방치 건축물|^초고층 및 지하연계 복합건축물|^법원청사건축|^법원 청사 건축|^건축물착공',
     ['BUILDING'], 'HIGH'),
    (r'^다중이용업소', ['BUILDING'], 'MEDIUM'),  # 검증: 건물 내 영업
    
    # === CONSTRUCTION 단독 ===
    (r'^건설기계|^건설기술|^건설산업|^건설폐기물', ['CONSTRUCTION'], 'HIGH'),
    
    # === INDUSTRIAL 단독 ===
    (r'^산업집적활성화 및 공장설립|^공장 (및|광업)|^화학물질|^위험물안전|^화학무기',
     ['INDUSTRIAL'], 'HIGH'),
    (r'^제품안전', ['INDUSTRIAL'], 'MEDIUM'),  # 검증: 제조업+수입업
    
    # === 다중 (BUILDING + INDUSTRIAL + CONSTRUCTION) ===
    (r'^산업안전보건|^한국산업안전보건공단', ['BUILDING','INDUSTRIAL','CONSTRUCTION'], 'HIGH'),
    (r'^재난 및 안전관리|^재난관리자원|^재난안전(통신망|산업)|^지진|^산업재해보상보험|'
     r'^고용보험|^근로기준|^파견근로자|^중대재해|^화재의 예방|^소방시설 설치|^소방기본|'
     r'^시설물의 안전 및 유지관리|^폐기물관리법',
     ['BUILDING','INDUSTRIAL','CONSTRUCTION'], 'HIGH'),
    
    # === BUILDING + CONSTRUCTION (주택/도시계획) ===
    (r'^주택법|^공동주택관리법|^공동주택|^국토의 계획|^도시ㆍ군|^노후계획도시|^주차장법|'
     r'^정보통신공사업|^소방시설공사업',
     ['BUILDING','CONSTRUCTION'], 'HIGH'),
    (r'^전기공사(업|공제조합)법|^전기사업회계', ['BUILDING','CONSTRUCTION'], 'HIGH'),
    
    # === BUILDING + INDUSTRIAL (전기/가스/수도/승강기 — 건물도 공장도 사용) ===
    (r'^전기사업법|^전기안전|^전기용품|^에너지이용|^집단에너지|^기계설비법|^실내공기질|'
     r'^석면안전|^석면피해|^승강기 안전|^승강기산업|^도시가스|^액화석유가스|^고압가스|'
     r'^수도법|^하수도법|^수도용|^어린이놀이시설',
     ['BUILDING','INDUSTRIAL'], 'HIGH'),
    
    # === INDUSTRIAL + CONSTRUCTION (환경) ===
    (r'^대기환경|^물환경|^토양환경|^소음ㆍ진동|^악취방지|^잔류성오염|^해양폐기물|'
     r'^폐기물의 국가 간|^환경기술|^한국환경|^신에너지|^기후위기|^대기관리권역|^폐기물처리시설',
     ['INDUSTRIAL','CONSTRUCTION'], 'HIGH'),
    
    # === SPECIAL_FACILITY (비활성) ===
    (r'^의료|^응급의료|^공공보건의료|^농어촌 등 보건|^군보건|^체외진단의료기기|^혁신의료기기',
     ['SPECIAL_FACILITY'], 'HIGH'),
    (r'^장애인|^발달장애|^노인|^사회복지|^어린이ㆍ노인|^국립장애인|^중증장애|^재난적의료비',
     ['SPECIAL_FACILITY'], 'HIGH'),
    (r'^학교안전|^식품안전|^전기통신사업|^방송통신', ['SPECIAL_FACILITY'], 'HIGH'),
    
    # === MEDIUM (외부 검색 검증, SPECIAL_FACILITY) ===
    (r'방사성폐기물|원자력안전|^고준위 방사성폐기물|^중ㆍ저준위', ['SPECIAL_FACILITY'], 'MEDIUM'),
    (r'^산림재난|^해사안전|^공항소음|^군용비행장', ['SPECIAL_FACILITY'], 'MEDIUM'),
    
    # === INACTIVE (sectors=NULL, 비활성) ===
    # 자연재난/사회재난 구호: 국가 보상금 기준
    # 농어촌 전기공급: 한전 사업
    # 정부 조직 규칙
    (r'^자연재난 구호|^사회재난 구호|^농어촌 전기공급|^보건복지부 소관 비상대비|^기후에너지환경부장관',
     None, 'INACTIVE'),
]
```

---

## 외부 검색 검증 사례 (MEDIUM 확정)

### 다중이용업소의 안전관리에 관한 특별법 → BUILDING만

검색 결과: 식품접객업/노래연습장/PC방/고시원/산후조리원 등 모두 **건물 내 영업**.
→ INDUSTRIAL 무관. BUILDING만 적절.
출처: 다중이용업소법 시행령 제2조, 소방청

### 제품안전기본법 → INDUSTRIAL

검색 결과: 사업자 = 제품을 **제조 또는 수입·판매·대여**하는 자.
→ 사업장 안전이 아닌 **제품 자체** 리콜법. INDUSTRIAL 적절.
출처: 국가기술표준원

### 산림재난방지법 → SPECIAL_FACILITY (비활성)

검색 결과: **산림 소유자/산림청** 대상. 일반 사업장 무관.
출처: 산림청, 산림재난방지법 시행령

### 자연재난/사회재난 구호 비용 → 비활성 (NULL)

검색 결과: **국가/지자체의 보상금 지급 기준법**. 사업장에 부여되는 의무 아님.
출처: 자연재난 구호 및 복구 비용 부담기준 등에 관한 규정 제4조

### 농어촌 전기공급사업 촉진법 → 비활성 (NULL)

검색 결과: **한국전력공사**의 농어촌 전기공급 사업법. 일반 사업장 무관.
출처: 농어촌 전기공급사업 촉진법 제2조 (전기사업자 = 한국전력공사)

---

## 다음 단계 (master_rule_v2 설계)

### A. 코드 영향 검색 (전역변수 sector 사용처)

사용자 명시: "전역변수를 사용하고 있는 곳들이 있으므로 해당 프로그램이나 API 등을 수정해야 하는 작업 동반"

검색 대상:
- `tai-api`(Python): `sector ==`, `'INDUSTRY'`, `'MANUFACTURING'`, `'BUILDING'`, `'CONSTRUCTION'`, `'COMMON'`, `'SPECIAL'` 패턴
- `tai-admin`(HTML/JS): 같은 패턴
- 결과 → `SECTOR_CODE_IMPACT_2026-05-07.md`

### B. master_rule_v2 스키마 설계

스키마 doc 작성 후 사용자 검토 → migration:
- `master_rule` (마스터 룰, 6하원칙 + 범위 + sectors[])
- `master_rule_application` (사업장별 적용 결과)
- `inspection_item_v2` (점검항목, 4가지 세팅 boolean)
- `master_rule_extraction_log` (변환 추적)

### C. 의미절 → master_rule 자동 변환 알고리즘

정규식/키워드 사전 기반 (AI 0%). 의미절 5요소 + sectors[] → 6하원칙 + 범위로 변환.

---

## 검증 SQL (참고)

```sql
-- BUILDING 사업장에 적용되는 룰
SELECT * FROM law_sector_mapping WHERE 'BUILDING' = ANY(sectors);

-- 다중 적용("공용") 룰
SELECT * FROM law_sector_mapping WHERE array_length(sectors, 1) >= 2;

-- 비활성 룰
SELECT * FROM law_sector_mapping WHERE sectors IS NULL;

-- sector별 적용 의미절 수 (unnest)
SELECT unnest(sectors) AS sector, COUNT(DISTINCT sci.id) AS clauses
FROM law_sector_mapping lsm
JOIN law_article la ON la.law_id = lsm.law_id
JOIN semantic_clause sci ON sci.source_article_id = la.id
WHERE sectors IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC;
```

---

## 관련 핸드오프

- `docs/extraction/HANDOFF_2026-05-05.md` — 의미절 v1.0~v1.4
- `docs/extraction/HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용 + sector 표준화 분석
- `docs/extraction/LAW_SECTOR_MAPPING_2026-05-07.md` — **본 문서** (366 법령 sector 매핑 완료)
