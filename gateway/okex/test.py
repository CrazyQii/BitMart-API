import re

# str = 'btcusdt@trade'
# print(re.search('@.+', str).group(0))

Asin = [{'Asin': 'b2b'}]
i = 0
for item in Asin:
    if item['Asin'] == 'b2b':
        Asin[i] = 'sdf'
    i = i + 1
print(Asin)