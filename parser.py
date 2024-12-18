import requests
from bs4 import BeautifulSoup, Tag
from fuzzywuzzy import fuzz
import json


headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

def get_pc_info(tag_name:str):
    r = requests.get(f"https://hackerboards.com/compare/{tag_name}/", headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    trs: list[Tag] = soup.find_all('tr')
    pic = f"https://hackerboards.com/image/{tag_name}/board.jpg"
    name = trs[0].find_all("strong")[-1].text.strip()
    
    result = {
        "name": name,
        "pic": pic,
        "info": {}
    }
    
    for tr in trs[1:]:
        th = tr.find('th').text.strip()
        td = tr.find('td').text.strip()
        result["info"][th] = td
    
    return result
        
def benchmark_search(name:str, cpu:str=""):
    r = requests.get("https://github.com/ThomasKaiser/sbc-bench/blob/master/Results.md", headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    
    scripts = soup.find_all('script')
    for script in scripts:
        if "richText" in script.text:
            data = json.loads(script.text)
            break
        
    soup = BeautifulSoup(data['payload']['blob']['richText'], 'lxml')
    table = soup.find_all('table')[0]
    
    trs: list[Tag] = table.find_all('tr')
    
    most_index = -1
    most_percentage = 0
    
    if cpu:
        search_name = f"{name} ({cpu})"
    else:
        search_name = name
        
    for i, tr in enumerate(trs):
        
        table_name = tr.find('td')
        
        perc = fuzz.ratio(table_name, search_name)
        if perc > most_percentage:
            most_percentage = perc
            most_index = i
    
    if most_index == -1:
        return {}
    founded: list[Tag] = trs[most_index].find_all('td')
    
    result = {
        "Name": founded[0].text.strip(),
        "Clockspeed": founded[1].text.strip(),
        "Kernel": founded[2].text.strip(),
        "Distro": founded[3].text.strip(),
        "7-zip multi": founded[4].text.strip(),
        "7-zip single": founded[5].text.strip(),
        "AES": founded[6].text.strip(),
        "Memcpy": founded[7].text.strip(),
        "Memset": founded[8].text.strip(),
        "kH/s": founded[9].text.strip(),
    }
    return result

def get_full_info(tag_name:str, cpu:str=None):
    res = get_pc_info(tag_name)
    
    if cpu:
        r = benchmark_search(res["name"], res["info"]["CPU"].split()[1])
    else:
        r = benchmark_search(res["name"])
    
    res["benchmark"] = r
    return res
    
if __name__ == '__main__':
    res = get_full_info("asus-tinker-board-s")
    import json
    with open('result.json', 'w', encoding="utf-8") as f:
        json.dump(res, f, indent=4)