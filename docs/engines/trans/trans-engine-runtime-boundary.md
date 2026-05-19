# Trans Engine Runtime Boundary

## 목적

Trans Engine과 다른 Runtime 간의 경계를 명확히 정의한다.

## 경계 원칙

Trans Engine은 **Projection Layer**이다.  
Truth를 생성하거나 Runtime을 제어하지 않는다.

## 소유권 매트릭스

| 영역 | 소유자 | Trans Engine |
|------|--------|-------------|
| Event 발생 | Runtime Foundation | 읽기만 |
| Severity 결정 | Intelligence Runtime | 참조만 |
| Incident 관리 | Incident Runtime | 참조만 |
| Validation | Validation Runtime | 접근 금지 |
| Sovereignty | Sovereignty Runtime | 접근 금지 |
| Event Bus | Event Bus | 구독만 |
| **상황 해석** | **Trans Engine** | ✅ 소유 |
| **우선순위** | **Trans Engine** | ✅ 소유 |
| **대응 가이드** | **Trans Engine** | ✅ 소유 |
| **학습** | **Trans Engine** | ✅ 소유 |
| **종료 워크플로우** | **Trans Engine** | ✅ 소유 |

## 변경 금지 대상

Trans Engine 개발 시 절대 변경하면 안 되는 파일/구조:

- Runtime Foundation 모든 파일
- Control Runtime
- Validation Runtime
- Sovereignty Runtime
- Event Bus
- Intelligence Runtime
- document_runtime.py
- conditional_rendering_resolver.py
- evidence_binding_engine.py
- field_completeness_engine.py
- runtime_binding_resolver.py
- rendering_integrity.py
- runtime_document_context.py

## DB 원칙

- Trans Engine 전용 테이블만 생성/수정
- 기존 테이블에 nullable 컬럼만 추가 가능
- Breaking migration 금지
- RLS + service_role full access 패턴 유지
