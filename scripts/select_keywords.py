"""도로시펫 대구점 키워드 → data/pages.json + keywords/도로시펫_대구_1000.xlsx

  python -I scripts/select_keywords.py
raw/도로시펫 키워드 - 대구 1000개.csv 1,000행 그대로(부산 1,000개2.csv 를 대구권 지명으로 바꾼 953 + 견종 패턴 47, 2026-11-13·16).
노출·클릭은 부산 원본 참고값. 추가는 사용자가 요청한 만큼만. 엑셀은 요약 시트 없이 키워드 시트가 첫 시트.
"""
import csv, json, os, re, sys
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'raw', '도로시펫 키워드 - 대구 1000개.csv')


def slug(kw):
    return re.sub(r'\s+', '-', kw.strip())


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    rows = [r for r in list(csv.reader(open(SRC, encoding='utf-8-sig')))[1:] if r and r[0].strip()]
    n = lambda v: int(re.sub(r'\D', '', v or '') or 0)
    store, seen = [], set()
    for r in rows:
        kw = r[0].strip()
        assert kw not in seen, kw
        seen.add(kw)
        store.append(dict(kw=kw, slug=slug(kw), set='store', impressions=n(r[1]), clicks=n(r[2]), dupRows=0, added=bool(r[4].strip()) if len(r) > 4 else False, src=r[3].strip() if len(r) > 3 else ''))
    assert len(store) == 1000, len(store)
    json.dump({'store': store, 'franchise': []}, open(os.path.join(ROOT, 'data', 'pages.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

    wb = openpyxl.Workbook(); ws = wb.active; ws.title = '키워드'
    ws.append(['키워드', 'URL', '노출수(부산 참고)', '클릭수(부산 참고)', '부산 원본 키워드', '비고'])
    for p in store:
        ws.append([p['kw'], f"/{p['slug']}/", p['impressions'] or None, p['clicks'] or None, p['src'], '추가(견종 건수 순)' if p['added'] else ''])
    for col, w in zip('ABCDEF', (28, 32, 14, 14, 24, 18)): ws.column_dimensions[col].width = w
    os.makedirs(os.path.join(ROOT, 'keywords'), exist_ok=True)
    wb.save(os.path.join(ROOT, 'keywords', '도로시펫_대구_1000.xlsx'))
    print(f'매장 {len(store)} (지명 바꾼 {sum(1 for p in store if p["src"])} · 추가 {sum(1 for p in store if p["added"])})')


if __name__ == '__main__':
    main()
