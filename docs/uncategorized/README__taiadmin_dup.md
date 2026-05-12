# React 예시 (복사용)

이 폴더는 **Vite + React 18 + TypeScript** 프로젝트에 그대로 옮겨 담을 수 있는 예시입니다.

## 설치 (새 프로젝트 시)

```bash
npm create vite@latest partner-web -- --template react-ts
cd partner-web
npm install react-router-dom
# 선택: npm install react-hook-form zod @hookform/resolvers
```

## 라우팅

`App.tsx`에서 `PartnerRoutes.example.tsx`의 라우트를 합치면 됩니다.

## 스타일

Tailwind를 쓰지 않는 경우, 프로젝트의 디자인 토큰(Bootstrap / SCSS)에 맞춰 `className`만 교체하면 됩니다. 예시는 **의미 중심 클래스명 + 주석**으로 작성했습니다.
