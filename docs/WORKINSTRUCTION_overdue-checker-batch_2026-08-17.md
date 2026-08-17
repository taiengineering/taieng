# 작업지시서 — overdue_checker.py 배치 수정 (LEDGER 22·21독촉·16)

> 2026-08-17 · 캠페인 레인 A(서버) · 대상 `tai-api` · `routers/overdue_checker.py`
> 처리 주체: **Cursor / Claude Code** (파일 23KB + 기존 mojibake + \u 이스케이프 → MCP 전면 재작성 위험, 로컬 편집)
> 한 파일에 걸린 세 건을 함께 처리(파편화 아님).

---

## ① [높음] 22 — 대시보드 미이행 카운터가 항상 0 (응답봉투)

**원인** `GET /overdue/summary` 는 숫자를 `summary` 아래에 준다.
```python
return {
    "status": "success",
    "date":   today.isoformat(),
    "factory_id": factory_id or "all",
    "summary": summary,
}
```
화면(`useSafetyDashboard`)은 `const sumData = sumRes?.data || sumRes || {}` 로 **`data`** 를 먼저 본다.
`data` 가 없어 `sumRes` 자체를 쓰고 거기엔 `warn_d1` 이 없다 → 전부 `|| 0`.

**수정** 반환에 `data` 를 추가한다(기존 `summary` 도 유지 — 하위호환).
```python
return {
    "status": "success",
    "date":   today.isoformat(),
    "factory_id": factory_id or "all",
    "data":    summary,   # ← 추가: 화면이 sumRes.data 로 읽는다 (LEDGER 22)
    "summary": summary,   # 하위호환 유지
}
```
`summary` 키를 쓰는 서버 코드는 이 라우터뿐이므로 안전하다.

**검증** 대시보드 미이행 카드(경고 D+1·에스컬레이션 D+2·OVERDUE D+7)가 실제 건수를 표시.

## ② [높음] 21(독촉) — `POST /overdue/urge/{assignment_id}` 부재

**원인** 대시보드 [독촉]은 `POST /overdue/urge/{id}` 를 부르는데 이 라우터엔 `check·summary·history·resolve/{id}` 뿐 → 404 를 전송부(①)가 성공으로 표시.

**수정** 즉시 독촉 라우트 신설. 해당 work_assignment 의 담당자에게 리마인더 발송(cron 에스컬레이션과 별개의 수동 독촉).
```python
@router.post("/urge/{assignment_id}")
def urge_overdue(assignment_id: str):
    """대시보드 [독촉] — 담당자에게 즉시 리마인더(SMS/인앱). 에스컬레이션 level 은 변경하지 않는다."""
    supabase = get_supabase()
    wa = supabase.table("work_assignments").select(
        "id, assigned_user_id, factory_id, task_name, inspection_set_id, scheduled_date, due_date"
    ).eq("id", assignment_id).limit(1).execute()
    if not wa.data:
        raise HTTPException(status_code=404, detail="배정을 찾을 수 없습니다.")
    row = wa.data[0]
    user_id = row.get("assigned_user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="담당자가 배정되지 않았습니다.")
    task = row.get("task_name") or "점검 작업"
    msg = f"[TAI Safe] {task} 완료를 독촉합니다. 확인 후 처리해 주세요."
    ur = supabase.table("users").select(
        "id, phone, allow_sms, company_id"
    ).eq("id", user_id).limit(1).execute()
    u = ur.data[0] if ur.data else {}
    sms_ok = False
    if u.get("allow_sms") and u.get("phone"):
        sms_ok = _send_sms(u["phone"], msg, user_id=user_id,
                           company_id=u.get("company_id"), trace_id=f"urge-{assignment_id}",
                           source_entity_id=assignment_id)
    _write_notification(supabase, user_id, u.get("company_id"),
                        "[TAI Safe] 독촉", msg,
                        trace_id=f"urge-{assignment_id}", source_entity_id=assignment_id)
    _write_history(supabase, assignment_id, row.get("factory_id"), user_id,
                   row.get("overdue_level") or 0, "URGE", msg, sms_ok, False, True)
    return {"status": "success", "assignment_id": assignment_id, "sms": sms_ok, "notif": True}
```
(고정경로이므로 `/resolve/{history_id}` 등과 같은 위치에 둔다. `_send_sms`·`_write_notification`·`_write_history` 재사용.)

**검증** 대시보드 [독촉] → 담당자 인앱/문자 수신 + `overdue_history` 에 `action_type='URGE'` 1행.

## ③ [낮음] 16 — 파일 내 깨진 글자(mojibake) 정리 (선택)

주석·로그·문자열에 인코딩 깨짐이 있다(예: "추제"→"추적", "판리자"→"관리자", "긜별"→"구분", "상와"→"상황", "에스켈레이션"→"에스컬레이션", "해주기"→"하기", "증"→"즉"). **사용자 노출 문자열 우선**으로 바로잡는다. 로직 무변경.

## 범위 (폭주 금지)
`get_overdue_summary` 반환 한 줄 추가 + `urge` 라우트 신설 + (선택) 문자열 정리. 에스컬레이션 로직·발송 경로 불변.

## 배포
`main` push → Railway(tai-api-prod) 자동 배포. 로그: project `7c3ab53b…` / service `tai-api-prod 4cf52678…` / env `production 9dacb6f0…`.
