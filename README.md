# tweet-downloader-py

## 설명

키워드로 검색해서 나온 결과 트윗에 첨부된 이미지를 다운로드 받는 파이썬 스크립트입니다.

## 사용방법

1. [파이썬 홈페이지](https://www.python.org/)에서 파이썬을 받아서 설치합니다.
2. 명령 프롬프트를 연 후 다음 명령어로 종속성 추가. `pip install -r requirements.txt`
3. crendential.py 파일을 연 후, [이 곳](https://gist.github.com/shobotch/5160017)을 참조하여 type이 PIN으로 되어있는 앱의 Consumer key와 Consumer secret을 입력 후 저장.
4. 다음 명령어로 파이썬 스크립트 실행. `python tweet_downloader.py [OPTION] [ARGUMENT] 검색어`
5. 기존에 액세스 토큰을 받은 적이 없다면 브라우저 창이 열리면서 인증을 요구하는 창이 열립니다. 여기서 허가를 선택 후 나오는 8자리의 PIN을 입력합니다.
6. 해당 디렉토리에 파일이 다운로드됩니다.

## 옵션

- -r, --retweet [NUMBER] : [NUMBER]회 이상 리트윗된 트윗 미디어만 다운로드합니다.
- -d, --dir [PATH] : 다운로드한 미디어를 [PATH] 디렉토리 안에 저장합니다.
- -i, --item [COUNT] : [COUNT]개의 트윗 내에서 검색합니다. 기본은 500개입니다.
- -s, --silence : 화면에 다운로드 메시지를 출력하지 않습니다.

## 예시

`python tweet_downloader.py --retweet 150 --directory arifumi ありふみ`

## 기타

- python3에서 테스트하였습니다. python2의 경우에는 유니코드 출력문제로 제대로 처리되지 않을 수 있습니다. 만약 출력도중에 스크립트가 멈춘다면 --silence 옵션을 사용해보세요.
- 트윗에 여러개의 그림이 첨부되어 있거나 동영상이 첨부되어 있는 경우에도 하나의 그림 파일만 다운로드됩니다. 이것은 search API에서 보여주는 정보를 바로 사용하고 있기 때문입니다. 차후에 수정할 예정입니다.
- 그 외에 많은 문제가 존재할 수 있습니다. 버그나 문의사항에 관해서는 트위터 [@lostland](https://twitter.com/lostland)로 연락바랍니다.
- 신데렐라 걸즈 최고 커플링은 아리후미이며, 이것은 과학으로도 증명할 수 있습니다.