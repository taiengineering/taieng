# 원천 무결성 진단 — master/version/article 정순·역순 (S13)

**작성일**: 2026-05-04
**대상**: `law_master` (752) / `law_version` (752) / `law_article` (32,808)
**검증 방향**: 정순 (master→version→article) + 역순 (article→version→master) + 횡적
**결론**: **원천 무결성 대부분 양호하지만 article 중복 5,430건 + master 9개 중복 발견**

---

## 1. 트랙 A — 정순 무결성 (FK / 일관성) ✅ 매우 양호

| 항목 | 결과 |
|---|---|
| master 총수 / active=true | 752 / 752 |
| master active=false / NULL | 0 / 0 |
| **master.current_version_id NULL** | **0** ✅ |
| **master.current_version_id orphan FK** | **0** ✅ |
| version 총수 | 752 (master와 1:1) |
| **version.law_id orphan** | **0** ✅ |
| version 1개당 master 매핑 안 됨 | 0 ✅ |
| **article.law_version_id NULL / orphan** | **0 / 0** ✅ |
| **article.law_id NULL / orphan** | **0 / 0** ✅ |
| **article.law_id ≠ version.law_id (역추적 불일치)** | **0** ✅ **완벽** |
| article.article_no NULL | 0 ✅ |
| article.article_text NULL | 0 ✅ |
| 삭제된 article (is_deleted_in_version=true) | 0 ✅ |

→ **정순 FK + 역추적 일관성 100%**. 마이그레이션이 잘 됐음.

---

## 2. 트랙 B — 역순 + 횡적 무결성 ⚠️ 다수 발견

### 2.1 ★ article 진짜 중복 — 5,430 row (16.6%) ⚠️⚠️⚠️

같은 (`law_version_id`, `article_no`, `article_sub_no`, `article_type`) 조합이 여러 row.

| 차원 | 결과 |
|---|---:|
| 중복 그룹수 | 674 |
| 영향 row | **5,430** (전체 article의 16.6%) |
| article_type 분포 | 조문 20,711 / 본칙 5,444 / 항 2,325 / 전문 1,766 / 조 1,223 / 절 649 / 목 452 / 장 238 |

#### 가장 심각한 패턴 — NFTC 화재안전기술기준 (제2조 항 100개+ 중복)

| 법령 | 중복 패턴 |
|---|---|
| 스프링클러 NFTC 103 | 제2조 '항' **175개** 중복 |
| 포소화 NFTC 105 | 제2조 '항' **131개** 중복 |
| 화재조기진압 NFTC 103B | 제2조 '항' **126개** 중복 |
| 간이스프링클러 NFTC 103A | 제2조 '항' **99개** 중복 |
| 옥내소화전 NFTC 102 | 제2조 '항' **92개** 중복 |

→ NFTC 제2조는 "용어 정의/설치기준"으로 수많은 항(2.1, 2.2, 2.3...)이 있는데, **모두 article_no=2, article_type='항'으로 같게 매겨져 있음**. `article_no_sort`나 `article_internal_key`로는 구분되지만 (article_no, sub_no, type) 키만으로는 서로 안 보임. 적재 시 계층 구조 표현 실패.

#### 법령별 중복 그룹 TOP

| 법령 | 중복 그룹수 |
|---|---:|
| 방사선 안전관리 등의 기술기준에 관한 규칙 | 23 |
| 방호장치 안전인증 고시 | 23 |
| 작업환경측정 및 정도관리 등에 관한 고시 | 18 |
| 전기설비기술기준 | 17 |
| 유해화학물질 제조·사용·저장시설 설치 및 관리에 관한 고시 | 13 |

→ 이쪽은 NFTC와 다른 패턴. 같은 조항이 진짜로 두 번 적재됐을 가능성 — row 단위 비교로 검증 필요.

### 2.2 ★ law_name 중복 active master 9개 ⚠️

| 법령명 | 중복 master 수 |
|---|---:|
| **"안전기준 등록"** | **9개 master** |

→ 동일 이름의 master가 9개. 4월 22일 dup_backup에서 정리했어야 할 것이 살아남았거나, 사후 추가됐음. master_id가 다 다르므로 9개 중 하나만 진짜고 나머지 8개는 폐기 후보.

### 2.3 master 데이터 입력 오류

| 항목 | 건수 | 의미 |
|---|---:|---|
| announcement_date > enforcement_date | 1 | **해사안전기본법 시행규칙** (announce=2024-02-05 / enforce=2024-01-26) |
| enforcement_date 미래 | 8 | 시행 예정 법령 (정상이지만 추출 정책 결정 필요) |

#### 시행 예정 법령 8건 (룰 추출 정책 결정 필요)

| 법령 | enforce 일자 |
|---|---|
| 화학물질의 등록 및 평가 등에 관한 법률 | 2026-05-12 (8일 후) |
| 기계설비법 시행규칙 | 2026-06-01 |
| 공동주택관리법 | 2026-06-03 |
| 노후계획도시 정비 및 지원에 관한 특별법 | 2026-08-04 |
| 주택법 | 2026-08-04 |
| 물환경보전법 | 2027-02-20 |
| 건설기계관리법 | 2027-02-28 |
| 어린이놀이시설 안전관리법 | 2027-02-28 |

→ 시행 전 추출할지, 시행일에 맞춰 추출할지 정책 결정 필요.

### 2.4 본문 부족 master

| 항목 | 건수 | 처리 방향 |
|---|---:|---|
| article 0개 master | 2 | 누락 적재 또는 master 폐기 |
| **article 1개만(메타만) 있는 master** | **100** | KEC와 같은 패턴 — 외부 PDF 수집 필요 |
| article 100개 이상 master | 88 | 정상 (대법령) |
| master당 평균 article | 43.6 | — |
| master당 article 최대 | 822 | — |

#### 메타만 있는 master 100개 정체

검색 샘플:
- 전기용품 안전기준(KC 60598-2-20, KC 60335-2-23, KC 10023, ...) — **KC 인증 표준**
- 소음·진동공정시험기준 / 빛공해공정시험기준 / 악취공정시험기준 — **환경 시험기준**

→ 본문이 IEC/ISO 등 국제 표준 또는 별표/시방서 형태라 article로 적재 안 됨. **KEC와 같은 카테고리 — 외부 수집 트랙**.

---

## 3. 트랙 C — 백업 테이블 (정리 검토)

| 테이블 | row 수 | 시점 |
|---|---:|---|
| `law_master_old_20260423` | 473 | 4/23 마이그레이션 백업 |
| `law_article_old_20260423` | 30,827 | 4/23 article 백업 |
| `law_master_dup_backup_20260422` | 96 | 4/22 중복 정리 시 |
| `law_version_dup_backup_20260422` | 96 | 4/22 동일 |
| `law_master_archive_20260422` | ? | 4/22 archive |
| `law_master_preswitch_20260423` | ? | 4/23 switch 직전 |

→ 합계 약 **31,500 row의 백업 데이터**. 운영 영향 없음. 30일~90일 보관 후 정리 정책 결정 필요.

---

## 4. ★ 결정적 인사이트 — drafts 중복은 article 중복의 결과

직전 진단(`AUDIT_law_rule_drafts_20260504.md`)에서 발견한 **drafts 완전중복 18 그룹 / 40 건** 중 다수는 NFTC + 작업환경측정 + 전기설비기술기준 — 정확히 이번에 발견된 **article 진짜 중복 법령들**.

```
원천 article 중복 (5,430)
        ↓
drafts 추출 시 같은 의무 여러 번 적재
        ↓
drafts 완전중복 40건 (이전 진단의 P5)
```

→ **drafts 중복 정리(P5) 전에 원천 article 중복부터 정리해야 함**.
→ 원천 정리 안 하면 T1 (606 법령 추출) 시 같은 패턴으로 계속 중복 생성.

---

## 5. 작업 우선순위 재재정의 (3차)

이전 우선순위는 drafts 중심이었으나, **원천 정리가 모든 추출의 선행 조건**.

| 트랙 | 작업 | 영향 | 의존 |
|---|---|---:|---|
| **T0-A** | NFTC 외 article 중복 정리 (법령별 10~23건) | ~150 row | 없음 |
| **T0-B** | NFTC 제2조 항 중복 (적재 시 article_no_sort/sub_no 정리) | ~5,300 row | 없음 |
| **T0-C** | "안전기준 등록" master 9개 정리 (8개 폐기) | 9 master | 없음 |
| **T0-D** | 해사안전기본법 announcement/enforcement 보정 | 1 row | 없음 |
| **T0-E** | enforce 미래 8건 추출 정책 결정 | 8 master | 결정 |
| **T0-F** | article 0개 master 2개 처리 | 2 master | 적재 또는 폐기 |
| **T0-G** | 메타만 master 100개 외부 수집 트랙 (별도) | 100 master | KEC 4 master 트랙과 동일 |
| **T0-H** | 백업 테이블 보관 정책 결정 | 31,500 row | 30~90일 후 |
| ────────── | ──────────────────────── | ───── | ───── |
| **T1 본미션** | **606 법령 추출** (T0-A,B 완료 후) | 20,629 article | T0-A,B |
| T2 | 산안법 18건 매핑 수정 | 18 | 없음 |
| T3 | drafts.article_id 1,352 자동 매칭 | 1,352 | T0-B (article_no_sort 정리 후) |
| T4 | drafts 무결성 정리 (P1~P6) | 5,418 | T0,T1,T2,T3 |
| T5 | 정규화 + active 적재 | 3,158 | T1,T4 |

### 추천 진행 순서

```
T0-A,B,C,D ──→ T1 ── 동시 ──→ T2, T3 ──→ T4 ──→ T5
                                              ↑
                T0-G (메타 100개) ────────────┘
                T0-E,F (정책 결정)
                T0-H (백업, 30일 후)
```

---

## 6. 결론

### 정순(Forward) 무결성 — 매우 양호 ✅
- master ↔ version ↔ article FK / 역추적 100% 일관
- NULL / orphan 0건
- 삭제 / 비활성 일관성 OK

### 역순(Backward) + 횡적 무결성 — 다수 이슈 ⚠️
- **article 진짜 중복 5,430건 (16.6%)** — NFTC + 일부 법령
- **law_name 중복 active 9 master** ("안전기준 등록")
- announcement > enforcement 1건
- enforce 미래 8건 (정책 결정 대상)
- 메타만 master 100개 (외부 수집 대상)
- article 0개 master 2개

### 가장 큰 인사이트
**drafts 완전중복 40건은 article 중복 5,430건의 결과**. 원천 정리 없이 추출 진행 시 같은 패턴 재생산.

### 다음 단계 (대표님 결정)

1. **T0-A,B,C,D 즉시 정리**할까요? Python 스크립트 1개로 SQL DELETE/UPDATE 가능
2. **NFTC article 중복(T0-B)의 정확한 원인** 더 파헤칠까요? — 적재 스크립트 검토
3. **"안전기준 등록" 9 master**의 진짜와 가짜 어떻게 구분할까요? — 9 master id 직접 확인 후 정책 결정
4. **메타만 master 100개**는 별도 트랙(KEC 4 master 트랙과 합쳐) 진행할까요?
