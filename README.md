# crawler

트위터 키워드 기반 크롤링 검색 코드입니다.

기존의 오픈소스 크롤링이 성능이 떨어져서 기존꺼 바탕으로 새롭게 만들었습니다.

selenium의 webdriver를 사용한 동적 크롤링으로 크롬드라이버를 사용했습니다.

동적 크롤링에 더해서 사용자가 설정한 Poolsize값에 따라서 병렬로 크롤링하도록 구현했습니다.

크롬 드라이버는 현재 githup에 올린 버전을 사용했습니다.

구현 환경은 Anaconda3 5.1.0 64-bit에서 가상환경을 만들어서 Python 3.6.8 버전으로 진행했습니다.

추후에 만들어놓았던 YouTube 댓글 크롤링도 병렬과정을 추가해서 올릴 예정입니다.

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

추후에 문제나 추가할 기능을 커밋하겠습니다.


## 4. 참고

https://github.com/taspinar/twitterscraper.git

https://github.com/e9t/nsmc.git
