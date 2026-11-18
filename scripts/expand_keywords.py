"""매장 키워드 확장 1,500개 → raw/도로시펫 키워드 - 대구 확장 1000개.csv (사용자 요청 2026-11-16 "페이지 천개 더", 2026-11-18 "500개 더" — 앞 1,000은 그대로, 뒤에 500 추가)

  python -I scripts/expand_keywords.py
축(앞에서부터 채우고 1,000에서 끊음), 기존 1,000과 겹치면 건너뜀. 검색량은 측정 안 함(0).
 1. 견종 92종(특수견·묘 분류 제외) × 패턴 11 — 부산 확장과 같은 패턴을 대구권 지명으로
 2. 대구 동네 33곳(규모 큰 순) × 분양 어휘 8
 3. 경북 도시(포항·경주·김천·하양) × 분양 분류 건수 많은 견종 '분양'
 4. 대구 동네 × 짧은 어휘(강아지·고양이·애견·반려견분양·반려묘분양)
 5. (2026-11-18) 견종 × 종류별 패턴 4 — 개: ○○강아지분양·○○새끼·○○분양비용·○○분양샵, 고양이: ○○고양이분양·○○새끼·○○분양비용·○○분양샵
 6. 구미·경산·포항 × 견종 '입양'
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'raw', '도로시펫 키워드 - 대구 1000개.csv')
OUT = os.path.join(ROOT, 'raw', '도로시펫 키워드 - 대구 확장 1000개.csv')
TARGET = 1500
KIND_PATTERNS = {'dog': ['{}강아지분양', '{}새끼', '{}분양비용', '{}분양샵'], 'cat': ['{}고양이분양', '{}새끼', '{}분양비용', '{}분양샵']}
CITY_PATTERNS2 = ['구미{}입양', '경산{}입양', '포항{}입양']
BREED_PATTERNS = ['{}분양', '대구{}분양', '{}분양가', '{}입양', '대구{}입양', '{}가격', '{}분양가격', '구미{}분양', '경산{}분양', '영천{}분양', '대구{}']
PLACE_WORDS = ['강아지분양', '고양이분양', '애견샵', '펫샵', '애견분양', '강아지입양', '고양이입양', '애견분양샵']
CITY_PATTERNS = ['포항{}분양', '경주{}분양', '김천{}분양', '하양{}분양']
PLACE_WORDS2 = ['강아지', '고양이', '애견', '반려견분양', '반려묘분양']  # 4. 동네 × 짧은 어휘 (앞 축으로 1,000이 안 차서)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    have = {r[0].replace(' ', '') for r in list(csv.reader(open(BASE, encoding='utf-8-sig')))[1:] if r and r[0].strip()}
    breeds = json.load(open(os.path.join(ROOT, 'data', 'breeds.json'), encoding='utf-8'))['breeds']
    allb = [b for b in breeds if 'special' not in (b['site'] or '')]
    top = sorted([b for b in allb if b['siteCount']], key=lambda b: -b['siteCount'])
    places = json.load(open(os.path.join(ROOT, 'data', 'regions.json'), encoding='utf-8'))['places']
    plist = sorted([k for k in places if k != '대구'], key=lambda k: -(places[k].get('dongHouseholds') or places[k]['households']))
    out, how = [], {}

    def add(kw, axis):
        k = kw.replace(' ', '')
        if k in have or len(out) >= TARGET: return
        have.add(k); out.append(k); how[axis] = how.get(axis, 0) + 1

    for pat in BREED_PATTERNS:
        for b in allb: add(pat.format((b['siteName'] or b['name']).replace(' ', '')), '견종×패턴')
    for w in PLACE_WORDS:
        for p in plist: add(f'{p}{w}', '동네×어휘')
    for pat in CITY_PATTERNS:
        for b in top: add(pat.format(b['siteName'].replace(' ', '')), '경북도시×견종')
    for w in PLACE_WORDS2:
        for p in plist: add(f'{p}{w}', '동네×짧은어휘')
    for i in range(4):
        for b in allb: add(KIND_PATTERNS[b['kind']][i].format((b['siteName'] or b['name']).replace(' ', '')), '견종×종류별패턴')
    for pat in CITY_PATTERNS2:
        for b in top: add(pat.format(b['siteName'].replace(' ', '')), '경북도시×견종입양')
    assert len(out) == TARGET, len(out)
    with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['검색어', '노출수(부산 참고)', '클릭수(부산 참고)', '원본 키워드', '비고'])
        for i, k in enumerate(out): w.writerow([k, '', '', '', '확장(2026-11-16)' if i < 1000 else '확장(2026-11-18)'])
    print(f'확장 {len(out)}: ' + ' · '.join(f'{a} {n}' for a, n in how.items()))


if __name__ == '__main__':
    main()
