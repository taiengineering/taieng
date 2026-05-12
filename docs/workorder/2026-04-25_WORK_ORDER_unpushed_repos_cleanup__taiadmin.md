# WORK ORDER 2026-04-25 · tai-api / taieng 미푸시분 정리

- **대상**: Cursor (전 영역창)
- **목적**: 로컬에만 있는 작업물의 GitHub 백업 + 안전한 푸시
- **선행 보고**: Cursor가 "tai-api에 law rule generator, CI 등 / taieng에 nexas 등 미푸시분 있음" 자체 보고

---

## 사전 원칙

### 절대 하지 말 것

1. **`git push --force` 금지** — 히스토리 망가뜨림
2. **확인 없이 main에 일괄 push 금지** — tai-api는 main push → Railway 자동 배포라 운영 영향
3. **여러 무관한 변경을 한 커밋으로 묶지 말 것** — 작업 단위로 분리

### 반드시 할 것

1. **변경사항 보고 먼저, 푸시는 나중**
2. **tai-api는 무조건 dev 브랜치 우선** (memory 기록된 규칙)
3. **각 변경의 출처 명시** — 어떤 작업의 결과물인지 모르면 푸시 보류

---

## TASK 1. 현재 상태 보고 (먼저 실행)

### 1-1. tai-api 레포 점검

```bash
cd ~/path/to/tai-api   # 실제 로컬 경로

# 현재 브랜치 + 작업트리 상태
git status

# 미푸시 커밋 (dev 기준)
git log origin/dev..HEAD --oneline

# 미푸시 커밋 (main 기준)
git log origin/main..HEAD --oneline

# 미커밋 변경 통계
git diff --stat HEAD
git diff --stat --cached HEAD

# 추적 안 된 파일 목록
git ls-files --others --exclude-standard
```

### 1-2. taieng 레포 점검

```bash
cd ~/path/to/taieng   # 실제 로컬 경로

git status
git log origin/main..HEAD --oneline
git diff --stat HEAD
git ls-files --others --exclude-standard
```

### 1-3. 보고 형식

각 레포에 대해 다음 표 작성하여 보고:

```
## tai-api

현재 브랜치: ___
원격 추적: origin/___

### 미푸시 커밋
| SHA | 제목 | 작성일 |
|-----|------|--------|
| ... | ...  | ...    |

### 미커밋 변경 (working tree)
| 파일 | 상태 (M/A/D) | 추정 작업 출처 |
|------|------|------|
| ... | M | law rule generator |
| ... | A | CI 설정 |

### 추적 안 된 파일
| 파일 | 추정 출처 | 의도 |
|------|----------|------|
| ... | 임시 파일 / 백업 / 새 작업 | 푸시 / 삭제 / 보류 |
```

---

## TASK 2. 분류 및 결정 (보고 후 심태왕 검토)

각 변경을 다음 4분류로 나눔:

### 분류 A: 의도된 완성 작업 → 정상 푸시
- 명확한 기능 추가/버그 수정
- 테스트 완료
- → tai-api는 **dev 브랜치**, taieng는 **main**

### 분류 B: 진행 중 작업 → 임시 브랜치 보존
- 미완성이지만 작업 중인 코드
- 컴퓨터 분실 대비 백업 필요
- → `wip/<주제>` 브랜치로 push (예: `wip/law-rule-generator-2026-04`)

### 분류 C: 실험/탐색 코드 → stash 또는 삭제
- 실험 후 결론 난 것
- 의미 없는 디버그 출력
- → `git stash push -m "..."` 또는 직접 삭제

### 분류 D: 출처 불명 → 푸시 보류
- 무엇인지 모름
- 어떤 작업의 결과물인지 확인 불가
- → 보류, 심태왕에게 다음 작업 시 확인 요청

⚠️ **불명확한 변경을 절대 main에 푸시하지 말 것.** 심태왕이 직접 확인 후 결정.

---

## TASK 3. 단계별 푸시 (분류 결정 후)

### 3-1. tai-api dev 브랜치 푸시

```bash
cd ~/path/to/tai-api

# 현재 dev 추적 중인지 확인
git branch -vv | grep "^\*"

# dev가 아니면 전환
git checkout dev || git checkout -b dev origin/dev

# 원격 최신화
git fetch origin

# 로컬 dev가 origin/dev보다 뒤져있으면 rebase
git rebase origin/dev

# 푸시
git push origin dev
```

### 3-2. taieng main 푸시

```bash
cd ~/path/to/taieng

git fetch origin
git rebase origin/main
git push origin main
```

⚠️ 만약 rebase 충돌 발생 시 **즉시 작업 중단하고 보고**. 충돌 해결을 임의로 시도하지 말 것.

---

## TASK 4. 푸시 후 검증

### tai-api 검증

1. **dev 브랜치**에 푸시한 경우:
   - GitHub에서 dev 브랜치 commits 페이지 확인
   - PR 생성 (dev → main)은 별도 작업으로 분리
   - dev → main merge는 심태왕 확인 후
   
2. **Railway 배포 확인**:
   - main에 머지된 게 아니면 Railway는 영향 없음
   - main 머지 후에는 https://api.taieng.co.kr/health 200 확인

### taieng 검증

1. https://github.com/taiengineering/taieng/commits/main 에서 푸시 커밋 확인
2. Cloudflare Pages 자동 배포 → https://new.taieng.co.kr 5분 후 확인

---

## TASK 5. 정리 보고

푸시 완료 후 다음 형식으로 최종 보고:

```
## tai-api 정리 결과

푸시한 브랜치: dev
푸시한 커밋: <SHA1>, <SHA2>, ...
주요 변경:
- law rule generator: 어떤 변경인지
- CI: 어떤 변경인지

분류 B (wip 브랜치)로 보존: <브랜치명>
분류 C (stash)로 보류: <stash 메시지>
분류 D (확인 필요): <파일 목록>

## taieng 정리 결과
...
```

---

## 체크리스트

### Phase 1: 보고
- [ ] tai-api `git status`, `git log` 결과 확인
- [ ] taieng `git status`, `git log` 결과 확인
- [ ] 각 변경을 A/B/C/D로 분류한 표 작성
- [ ] 심태왕에게 분류 결과 공유 + 푸시 승인 요청

### Phase 2: 푸시 (승인 후)
- [ ] 분류 A: tai-api dev 브랜치 푸시
- [ ] 분류 A: taieng main 푸시
- [ ] 분류 B: wip 브랜치 생성 + 푸시
- [ ] 분류 C: stash 또는 삭제
- [ ] 분류 D: 보류, 다음 작업 시 확인

### Phase 3: 검증
- [ ] GitHub commits 페이지 확인
- [ ] tai-api `/health` 200 (main 머지 시)
- [ ] taieng Cloudflare Pages 정상 배포
- [ ] 최종 정리 보고서 제출

---

## 위험 대응

| 위험 | 대응 |
|---|---|
| rebase 충돌 발생 | 즉시 중단, `git rebase --abort` 후 보고 |
| main에 잘못 푸시 | revert 커밋으로 되돌리기 (force push 금지) |
| Railway 배포 후 /health 503 | tai-api dev로 즉시 revert PR 생성 |
| 분류 D 항목을 누가 만든지 모름 | 절대 삭제하지 말고 보류 |

---

**작성**: Claude (기획창)  
**실행**: Cursor (전 영역창)  
**검증**: 심태왕 (분류 결정 + 푸시 승인)
