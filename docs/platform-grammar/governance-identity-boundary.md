# Governance ↔ Identity Boundary

## Governance (거버넌스)
- **정의**: 조직/Tenant 운영 영향 관리
- **저장**: `tenant_operational_registry`
- **책임**: "어떤 고객이 영향 받는가"
- **산출**: Tenant Stability (HEALTHY~CRITICAL), Escalation (L1~L4)

**Governance는 조직 영향을 본다. 개인을 보지 않는다.**

## Identity (아이덴티티)
- **정의**: 행위자 역할/권한/가시성
- **저장**: `identity_role_registry`
- **책임**: "누가 무엇을 볼 수 있는가"
- **산출**: Actor Context, Visibility Scope, Audience Resolution

**Identity는 가시성을 결정한다. 데이터를 만들지 않는다.**

## 경계 규칙
- Governance ≠ Identity: Governance는 조직 상태, Identity는 개인 권한
- Governance가 Tenant 위험을 판단 → Identity가 누구에게 보여줄지 결정
- Identity는 IAM이 아니다. 공통 인터페이스일 뿐
