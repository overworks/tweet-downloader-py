#!usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import json
import webbrowser
import requests
import tweepy
from six.moves import input


class ArgumentError(ValueError):
    """인수가 잘못되었을때 사용법을 표시하기 위한 예외"""
    pass


def get_auth():

    # 컨슈머 키와 시크릿은 공개되면 안되므로 별도의 파일에 집어넣음
    from credential import CONSUMER_KEY, CONSUMER_SECRET
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, 'oob')

    token = {}
    if os.path.exists('token.json'):
        with open('token.json', 'r') as f:
            token = json.load(f)

    access_token = token.get('access_token')
    access_token_secret = token.get('access_token_secret')

    if access_token != None and access_token_secret != None:
        auth.set_access_token(access_token, access_token_secret)
    else:
        redirect_url = auth.get_authorization_url()
        webbrowser.open(redirect_url)
        verifier = input('Input PIN: ')
        access_token, access_token_secret = auth.get_access_token(verifier)

        token['access_token'] = access_token
        token['access_token_secret'] = access_token_secret

        with open('token.json', 'w') as f:
            json.dump(token, f)

    return auth


def display_usage():
    print('사용법: tweet_downloader [옵션] [인수] 검색어')
    print()
    print('옵션 -')
    print('\t-dir [PATH]: 저장할 디렉토리')
    print('\t-item [NUMBER]: 검색할 트윗 갯수')
    print('\t-rt [NUMBER]: [NUMBER] 이상 리트윗된 것만 다운로드')


def check_status(status, rt):
    """다운로드 대상 오브젝트인지 체크"""

    if rt <= status.retweet_count:
        if 'media' in status.entities:
            return True

    return False


def download_media(status, directory):
    """트윗에서 미디어를 다운로드하고 다운로드한 파일의 갯수를 돌려줌"""

    if directory is None:
        directory = os.path.curdir

    if os.path.exists(directory) is False:
        os.mkdir(directory)

    download_count = 0
    for media in status.entities['media']:
        url = media['media_url_https']
        filename = os.path.basename(url)
        file_path = os.path.join(directory, filename)

        if os.path.exists(file_path) is False:
            print('downloading file {0} from {1} (RT count: {2})'.format(filename, status.text, status.retweet_count))
            r = requests.get(url, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=512):
                    f.write(chunk)
            download_count += 1

    return download_count


def main(query, rt, item_count, directory):
    """메인 함수"""

    try:
        auth = get_auth()
        api = tweepy.API(auth)

        count = 0
        for status in tweepy.Cursor(api.search, q=query).items(item_count):
            if check_status(status, rt):
                count += download_media(status, directory)

    except tweepy.TweepError as e:
        print(e.reason)


def parse_args():
    num_args = len(sys.argv)
    if num_args < 2:
        raise ArgumentError()

    argi = 1
    retweet_count = 0
    item = 500
    d = None
    try:
        while argi < num_args - 1:
            option = sys.argv[argi]
            if option == '-rt':
                argi += 1
                retweet_count = int(sys.argv[argi])
            elif option == '-dir':
                argi += 1
                d = sys.argv[argi]
            elif option == '-item':
                argi += 1
                item = int(sys.argv[argi])

            argi += 1

    except:
        raise ArgumentError()

    query = sys.argv[argi]
    return query, retweet_count, item, d


if __name__ == '__main__':
    try:
        q, retweet_count, item, d = parse_args()
        main(q, retweet_count, item, d)

    except ArgumentError:
        display_usage()
