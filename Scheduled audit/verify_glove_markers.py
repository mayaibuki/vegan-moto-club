"""Double-check: scan ALL 59 unique gloves for ANY case-insensitive 'vegan'
substring (not just the strict <h2>Vegan</h2>) to ensure nothing is missed."""
import requests, re, time

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

r = requests.get('https://revitsport.com/en-us/collections/men-motorcycle-gloves/products.json',
                 params={'limit': 250}, headers=H, timeout=30)
prods = r.json()['products']
seen, uniq = set(), []
for p in prods:
    b = re.sub(r'\s+', ' ', re.sub(r'\s*\|\s*.*$', '', p['title'])).strip()
    if b in seen: continue
    seen.add(b); uniq.append((b, p['handle']))

for b, h in uniq:
    try:
        pr = requests.get(f'https://revitsport.com/en-us/products/{h}', headers=H, timeout=30)
        n = len(re.findall(r'vegan', pr.text, re.I))
        if n:
            print(f'{n:2d}  {b}')
    except Exception as e:
        print(f'ERR {b}: {e}')
    time.sleep(0.25)
print('done')
