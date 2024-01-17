import json
from pathlib import Path


Img_data = {}



def clean_data():
    global Img_data
    with open(f"../../assets/data/json/yande.re/yande.re2022.03-02_03-02.json", 'r', encoding='utf-8') as raw:
        Img_data = json.load(raw)
        for _ in Img_data:
            Img_data[_]["retrieved"] = True
    with open(f"../../assets/data/json/yande.re/yande.re2022.03-02_03-02.json", 'w', encoding='utf-8') as m:
        json.dump(Img_data, m, indent=4, ensure_ascii=False)


def debug_data():
    global Img_data
    p = Path('../../assets/data/json/yande.re')
    file_list = [x for x in p.iterdir() if x.is_file()]
    for q in file_list:
        with q.open(encoding='utf-8') as qr:
            Img_data = json.load(qr)
        keys = [*Img_data]
        has_empty = [x for x in keys if len(Img_data[x]) == 2]
        if has_empty:
            print(q)


if __name__ == "__main__":
    debug_data()
