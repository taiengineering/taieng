"""
admrule-kr frontmatter → CSV 추출 script
실행 위치: admrule-kr 저장소 root
출력: admrule_kr_mapping.csv
"""
import os
import csv
import re
import yaml
from pathlib import Path


def extract_frontmatter(filepath: str) -> dict:
    """파일에서 YAML frontmatter 추출."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}
    
    # frontmatter는 --- ~ --- 사이
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    
    fm_text = match.group(1)
    try:
        fm = yaml.safe_load(fm_text)
        return fm if isinstance(fm, dict) else {}
    except yaml.YAMLError as e:
        return {"yaml_error": str(e)}


def main():
    repo_root = Path(".")
    output_csv = "admrule_kr_mapping.csv"
    
    # 모든 .md 파일 찾기 (README.md 제외)
    md_files = [
        f for f in repo_root.rglob("*.md")
        if f.name != "README.md" and ".git" not in str(f)
    ]
    
    print(f"Found {len(md_files)} .md files")
    
    rows = []
    skipped = 0
    
    for md_file in md_files:
        fm = extract_frontmatter(str(md_file))
        
        if not fm or "error" in fm or "yaml_error" in fm:
            skipped += 1
            continue
        
        # 13자리 MST가 있는 row만 추출
        legal_mst = str(fm.get("행정규칙일련번호", "")).strip()
        if not legal_mst or len(legal_mst) != 13:
            skipped += 1
            continue
        
        # 디렉토리 path: 부처/외청/rule_type/행정규칙명
        rel_path = md_file.relative_to(repo_root)
        path_parts = list(rel_path.parts)
        
        # 부처/외청/rule_type/행정규칙명 추출
        # path_parts: [부처, 외청, rule_type, 행정규칙명, 파일명.md]
        ministry = path_parts[0] if len(path_parts) > 0 else ""
        sub_org = path_parts[1] if len(path_parts) > 1 else ""
        rule_type_dir = path_parts[2] if len(path_parts) > 2 else ""
        rule_name_dir = path_parts[3] if len(path_parts) > 3 else ""
        filename = path_parts[-1]
        directory_path = "/".join(path_parts[:-1])  # 파일명 제외
        
        # 기관경로 (list → join)
        org_path = fm.get("기관경로", [])
        if isinstance(org_path, list):
            org_path_str = " > ".join(org_path)
        else:
            org_path_str = str(org_path)
        
        rows.append({
            "directory_path": directory_path,
            "directory_name": rule_name_dir or rule_type_dir,
            "filename": filename,
            "fm_title": str(fm.get("행정규칙명", "")).strip(),
            "rule_type": str(fm.get("행정규칙종류", "")).strip(),
            "ministry_name": str(fm.get("상위기관명", "")).strip(),
            "sub_org_name": str(fm.get("소관부처명", "")).strip(),
            "org_path": org_path_str,
            "rule_id": str(fm.get("행정규칙ID", "")).strip(),
            "legal_mst": legal_mst,
            "source_file": str(rel_path),
        })
    
    # CSV write
    fieldnames = [
        "directory_path", "directory_name", "filename",
        "fm_title", "rule_type", "ministry_name", "sub_org_name", "org_path",
        "rule_id", "legal_mst", "source_file"
    ]
    
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Extracted {len(rows)} rows to {output_csv}")
    print(f"Skipped (no MST or yaml error): {skipped}")
    
    # 분포 출력
    from collections import Counter
    rule_type_dist = Counter(r["rule_type"] for r in rows)
    print(f"\nRule type 분포:")
    for rt, cnt in rule_type_dist.most_common():
        print(f"  {rt}: {cnt}")
    
    # 부처별 분포 (top 10)
    ministry_dist = Counter(r["ministry_name"] for r in rows)
    print(f"\n부처별 분포 (top 10):")
    for m, cnt in ministry_dist.most_common(10):
        print(f"  {m}: {cnt}")
    
    # MST 13자리 검증
    invalid_mst = [r for r in rows if len(r["legal_mst"]) != 13 or not r["legal_mst"].isdigit()]
    if invalid_mst:
        print(f"\n⚠ 13자리 MST 검증 실패: {len(invalid_mst)}건")
    else:
        print(f"\n✓ 모든 MST가 13자리 숫자")


if __name__ == "__main__":
    main()
