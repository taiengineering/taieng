# TAI 페이지 유형 분류 (A/B/C)

**확정일**: 2026-04-19
**기준**: 방문자 의도에 따른 상단 레이아웃 결정

---

## 유형 A: 풀 히어로 (13개)

**방문자**: "이게 뭐지?" → 첣인상이 중요

| 파일 | 페이지 |
|------|--------|
| `index.html` | 메인 홈 |
| `service/saas.html` | SaaS 소개 |
| `service/diagnosis.html` | 법령진단 소개 |
| `service/education.html` | 교육사업 소개 |
| `service/appointment.html` | 선임 서비스 |
| `service/repair.html` | 수선 서비스 |
| `service/consulting.html` | 컨설팅 소개 |
| `service/inapp.html` | 인앱 서비스 (자동신고·문서서식) |
| `pricing.html` | 요금제 |
| `target/building.html` | 업종별: 건물·시설 |
| `target/factory.html` | 업종별: 제조공장 |
| `target/construction.html` | 업종별: 건설현장 |
| `for-safety-manager.html` | 역할별: 안전관리자 |
| `for-business-owner.html` | 역할별: 사업주 |

---

## 유형 B: 히어로 없음 (8개)

**방문자**: "빨리 하자" → 스크롤 낭비 금지

| 파일 | 페이지 |
|------|--------|
| `fix-request.html` | 전문가 매칭 채팅 |
| `free-diagnosis.html` | 무료 진단 입력 |
| `free-diagnosis-result.html` | 진단 결과 |
| `log-in.html` | 로그인 |
| `sign-up.html` | 회원가입 |
| `provider-register.html` | 업체 등록 |
| `mypage.html` | 마이페이지 |
| `precedent-search.html` | 판례 검색 |

---

## 유형 C: 미니 헤더 (8개)

**방문자**: "읽어보자" → 제목+한 줄 설명만

| 파일 | 페이지 |
|------|--------|
| `about.html` | 회사소개 |
| `patents.html` | 특허/기술력 |
| `safety-news.html` | 안전정보 뉴스 목록 |
| `safety-news-detail.html` | 안전정보 뉴스 상세 |
| `faq.html` | 자주 묻는 질문 |
| `contact.html` | 문의하기 |
| `privacy.html` | 개인정보처리방침 |
| `terms.html` | 이용약관 |

---

## 미사용/삭제 대상 (템플릿 잔여)

index-1~6, blog-*.html, blog-single-*.html, team.html, team-details.html,
demo.html, service.html, service-details.html, construction.html(루트),
connect.html, showcase.html, tai-fix.html

---

## 판단 기준

```
방문자가 "이게 뭐지?" → 유형 A (풀 히어로)
방문자가 "빨리 하자" → 유형 B (히어로 없음)
방문자가 "읽어보자" → 유형 C (미니 헤더)
```

TAI UI 원칙 "지금 보지 않아도 되는 것은 보여주지 않는다"와 일치.
