"""Probe a REV'IT! glove product page to locate the vegan signal."""
import requests, re

H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

url = 'https://revitsport.com/en-us/products/en-motorcycles-gloves-endo-black-grey'
r = requests.get(url, headers=H, timeout=30)
html = r.text
print('status', r.status_code, 'len', len(html))

# Find all 'vegan' occurrences with context
print('\n=== VEGAN OCCURRENCES ===')
for m in re.finditer(r'vegan', html, re.I):
    s = max(0, m.start()-120)
    print(repr(html[s:m.end()+120]))
    print('---')

# Look for a .js or metafield endpoint / sustainability JSON
print('\n=== SUSTAINAB OCCURRENCES (first 5) ===')
for i, m in enumerate(re.finditer(r'sustainab', html, re.I)):
    if i >= 5: break
    s = max(0, m.start()-60)
    print(repr(html[s:m.end()+200]))
    print('---')
