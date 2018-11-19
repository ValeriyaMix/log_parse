# -*- encoding: utf-8 -*-
import datetime
import re
from collections import Counter

regexp_pattern = r"""\[
(?P<day>\d{2})
\/
(?P<month>\w{3})
\/
(?P<year>\d{4})
\s{1}
(?P<hours>\d{2})
:
(?P<minutes>\d{2})
:
(?P<seconds>\d{2})\]
\s{1}\"
(?P<request_type>[A-Z]*)
\s{1}
(?P<url>[a-zA-Z\d\:\/\.\&\@\?\#\%\=\_\-]*)
\s{1}
(?P<protocol>[A-Z]*)
\/
(?P<protocol_version>\d{1}.\d{1})
\"\s{1}
(?P<response_code>\d{3})
\s{1}
(?P<response_time>\d*)"""
re_parser = re.compile(regexp_pattern, re.VERBOSE)

url_pattern = r"""\w*:\/\/(?P<url>[a-zA-Z0-9\/.\-\_\@]*)\/?"""
url_parser = re.compile(url_pattern)


def parse_line(raw_log_line):
    result = re_parser.search(raw_log_line)
    if result:
        # print(result.groupdict())
        return result.groupdict()
    return None


def parse_url(raw_url):
    result = url_parser.search(raw_url)
    if result:
        # print(result.groupdict()['url'])
        return result.groupdict()['url']
    return ''


def get_formatted_line(parsed_line):
    str_datetime = '{day}/{month}/{year} {hours}:{minutes}:{seconds}'.format(**parsed_line)
    # print(str_datetime)
    return {
        'datetime': datetime.datetime.strptime(str_datetime, '%d/%b/%Y %H:%M:%S'),
        'request_type': parsed_line['request_type'],
        'url': parse_url(parsed_line['url']),
        'response_time': parsed_line['response_time']
    }


def read_log_file(file_name='log.log'):
    result = []
    with open(file_name) as f:
        for line in f.readlines():
            parsed_line = parse_line(line)
            # print(parsed_line)
            if not parsed_line:
                continue
            formatted_line = get_formatted_line(parsed_line)
            # print(formatted_line)
            result.append(formatted_line)
    return result

def filter_urls(lines, ignored_urls):
    result = []
    for line in lines:
        if line['url'] not in ignored_urls:
            result.append(line)
    return result



def filter_files(lines):
    result = []
    for line in lines:
        match_file = re.match(r"\.(jpg|png|css|gif|svg|js|jpeg)", line['url'])
        if not match_file:
            result.append(line)
    return result


# def filter_time(lines, start_at, stop_at):
#     result = []
#     if start_at and stop_at:
#         for line in lines:
#             if start_at <= line['datetime'] <= stop_at:
#                 result.append(line)
#     # elif start_at and not stop_at or not start_at and stop_at:
#     #     for line in lines:
#     #         if start_at <= line['datetime'] <= stop_at:
#     #             result.append(line)
#     return result
#
# def filter_request_type(lines):
#     result =[]
#     for line in lines:
#         request_type = re.match(r"\s(GET|POST|PUT)\s", line['request_type'])
#         if request_type:
#             result.append(line)
#     return result
#
def filter_www(lines):
    result = []
    for line in lines:
        raw_line_from_dict = line['url']
        www_matcher = re.match(r"www.[a-zA-Z0-9\/.\-\_\@]*\/?", raw_line_from_dict)
        # print (type(line['url']))
        if www_matcher:
            result.append(line['url'][4:])
        else:
            result.append(line['url'])
    return result

# def filter_www(lines):
#     result = []
#     for line in lines:
#         if re.match('www', str(line)):
#             line.replace('www', '')
#         result.append(line)
#     return result

# def search_avg(lines):
#     print(type(lines))
#     set_list = set(lines)
#     if len(lines) == len(set_list):
#         print('tha same is here')
#     return

def search_avg(lines):
    same_lines = []
    # diff_lines = []
    i = 0
    for line in lines:
        # for i in line:
        same_lines = set(line[i]['url'] & set(line[i+1]['url']))
        # if line['url'] == lines[int(line)+1]:
        #     same_lines.append(line)
        # else:
        #     diff_lines.append(line)
    return same_lines

def find_same(lines):
    # i = 0
    result_same = []
    result_dif = []
    for i in range(len(lines)-1):
        if lines[i]['request_type'] == lines[i+1]['request_type'] and lines[i]['url'] == lines[i+1]['url']:
            lines.append(result_same)
        else:
            lines.append(result_dif)
    return result_same, result_dif





# def return_milisec(lines):
#     result = []
#     for line in lines:
#         time_line = re.match(r'\d{5}', line['response_time'])
#         # print(type(line['response_time']))
#         if time_line:
#             # print(time_line)
#             result.append(line)
#             result = sorted(line, key=lambda x: x[1], reverse=True)
#     return result[-5:]



def parse(
        ignore_files=False,
        ignore_urls=None,
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
        ):
    lines = read_log_file()
    print(lines)
    if ignore_files:
        lines = filter_files(lines)
    if ignore_urls:
        lines = filter_urls(lines=lines, ignored_urls=ignore_urls)

    # if filter_time:
    #     lines = filter_time(lines, start_at, stop_at)
    # if request_type:
    #     lines = filter_request_type(lines)

    # print(len(lines))
    if ignore_www:
        lines = filter_www(lines)
    if slow_queries:
        lines = find_same(lines)

    # for_counter = [x['url'] for x in lines]
    # print(for_counter)
    counted_objects = Counter(lines)
    sorted_objects = sorted(counted_objects.items(), key=lambda x: x[1], reverse=True)
    print(sorted_objects)
    return [x[1] for x in sorted_objects][:5]







if __name__ == '__main__':
    print(parse())
