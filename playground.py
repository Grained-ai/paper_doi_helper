# import json
#
# with open(r'W:\Personal_Project\grained_ai\projects\paper_doi_helper\src\all_journals.txt', 'r') as f:
#     raw = f.read()
# j_list = [i for i in raw.split('\n') if i]
# print(j_list)
#
# with open(r'W:\Personal_Project\grained_ai\projects\paper_doi_helper\modules\scripts\output_elsevier.json', 'r', encoding='utf-8') as f:
#     all_raw = json.load(f)
#
# j_list2 = []
# for p in all_raw:
#     if all_raw[p]:
#         j_list2.extend(all_raw[p])
#
# print(j_list2)
#
# import re
#
#
# def normalize_journal_name(journal_name):
#     """
#     Normalize the journal name by removing extra characters and converting to lowercase.
#
#     :param journal_name: The original journal name.
#     :return: Normalized journal name.
#     """
#     # Remove extra characters like '.', ',', etc.
#     normalized_name = re.sub(r'[.,;:]', '', journal_name).strip()
#     # Convert to lowercase
#     normalized_name = normalized_name.lower()
#     return normalized_name
#
#
# def match_journals(list1, list2):
#     """
#     Match journals between two lists, considering case insensitivity and extra characters.
#
#     :param list1: First list of journal names.
#     :param list2: Second list of journal names.
#     :return: A list of tuples containing matched journal names (list1, list2).
#     """
#     # Normalize both lists
#     normalized_list1 = [normalize_journal_name(name) for name in list1]
#     normalized_list2 = [normalize_journal_name(name) for name in list2]
#
#     # Find matches
#     matches = []
#     for name1 in normalized_list1:
#         for name2 in normalized_list2:
#             if name1 == name2:
#                 # Find the original names in the input lists
#                 original_name1 = next((name for name in list1 if normalize_journal_name(name) == name1), None)
#                 original_name2 = next((name for name in list2 if normalize_journal_name(name) == name2), None)
#                 if original_name1 and original_name2:
#                     matches.append((original_name1, original_name2))
#                 break  # Break inner loop once a match is found
#
#     return matches
#
# matches = match_journals(j_list, j_list2)
# print(matches)

# proxyAddr = "tun-vdpzuj.qg.net:11753"
# authKey = "7063131B"
# password = "C8FBFB115FD4"
# proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
#     "user": authKey,
#     "password": password,
#     "server": proxyAddr,
# }
# print(proxyUrl)
# proxies = {
#     "http": proxyUrl,
#     "https": proxyUrl,
# }
import json
# resp = requests.get(url=url, headers=headers, proxies=proxies,verify=False,timeout = 20)
with open('W:\Personal_Project\grained_ai\projects\paper_doi_helper\modules\scripts\mapping.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

from collections import defaultdict

def count_publishers(data):
    """
    统计每个出版社出现的次数，并按次数从多到少排序，同时输出对应的百分比。

    :param data: 一个字典，键是期刊名称，值是出版社名称。
    :return: 一个列表，每个元素是一个元组，包含出版社名称、出现次数和百分比。
    """
    publisher_count = defaultdict(int)
    total_journals = len(data)

    # 统计每个出版社出现的次数
    for journal_name, publisher in data.items():
        publisher_count[publisher] += 1

    # 计算每个出版社的百分比
    publisher_stats = [
        (publisher, count, (count / total_journals) * 100)
        for publisher, count in publisher_count.items()
    ]

    # 按出现次数从多到少排序
    publisher_stats.sort(key=lambda x: x[1], reverse=True)

    return publisher_stats

# # 示例数据
# data = {
#     "Example Journal": "Publisher A",
#     "Another Journal": "Publisher B",
#     "Third Journal": "Publisher A",
#     "Fourth Journal": "Publisher C",
#     "Fifth Journal": "Publisher B",
#     "Sixth Journal": "Publisher A"
# }

# 调用函数
publisher_stats = count_publishers(data)
for publisher, count, percentage in publisher_stats:
    print(f"Publisher: {publisher}, Count: {count}, Percentage: {percentage:.2f}%")