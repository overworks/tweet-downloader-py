# -*- coding: utf-8 -*-

import sys
import os.path
import json
import webbrowser
import requests
import tweepy
from six.moves import input


class ArgumentError(ValueError):
    """ 인수가 잘못되었을때 사용법을 표시하기 위한 예외 """
    pass


class Argument():
    """ 스크립트 인수처리용 클래스 """
    query = ''
    path = os.path.curdir
    silence = False
    retweet_count = 0
    item_count = 500
    screen_name = ''


def get_auth():
    """ OAuthHandler 구성 """

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
        pin = input('Input PIN: ')
        access_token, access_token_secret = auth.get_access_token(pin)

        token['access_token'] = access_token
        token['access_token_secret'] = access_token_secret

        with open('token.json', 'w') as f:
            json.dump(token, f)

    return auth


def display_usage():
    """사용법 출력. 영어로 쓰고 싶은데 영어 몰라요우... 누가 번역좀..."""

    print('사용법: tweet_downloader [옵션] [인수] 검색어')
    print()
    print('옵션:')
    print('\t-d, --directory [PATH]          : 저장할 디렉토리')
    print('\t-i, --item [COUNT]              : 검색할 트윗 갯수')
    print('\t-rt, --retweet [NUMBER]         : [NUMBER] 이상 리트윗된 것만 다운로드')
    print('\t-s, --silence                   : 메시지를 표시하지 않음')
    print('\t-sn, --screen_name [SCREEN_NAME]: 트위터 유저 [SCREEN_NAME]의 트윗 내에서 검색')


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

    if not silence:
        print('downloading tweet media - id:{0}, rt count:{1}, text:{2}'.format(status.id, status.retweet_count, status.text))

    download_count = 0
    media_index = 1
    for media in status.entities['media']:
        url = media['media_url_https']
        extension = os.path.splitext(url)[1]
        filename = '{0}-{1}{2}'.format(status.id, media_index, extension)
        filepath = os.path.join(directory, filename)

        if not os.path.exists(filepath):
            if not silence:
                print('\tsaving {0} to {1}'.format(url, filepath))

            r = requests.get(url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=512):
                    f.write(chunk)
            download_count += 1
        else:
            if not silence:
                print('\t{0} already exists'.format(filepath))
        
        media_index += 1

    return download_count


def main(args):
    """메인 함수"""

    try:
        auth = get_auth()
        api = tweepy.API(auth)

        query = args.query
        if args.screen_name:
            query = 'from:{0} {1}'.format(args.screen_name, query)

        downloaded_tweet_list = []
        count = 0
        for status in tweepy.Cursor(api.search, q=query).items(args.item_count):
            if check_status(status, args.retweet_count):
                source_id = status.entities['media'][0]['source_status_id']
                if source_id not in downloaded_tweet_list:
                    source_status = api.get_status(id=source_id)
                    count += download_media(source_status, args.path, args.silence)
                    downloaded_tweet_list.append(source_id)

    except tweepy.TweepError as e:
        print(e.reason)


def parse_args():
    """인수 파싱"""

    num_args = len(sys.argv)
    if num_args < 2:
        raise ArgumentError()

    args = Argument()
    argi = 1
    try:
        while argi < num_args - 1:
            option = sys.argv[argi]
            if option == '-rt' or option == '--retweet':
                argi += 1
                args.retweet_count = int(sys.argv[argi])
            elif option == '-d' or option == '--directory':
                argi += 1
                args.path = sys.argv[argi]
            elif option == '-i' or option == '--item':
                argi += 1
                args.item_count = int(sys.argv[argi])
            elif option == '-s' or option == '--silence':
                args.silence = True
            elif option == '-sn' or option == '--screen_name':
                argi += 1
                args.screen_name = sys.argv[argi]
            else:
                raise ArgumentError()

            argi += 1
    except:
        raise ArgumentError()

    args.query = sys.argv[argi]
    return args

if __name__ == '__main__':
    try:
        args = parse_args()
        main(args)

    except ArgumentError:
        display_usage()
