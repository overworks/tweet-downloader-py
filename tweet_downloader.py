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
    """사용법 출력. 영어로 쓰고 싶은데 영어 몰라요우... 누가 번역좀..."""

    print('사용법: tweet_downloader [옵션] [인수] 검색어')
    print()
    print('옵션 -')
    print('\t-d, --directory [PATH]: 저장할 디렉토리')
    print('\t-i, --item [COUNT]: 검색할 트윗 갯수')
    print('\t-r, --retweet [NUMBER]: [NUMBER] 이상 리트윗된 것만 다운로드')
    print('\t-s, --silence: 메시지를 표시하지 않음')


def check_status(status, retweet_count):
    """다운로드 대상 오브젝트인지 체크"""

    if retweet_count <= status.retweet_count:
        if 'media' in status.entities:
            return True

    return False


def download_media(status, directory, silence):
    """트윗에서 미디어를 다운로드하고 다운로드한 파일의 갯수를 돌려줌"""

    if not directory:
        directory = os.path.curdir

    if not os.path.exists(directory):
        os.mkdir(directory)

    download_count = 0
    for media in status.entities['media']:
        url = media['media_url_https']
        filename = os.path.basename(url)
        file_path = os.path.join(directory, filename)

        if not os.path.exists(file_path):
            if not silence:
                print('downloading file {0} from {1} (RT count: {2})'.format(filename, status.text, status.retweet_count))
            r = requests.get(url, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=512):
                    f.write(chunk)
            download_count += 1

    return download_count


def main(args):
    """메인 함수"""

    try:
        auth = get_auth()
        api = tweepy.API(auth)

        query = args[0]
        retweet_count = args[1]
        item_count = args[2]
        directory = args[3]
        silence = args[4]

        count = 0
        for status in tweepy.Cursor(api.search, q=query).items(item_count):
            if check_status(status, retweet_count):
                count += download_media(status, directory, silence)

    except tweepy.TweepError as e:
        print(e.reason)


def parse_args():
    """인수 파싱"""

    num_args = len(sys.argv)
    if num_args < 2:
        raise ArgumentError()

    argi = 1
    retweet_count = 0
    item = 500
    directory = os.path.curdir
    silence = False
    try:
        while argi < num_args - 1:
            option = sys.argv[argi]
            if option == '-r' or option == '--retweet':
                argi += 1
                retweet_count = int(sys.argv[argi])
            elif option == '-d' or option == '--directory':
                argi += 1
                directory = sys.argv[argi]
            elif option == '-i' or option == '--item':
                argi += 1
                item = int(sys.argv[argi])
            elif option == '-s' or option == '--silence':
                silence = True

            argi += 1

    except:
        raise ArgumentError()

    query = sys.argv[argi]
    return (query, retweet_count, item, directory, silence)

if __name__ == '__main__':
    try:
        args = parse_args()
        main(args)

    except ArgumentError:
        display_usage()
