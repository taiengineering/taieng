# RFC-011 Domain Pack

## Purpose

Marketing Runtime must remain generic.

Domain-specific operational logic must be injected through Domain Packs.

---

## Principle

```text
Runtime is generic.
Domain knowledge is packaged.
```

---

## Domain Pack Responsibilities

A Domain Pack may provide:

```text
keywords
prompt templates
CTA definitions
risk vocabularies
content templates
industry tone
workflow presets
policy presets
```

---

## Example Packs

```text
tai-pack
hospital-pack
manufacturing-pack
esg-pack
```

---

## TAI Pack Example

```text
무료 법령진단
산업안전 키워드
법령 콘텐츠 프롬프트
중대재해 템플릿
안전관리 CTA
```

---

## Recommended Structure

```text
domain-packs/
 ├─ tai-pack/
 │   ├─ prompts/
 │   ├─ keywords/
 │   ├─ ctas/
 │   ├─ policies/
 │   └─ templates/
```

---

## Runtime Integration

Workspace binds a Domain Pack.

```text
workspace
→ domain_pack_binding
→ runtime configuration
```

---

## Important Principle

```text
Runtime must not directly depend on domain packs.
```

Domain packs are replaceable.

---

## Prohibitions

```text
1. No TAI-specific runtime hardcoding.
2. No domain pack owning platform contracts.
3. No direct provider logic inside packs.
```
