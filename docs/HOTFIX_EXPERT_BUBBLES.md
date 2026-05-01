# 핫픽스: for-expert.html 버블 위치 수정

> **작업자:** Cursor / Claude Code
> **대상 파일:** `taieng` 레포 → `nexas/for-expert.html`
> **작업 유형:** CSS만 수정 (HTML 변경 없음)

---

## 문제

버블 4개가 오른쪽에 일렬로 쏠려 있어서:
- 인물 얼굴/상체와 겹침
- 버블끼리 간격이 좁아 답답함
- 참고 이미지(company.png 원본)의 대각선 배치와 다름

## 수정 내용

**버블 위치 CSS만 변경.** 대각선 계단형으로 퍼뜨린다.

### 기존 (삭제)

```css
#fe2 .fe2-bubble-1 { right: 30px; top: 10px; animation: fe2Float 3s ease-in-out infinite; }
#fe2 .fe2-bubble-2 { right: 0;    top: 100px; animation: fe2Float 3s ease-in-out infinite 0.6s; }
#fe2 .fe2-bubble-3 { right: 40px; top: 190px; animation: fe2Float 3s ease-in-out infinite 1.2s; }
#fe2 .fe2-bubble-4 { right: 10px; top: 280px; animation: fe2Float 3s ease-in-out infinite 1.8s; }
```

### 변경 (교체)

```css
/* 버블 위치 — 우상단에서 좌하단으로 대각선 계단 */
#fe2 .fe2-bubble-1 { right: -10px; top: 20px;  animation: fe2Float 3s ease-in-out infinite; }
#fe2 .fe2-bubble-2 { right: -40px; top: 120px; animation: fe2Float 3s ease-in-out infinite 0.6s; }
#fe2 .fe2-bubble-3 { right: -10px; top: 220px; animation: fe2Float 3s ease-in-out infinite 1.2s; }
#fe2 .fe2-bubble-4 { right: -50px; top: 310px; animation: fe2Float 3s ease-in-out infinite 1.8s; }
```

### 추가 수정 — 버블 영역이 인물을 가리지 않도록

기존 `.fe2-a-bubbles` 에 `pointer-events: none`과 `width 제한` 추가:

```css
#fe2 .fe2-a-bubbles {
  flex: 0 0 280px;           /* flex:1 → 고정폭 280px로 축소 */
  position: relative;
  min-height: 360px;
  pointer-events: none;      /* 이미지 클릭 방해 방지 */
}

#fe2 .fe2-bubble {
  pointer-events: auto;      /* 버블 자체는 클릭 가능 */
}
```

### 모바일 추가 보강

```css
@media (max-width: 768px) {
  #fe2 .fe2-a-bubbles {
    flex: none;
    width: 100%;
    min-height: auto;
  }

  #fe2 .fe2-bubble {
    position: static !important;
    right: auto !important;
    top: auto !important;
  }
}
```

---

## 검증

- [ ] 데스크톱: 버블 4개가 우상단→좌하단 대각선으로 배치
- [ ] 데스크톱: 인물 얼굴과 버블이 겹치지 않음
- [ ] 데스크톱: 버블이 화면 밖으로 잘리지 않음 (overflow: hidden이므로 right 음수값 주의)
- [ ] 모바일: 버블이 수직 스택으로 정상 표시
- [ ] 부유 애니메이션 정상 동작
