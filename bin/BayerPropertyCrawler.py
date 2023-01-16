
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
from datetime import datetime

# input to choose project you want to scrape
project = input('Please enter the project name (EP or BG): ')
project = project.upper()

if project == 'EP':
    url = "https://bayerproperty.com/lakoprojektek/budapest/elite-park-2-3"
    merger = 'Elite Park 2-3 '
    short = 'EP'
elif project == 'BG':
    url = "https://bayerproperty.com/lakoprojektek/budapest/balance-garden"
    merger = 'Balance Garden '
    short = 'BG'
else:
    print('Choose EP or BG!')

r = requests.get(url)
r = r.text.split('<section class="section section-project-details section-project-details-homes" id="section-homes">')[1]
soup = BeautifulSoup(r, 'html.parser')

ran = range(len(soup.find_all('meta', attrs={'itemprop': 'position'})))

name = soup.find_all('meta', attrs={'itemprop': 'name'})
name = [name[i]['content'] for i in ran]
image = soup.find_all('meta', attrs={'itemprop': 'image'})
image = [image[i]['content'] for i in ran]

attr = soup.find_all('span', attrs={'class': 'home-attribute'})
val = soup.find_all('span', attrs={'class': 'home-value'})

attr_ = [attr[i].text for i in range(len(attr))]
val_ = [val[i].text for i in range(len(val))]

testl = []
for idx, el in enumerate(val_):
    if short in el:
        id = el
    else:
        testl.append({id: {attr_[idx]: val_[idx]}})

result = defaultdict(dict)
for d in testl:
    for key, value in d.items():
        result[key].update(value)

df = pd.DataFrame.from_dict(result, orient='index').reset_index(names='Lakás')
df['Ára'] = df['Ára'].fillna('Foglalt/Eladva')
df['Ára'] = df['Ára'].str.replace(' Ft', '')
df['Méret'] = df['Méret'].str.replace(' m2', '')
df['Terasz'] = df['Terasz'].str.replace(' m2', '')

df2 = pd.DataFrame({'name': name, 'Kép link': image})
df2['name'] = df2['name'].str.replace(merger, '')

df_final = pd.merge(df, df2, left_on='Lakás', right_on='name', how='left')

# drop name column
df_final.drop('name', axis=1, inplace=True)


datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
df_final.to_excel(f'BayerProperty_{short}_Export_{datetime_now}.xlsx', index=False)