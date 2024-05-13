import requests
import json
import time
from bs4 import BeautifulSoup
import multiprocessing
from datetime import datetime
from http.cookies import SimpleCookie
import re
import os
from utils.PgConnector import insert_data

module_path = os.path.dirname(__file__)

with open(module_path + '/cookies.txt', mode='r', encoding='utf-8') as f:
    cookie = SimpleCookie()
    print(cookie)
    cookie.load(f.read())
    cookies = {k: v.value for k, v in cookie.items()}
    # cookies = json.loads(f.read())

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}

def download_cv(profile_id):
    """
    download pdf CV
    """
    params = {
        'resume_id': profile_id,
    }

    response = requests.get(
        'https://careerviet.vn/en/employers/popup/downloadresume',
        params=params,
        cookies=cookies,
        headers=headers,
        stream=True
    )
    with open(module_path + '/CVs/{}.pdf'.format(profile_id), 'wb') as f:
        f.write(response.content)


def page_parser(parse_obj, alias_name):
    """
    parsing page components as requirements
    """
    lst_item = []
    for s in parse_obj:
        # print(s.find('a',{'class': 'name'}).get('href'))
        PROFILE = s.find('a',{'class': 'name'})
        item = {
            'datasource': 'careerviet',
            'profile_id' :  re.findall(r'(.+?).html', PROFILE.get('href').split('/')[-1])[0],
            'title' : s.find('a',{'class': 'job-title'}).text.replace('\n',''),
            'candidate_name' : PROFILE.text.split('#')[0].replace('\n','').replace('\t','').replace('\r','').strip(),
            'ref_link' : PROFILE.get('href'),
            'status' : s.select_one('a > span',{'class': 'hastag'}).text if s.select_one('a > span',{'class': 'hastag'}) else '',
            'education' : s.select_one('ul > li:nth-child(1) > p').text.split(':')[-1].strip(),
            'experienced' : s.select_one('td:nth-child(2) > p').text.replace('\n','').replace('\t','').strip(),
            'desired_salary' : s.select_one('td:nth-child(3) > p').text.replace('\r','').replace('\n','').replace('\t','').strip(),
            'current_location' : s.select_one('td:nth-child(4)').text.replace('\r','').replace('\n','').replace('\t','').strip(),
            'orther' : s.find('div',{'class':'jobs-view-detail'}).find('p').text.replace('\n','').replace('\t','').replace('\r','').strip(),
            'request_time': str(datetime.now())
        }
        # yield item
        lst_item.append(item)

    insert_data(lst_item)
    return lst_item
    # with open(module_path + f"data\\{alias_name}.json", "w+", encoding="utf-8") as outfile:
    #     outfile.write(json.dumps(lst_item, ensure_ascii=False))
    #     return [pf['profile_id'] for pf in lst_item]

def worker(link):
    """
    align a scaping process
    """
    rsp = requests.get(link, headers=headers)
    encoding = rsp.encoding if 'charset' in rsp.headers.get('content-type', '').lower() else None
    # print(encoding)
    rs = BeautifulSoup(rsp.content.decode(encoding,'ignore'), 'html.parser')
    obj = rs.find('div', {"class":"table table-jobs-posting"}).find('tbody').find_all('tr')
    category = re.findall(r'/category/(.+?)/', link)[0]
    page_num = link.split('/')[-1]
    pf_list = page_parser(obj, f'{category}_{page_num}')
    if pf_list:
        for pf in pf_list:
            download_cv(pf['profile_id'])
            time.sleep(1)
    
    
def career_link_generator(category, page_depth=3):
    """
    generate links to carrer pages
    """
    for i in range(1, page_depth+1):
        # print(f'https://careerviet.vn/en/resume-search/category/{category}/sort/date_desc/page/{i}')
        yield f'https://careerviet.vn/en/resume-search/category/{category}/sort/date_desc/page/{i}'



def run(p_category, p_page = 1):
    with multiprocessing.Pool(2) as pool:
        pool.map(worker, career_link_generator(p_category, p_page))


if __name__ == "__main__":
    
    with multiprocessing.Pool(2) as pool:
        # parallel the scapring process
        pool.map(worker, career_link_generator('human-resources', page_depth=1))
    
    ## test one link
    # category = 'architect'
    # i = 3
    # onelink_url = f'https://careerviet.vn/en/resume-search/category/{category}/sort/date_desc/page/{i}'
    # worker(onelink_url)
   
    
