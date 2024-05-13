import requests
import json
import re
import os
from time import sleep
from datetime import datetime
# from threading import Thread
from bs4 import BeautifulSoup
import urllib.parse
from utils.PgConnector import insert_data
module_path = os.path.dirname(__file__)
cookies = open(module_path + '/cookies.txt', mode='r', encoding='utf-8').read().split('\n')[0]
cv_save_folder = "CVs"

# delay in sec
request_delay = 1

## for tracing debug
# log_file = "logs.log"
# def print_log(text):
#     with open(log_file, "a") as f:
#         f.write(text + "\n")


class LinkedInParser():
    def __init__(self, meta_data) -> None:
        self.meta_data = meta_data
        pass

    def request_cv(self, profile_id, profile_link):
        """
        get CV downloadlink from linkedin
        """
        link = "https://www.linkedin.com/voyager/api/graphql"
        params = {
            'action': 'execute',
            'queryId': 'voyagerIdentityDashProfileActionsV2.ca80b3b293240baf5a00226d8d6d78a1'
        }
        headers = {
            'Accept': 'application/vnd.linkedin.normalized+json+2.1',
            'Cookie': cookies,
            'Csrf-Token': re.findall(r'JSESSIONID="(.+?)"', cookies)[0],
            'Dnt': '1',
            'Referer': profile_link,
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'X-Li-Lang': 'en_US',
            'X-Li-Page-Instance': 'urn:li:page:d_flagship3_search_srp_people_load_more;Ux/gXNk8TtujmdQaaFmrPA==',
            'X-Li-Track': '{"clientVersion":"1.13.9792","mpVersion":"1.13.9792","osName":"web","timezoneOffset":6,"timezone":"Asia/Dhaka","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1.3125,"displayWidth":1920.1875,"displayHeight":1080.1875}',
            'X-Restli-Protocol-Version': '2.0.0',
        }
        data = {
            "variables": {
                "profileUrn": "urn:li:fsd_profile:{}".format(profile_id)
            },
            "queryId": "voyagerIdentityDashProfileActionsV2.ca80b3b293240baf5a00226d8d6d78a1",
            "includeWebMetadata": True
        }
        try:
            resp = requests.post(link, headers=headers,
                                 params=params, data=json.dumps(data)).json()
            # print_log(resp)
        except:
            # print_log("Failed to open {}".format(link))
            return None
        try:
            cv_pdf_link = resp.get('data').get('data').get(
                'doSaveToPdfV2IdentityDashProfileActionsV2').get('result').get('downloadUrl')
        except:
            # print_log("Error processing CV link")
            return None
        return cv_pdf_link

    def download_cv(self, link, profile_id):
        # print_log("Downloading CV from {}".format(link))
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cookie': cookies,
            'Cache-Control': 'max-age=0',
            'Dnt': '1',
            'Referer': 'https://www.linkedin.com/in/{}/'.format(profile_id),
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        try:
            resp = requests.get(link, headers=headers)
            with open(os.path.join(cv_save_folder, f'{profile_id}.pdf'), 'wb') as f:
                f.write(resp.content)
        except:
            print("Failed to download CV")

    def get_profile_id(self, link):
        if not link.lower().startswith('http'):
            print(link)
            link = 'https://' + link
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Cookie': cookies,
            'Dnt': '1',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        try:
            resp = requests.get(link, headers=headers).text
        except:
            # print_log("Failed to open {}".format(link))
            return False
        try:
            profile_id = re.findall(
                r'urn:li:fsd_memberRelationship:(.+?)\&quot;', resp)[0]
        except:
            # print_log( "Could not parse profile ID for the profile {}".format(link))
            return False
        return profile_id

    # def start_process_thread(self):
    #     thread = Thread(target=self.process_profile_list, args=())
    #     thread.start()

    def process_profile_list(self):
        # meta_data = [link.strip() for link in self.meta_data if link.strip()]
        for item in self.meta_data:
            profile_id = self.get_profile_id(item['ref_link'])
            print('>>> ProfileID', profile_id)
            if profile_id:
                item['profile_id'] = profile_id
                download_link = self.request_cv(profile_id, item['ref_link'])
                if download_link is not None:
                    self.download_cv(download_link, profile_id)
            sleep(request_delay)
        # return self.meta_data
        insert_data(self.meta_data)
        
        ## write to json 
        # with open(module_path + f"data\\{self.meta_data[0]['title'].replace(' ','_')}.json",mode= "w+", encoding="utf-8") as outfile:
        #     outfile.write(json.dumps(self.meta_data, ensure_ascii=False))



headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

def google_site_search(title, location, orther=None):
    """
    google search query to get list of profile relate
    """
    query= f'site: linkedin "{title}" people {location} {orther or ""} -job'
    response = requests.get("https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
                        , headers=headers)
    s = BeautifulSoup(response.content, 'html.parser')
    cont = s.find('div', {"id":"rso"})
    meta_data = []
    for i in cont.find_all('a'):
        # element = i.find('a') 
        if i is not None and 'linkedin' in i.get('href') and '?' not in i.get('href'):
            if i.find('h3'):
                meta_tag = i.find('h3').text
                print(meta_tag)
                meta_data.append({
                        "datasource": 'linkedin',
                        "candidate_name": meta_tag.split(' - ')[0],
                        "title": title,
                        "orther": meta_tag + (orther or ''),
                        "current_location": location,
                        "request_time": str(datetime.now()),
                        "ref_link": i.get('href')
                        })
    return meta_data


def run(p_title, p_location = 'viet nam', p_orther = None):
    downloader = LinkedInParser(google_site_search(title=p_title, location = p_location, orther=p_orther))
    downloader.process_profile_list()

if __name__ == "__main__":
    if not os.path.exists(cv_save_folder):
        os.mkdir(cv_save_folder)
    p_title = "devops"
    p_location = "viet nam"
    downloader = LinkedInParser(google_site_search(title=p_title, location = p_location))
    downloader.process_profile_list()
