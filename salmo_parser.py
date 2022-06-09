import json
from dataclasses import asdict, dataclass
from typing import List

import requests
from lxml import html
from toolz import get_in


@dataclass
class SalmoStoreData:
    name: str
    image_url: str
    postal_code: str
    address: str
    lat: float
    lon: float
    store_url: str
    phone_number: str
    working_hours: List[str]


url = "https://www.salmo.by/contacts/stores/"

payload = {}
headers = {
    "authority": "www.salmo.by",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7",
    "cache-control": "no-cache",
    "cookie": "PHPSESSID=ATm9rjwNQtTciKyihp8O1DSPNcbvqzCi; BITRIX_SM_GUEST_ID=942202; BITRIX_SM_LAST_ADV=5_Y; BITRIX_SM_SALE_UID=823ba73aa100c87492549a724f578060; _ym_debug=null; BITRIX_CONVERSION_CONTEXT_s1=%7B%22ID%22%3A22%2C%22EXPIRE%22%3A1654808340%2C%22UNIQUE%22%3A%5B%22conversion_visit_day%22%5D%7D; _gcl_au=1.1.1556590252.1654797870; _ga=GA1.2.1727134990.1654797870; _gid=GA1.2.2147135285.1654797870; _ym_uid=1654797870927546123; _ym_d=1654797870; _ym_visorc=w; _ym_isad=2; BX_USER_ID=84f72931af1f5c7aeca75d9d0f50871d; _fbp=fb.1.1654797870640.380701111; BITRIX_SM_LAST_VISIT=09.06.2022%2021%3A05%3A02",
    "pragma": "no-cache",
    "referer": "https://www.salmo.by/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}

response = requests.request("GET", url, headers=headers, data=payload)

page = html.fromstring(response.content)

json_strings = page.xpath(
    '//div[@class="phone_email"]/script/text()'
)

days_map = {
    'Monday': 'Пн',
    'Tuesday': 'Вт',
    'Wednesday': 'Ср',
    'Thursday': 'Чт',
    'Friday': 'Пт',
    'Saturday': 'Сб',
    'Sunday': 'Вс',
}

stores: List[dict] = []

for salmo_store in json_strings:
    salmo_dict = json.loads(salmo_store)
    working_hours_dict = salmo_dict['openingHoursSpecification'][0]
    days = working_hours_dict['dayOfWeek']
    time = f'{working_hours_dict["opens"]}-{working_hours_dict["closes"]}'
    working_hours = [f'{days_map.get(day)} {time}' for day in days]
    store_data = SalmoStoreData(
        name=salmo_dict['name'],
        image_url=salmo_dict['image'],
        postal_code=get_in(['address', 'postalCode'], salmo_dict),
        address=', '.join(
            [
                get_in(['address', 'addressCountry'], salmo_dict),
                get_in(['address', 'addressRegion'], salmo_dict),
                get_in(['address', 'addressLocality'], salmo_dict),
                get_in(['address', 'streetAddress'], salmo_dict),
            ],
        ),
        lat=float(get_in(['geo', 'latitude'], salmo_dict)),
        lon=float(get_in(['geo', 'longitude'], salmo_dict)),
        store_url=salmo_dict['url'],
        phone_number=salmo_dict['telephone'],
        working_hours=working_hours,
    )
    stores.append(asdict(store_data))

with open('./salmo.json', 'w') as file:
    json.dump(stores, file, ensure_ascii=False, indent=4)
