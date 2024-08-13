import json
import os
from collections import defaultdict
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

with open('projects.json', 'r', encoding='utf-8') as f:
    project_dict = json.load(f)
    f.close()

project_list = {key: val['short'] for key, val in project_dict.items()}

print('You can choose from the following projects:')
for key, val in project_list.items():
    print(f'\tFor {key}, enter {val}')

project = input('Please enter the chosen project name: ').upper()
project = project

for key, value in project_dict.items():
    if project == value['short']:
        url = value['url']
        merger = value['merger']
        short = value['short']
        break

if project != value['short']:
    print('Choose a valid project! Choose from the list above.')

else:
    pass

r = requests.get(url)
r = r.text.split(
    '<section class="section section-project-details section-project-details-homes" id="section-homes">')[1]
soup = BeautifulSoup(r, 'html.parser')

ran = range(len(soup.find_all('meta', attrs={'itemprop': 'position'})))

name = soup.find_all('meta', attrs={'itemprop': 'name'})
name = [name[i]['content'].replace(merger, '') for i in ran]
image = soup.find_all('meta', attrs={'itemprop': 'image'})
image = [image[i]['content'] if i < len(image) else None for i in ran]

attr = soup.find_all('span', attrs={'class': 'home-attribute'})
val = soup.find_all('span', attrs={'class': 'home-value'})

attr_ = [attr[i].text for i in range(len(attr))]
val_ = [val[i].text for i in range(len(val))]

temp_list = []
for idx, el in enumerate(val_):
    if short in el:
        id = el
    else:
        temp_list.append({id: {attr_[idx]: val_[idx]}})

result = defaultdict(dict)
for d in temp_list:
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
df_final['Kép link'] = '=HYPERLINK("' + df_final['Kép link'] + '")'

datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs('export', exist_ok=True)
df_final.to_excel(
    f'export/BayerProperty_{short}_Export_{datetime_now}.xlsx', index=False)
