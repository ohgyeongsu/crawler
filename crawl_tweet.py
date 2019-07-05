#-*- coding: utf-8 -*-
import time
import json
import datetime as dt
from bs4 import BeautifulSoup
from selenium import webdriver
from multiprocessing import Pool

class twitter_crawling:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('lang=ko_KR')
        self.options.add_argument('--window-size=1920,1080')

    def search_query(self, keyword, since, until, poolsize):
        if '#' in keyword:
            keyword = keyword.replace('#', '%23')

        num = (until - since).days

        if num < 0:
            print('시작일과 종료일을 제대로 설정해주세요')
            exit()

        if (num // poolsize) == 0:
            poolsize = num

        datelist = [since + dt.timedelta(days=day) for day in self.__linspace(0, num, poolsize + 1)]

        new_since = datelist[1:-1]
        for i in range(len(new_since)):
            new_since[i] = new_since[i]+dt.timedelta(days=1)
        new_since = [datelist[0]]+ new_since

        urls = ["https://twitter.com/search?l=ko&src=typd&q={}%20since%3A{}%20until%3A{}&lang=ko".format(keyword, bd, ed) for bd, ed in zip(new_since, datelist[1:])]

        all_tweets = []

        try:
            pool = Pool(poolsize)
            for tweets in pool.map(self.crawltweets, urls):
                tweets = BeautifulSoup(tweets, 'html.parser').find_all('li',{'class': 'js-stream-item stream-item stream-item'})
                all_tweets.extend(list(filter(None, [self.__parse_tweet(tweet) for tweet in tweets])))
        finally:
            pool.close()
            pool.join()

        self.__tweetspreprocessing(all_tweets, keyword, since, until)

    def crawltweets(self, url):
        twitter = self.__driverget(url)
        self.__scroll(twitter)
        tweet_html = twitter.page_source
        twitter.quit()
        return tweet_html

    def __tweetspreprocessing(self, tweets, keyword, since, until): #중복 트윗 제거
        tweet_dup_check = []
        for tweet in tweets:
            tweet_dup_check.append(tweet['tweet'])
        tweet_no_dup = list(set(tweet_dup_check))

        with open('./' + keyword + '(' + str(since) + '~' + str(until) + ').json', 'w', encoding='utf-8') as j:
            index = []

            for no_dup in tweet_no_dup:
                check = False
                for num in range(len(tweets)):
                    if no_dup == tweets[num]['tweet'] and check == False:
                        check = True
                    elif no_dup == tweets[num]['tweet'] and check == True:
                        index.append(num)
                    else:
                        continue

            index.sort(reverse=True)

            for dup_num in index:
                tweets.pop(dup_num)
            json.dump(tweets, j, ensure_ascii=False, indent='\t')

    def __parse_tweet(self, tweet):
        hangul_timestamp = tweet.select_one('div > div > div.stream-item-header > small > a')['title'].split(' ')
        h, m = hangul_timestamp[1].split(':')
        year = hangul_timestamp[3][:-1]
        month = hangul_timestamp[4][:-1]
        day = hangul_timestamp[5][:-1]
        datetimestr = year + '-' + month + '-' + day + ' ' + h + ':' + m

        if hangul_timestamp[0] == '오전' or (hangul_timestamp[0] == '오후' and int(h) == 12):
            timestamp = dt.datetime.strptime(datetimestr, '%Y-%m-%d %H:%M')
        else:
            timestamp = dt.datetime.strptime(datetimestr, '%Y-%m-%d %H:%M').replace(hour=int(h)+12)

        try:
            return {'fullname': tweet.select_one('div > div > div.stream-item-header > a > span.FullNameGroup > strong').text.strip(),
                    'username': tweet.select_one('div > div > div.stream-item-header > a > span.username').text,
                    'timestamp': str(timestamp)[:-3],
                    'tweet': tweet.select_one('div > div > div.js-tweet-text-container > p').text.replace('\n',' ').replace('…','').strip()
                    } # 나중에 이미지나 동영상 추가

        except Exception as e:
            print(e, '문제 발생 추후 수정')
            return None

    def __driverget(self, url):
        driver = webdriver.Chrome('./chromedriver', chrome_options=self.options)
        driver.get(url)
        time.sleep(3)
        return driver

    def __scroll(self, driver):  # 스크롤을 아래로 내리기 위한 메소드
        last_height = driver.execute_script("return document.documentElement.scrollHeight")  # 처음 웹의 높이
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")  # 스크롤을 현재 웹의 맨 아래로 내
            time.sleep(3)  # 입력한 시간 만큼 대기
            new_height = driver.execute_script("return document.documentElement.scrollHeight")  # 내린 후에 업데이트 된 웹의 높이
            if new_height == last_height:
                break
            last_height = new_height  # 처음 높이 값을 새로운 값으로 업데이트

    def __linspace(self, start, stop, n):
        if n == 1:
            yield stop
            return
        h = (stop - start) / (n - 1)
        for i in range(n):
            yield start + h * i

# if __name__ == '__main__':
#     tc = twitter_crawling()
#     tc.search_query("갤럭시S9", dt.date(2018, 10, 1), dt.date(2018, 12, 31), 3)