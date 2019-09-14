# Twitter Crawler

트위터 키워드 기반 크롤링 검색 코드입니다.

기존의 오픈소스 크롤링이 성능이 떨어져서 기존꺼 바탕으로 새롭게 만들었습니다.

selenium의 webdriver를 사용한 동적 크롤링으로 크롬드라이버를 사용했습니다.

동적 크롤링에 더해서 사용자가 설정한 Poolsize값에 따라서 병렬로 크롤링하도록 구현했습니다.

크롬 드라이버는 현재 githup에 올린 버전을 사용했습니다.

구현 환경은 Windows10, Anaconda3 5.1.0 64-bit에서 가상환경을 만들어서 Python 3.6.8 버전으로 진행했습니다.

# 사용방법

## 1. 사전작업

이미 파이썬 환경이 있으시면 크롬드라이버와 crawl_tweet.py 파일을 같은 위치에 다운받으신 후 새로운 python파일에 아래 코드를 입력합니다.

## 2. 코드

```python

import datetime as dt
import crawl_tweet

if __name__ == '__main__':
    tc = crawl_tweet.twitter_crawling()
    # tc.search_query(크롤링할 키워드, 검색시작할날짜, 검색끝나는날짜, poolsize)
    tc.search_query("갤럭시S9", dt.date(2018, 10, 1), dt.date(2018, 12, 31), 3)
    
```

## 3. 설명

키워드에는 예제 코드에서 보이듯 원하는 단어를 입력하시면 됩니다.

트위터에서 제공하는 검색 방법인 -,OR 등도 키워드에 입력가능합니다.

날짜는 시작날짜가 끝나는 날짜보다 늦은 날짜면 코드가 종료됩니다.

poolsize는 병렬로 몇개를 돌릴 것이냐인데 쉽게 말하면 동적 크롤링할때 크롬 창이 poolsize크기만큼 켜져서 크롤링을 합니다.

poolsize보다 날짜간의 일수가 작으면 poolsize는 일수로 설정됩니다.

여러번 테스트해본 결과 전체 일수에서 1~3일 간격으로 나눠도 poolsize를 설정하면 속도는 빠를지언정 데이터를 많이 가져오지 못하는 상활이어서 적절하게 나눠야 할 것입니다.

실행하면 실행한 python파일과 같은 위치에 **키워드(시작날짜~끝날짜).json** 으로 크롤링한 데이터를 json으로 만들어줍니다.


## 4. 참고

https://github.com/taspinar/twitterscraper.git

https://github.com/e9t/nsmc.git






# YouTube Crawler

유튜브 키워드 기반 크롤링 검색 코드입니다.

키워드 관련 동영상과 그 동영상에 대한 댓글을 가능한 수집합니다.

selenium의 webdriver를 사용한 크롤링으로 크롬드라이버를 사용했습니다.

병렬 크롤링을 하려했으나 트랙픽이 과도하게 들어가면 구글에서 reCAPTCHA이 작동해서 추가하지 않았습니다.

그렇지만 계속해서 크롤러를 실행할 경우에도 reCAPTCHA 작동하므로 주의깊게 돌리시길 바랍니다.

크롬 드라이버는 현재 githup에 올린 버전을 사용했습니다.

구현 환경은 위의 트위터 크롤러 환경과 같습니다.

유튜브 api를 사용한 크롤링 코드는 youtube_api.py입니다. api를 사용하기 때문에 할당량 이상 요청하게되면 요청이 중단되어 오류가 발생합니다.

# 사용방법

## 1. 사전작업

이미 파이썬 환경이 있으시면 크롬드라이버와 crawl_youtube.py 파일을 같은 위치에 다운받으신 후 새로운 python파일에 아래 코드를 입력합니다.

api를 사용해서 크롤링 하실려면 youtube_api.py의 파일을 다운받아서 KEY값을 개인 발급 KEY로 수정하세요

## 2. 코드

```python

import crawl_youtube

if __name__ == '__main__':
    test = crawl_youtube.youtube_crawling()
    #test.video_hard_information("크롤링할 키워드")
    test.video_hard_information("갤럭시 S9")
    
```

```python

import youtube_api

if __name__ == '__main__':
    test = youtube_api.youtube_crawling_api()
    #test.crawling("크롤링할 키워드", 크롤링할 동영상 수)
    test.crawling("갤럭시 S9", 30)
    
```

## 3. 설명

키워드에는 예제 코드에서 보이듯 원하는 단어를 입력하시면 됩니다.

여러번 테스트해본 결과 selenium에서 maxretryerror이 몇몇 동영상에서 간헐적으로 발생하기 때문에 크롤링시에 이를 기억하고 모든 동영상을 한번씩 확인했으면 문제가 발생한 동영상을 다시 크롤링합니다.

하지만 그것은 완전한 해결방안이 아니기 때문에 특정동영상에서 위의 에러가 계속해서 발생하면 문제가 발생하는 동영상의 크롤링을 포기하거나 성공할 때까지 실행하는 것이 현재 해결방안압니다.

크롤링하는 동영상 채널에 구독자수를 비공개하거나 동영상의 조회수, 좋아요, 싫어요가 없고 댓글 금지 동영상의 경우는 0 또는 None, [] 등으로 값을 리턴합니다.

실행하면 실행한 python파일과 같은 위치에 **키워드** 폴더가 생성되고 그 폴더안에 **동영상타이틀_video.json** 으로 json파일을 생성합니다.

api를 사용해서 크롤링하는 방식은 키워드 관련 동영상 리스트와 댓글, 답글을 가능한 최대한 가져오는 방식이기때문에 10개 이상의 동영상을 수집하려면 많은 할당량이 들어가니 주의하시기 바랍니다.

추후에 문제나 추가할 기능을 커밋하겠습니다.

## 4. 참고

https://developers.google.com/youtube/v3/?hl=ko
