import pprint

import requests

base_url = 'http://127.0.0.1:8080/api/jobs'

# print(requests.get(url=base_url))
# print(requests.get(url=base_url + '/8'))
# print(requests.get(url=base_url + '/999'))
# print(requests.get(url=base_url + '/abc'))

# print(requests.post(url=base_url,
#                     json={'team_leader': 1, 'job': 'TEST', 'id_category': 1,
#                           'work_size': 34, 'collaborators': '2, 3, 4', 'is_finished': False}).json())  # всё корректно
# print(requests.post(url=base_url,
#                     json={'team_leader': 3, 'job': 'TEST_2', 'id_category': 2,
#                           'work_size': 2, 'collaborators': '5, 7'}).json())  # не хватает параметра -- error
# print(requests.post(url=base_url,
#                     json={}).json())  # Пустые данные -- error
# print(requests.post(url=base_url,
#                     json={'team_leader': 3, 'job': 'TEST_4', 'id_category': 'any',
#                           'work_size': 2, 'collaborators': '5, 7'}).json())  # не верный id_category -- error


# new_job_id = requests.post(url=base_url,
#                            json={'team_leader': 1, 'job': 'TEST', 'id_category': 1,
#                                  'work_size': 34, 'collaborators': '2, 3, 4', 'is_finished': False}).json()
# print(new_job_id)
# pprint.pprint(requests.get(url=base_url).json())
# print(requests.delete(url=base_url + f'/{new_job_id["id"]}').json())
# print(requests.delete(url=base_url + '/000999333').json())
# print(requests.delete(url=base_url + '/ggafga').json())
# pprint.pprint(requests.get(url=base_url).json())


pprint.pprint(requests.get(url=base_url).json())
print(requests.put(url=base_url + '/7', json={'work_size': 12, 'is_finished': True}).json())  # Корректный
pprint.pprint(requests.get(url=base_url).json())
print(requests.put(url=base_url + '/7', json={'wze': 23}).json())  # Некорректный
pprint.pprint(requests.get(url=base_url).json())
print(requests.put(url=base_url + '/7', json={}).json())  # Некорректный
pprint.pprint(requests.get(url=base_url).json())
print(requests.put(url=base_url + '/fsafsa', json={'work_size': 23}).json())  # Некорректный
pprint.pprint(requests.get(url=base_url).json())

