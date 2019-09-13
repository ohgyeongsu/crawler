import re
import os
import time
import json
import datetime as dt
import requests
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class youtube_crawling:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument("--mute-audio")
        self.options.add_argument('--headless')
        self.options.add_argument('lang=ko_KR')

    def __driverget(self, url):
        driver = webdriver.Chrome('./chromedriver', chrome_options=self.options)
        driver.get(url)
        time.sleep(random.randrange(3, 5))
        return driver

    def __scroll(self, driver):  # 스크롤을 아래로 내리기 위한 메소드
        last_height = driver.execute_script("return document.documentElement.scrollHeight")  # 처음 웹의 높이
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")  # 스크롤을 현재 웹의 맨 아래로 내
            time.sleep(random.randrange(3, 6))  # 입력한 시간 만큼 대기
            new_height = driver.execute_script("return document.documentElement.scrollHeight")  # 내린 후에 업데이트 된 웹의 높이
            if new_height == last_height:
                break

            last_height = new_height  # 처음 높이 값을 새로운 값으로 업데이트

    def __button(self, driver, xpath):
        driver.find_element_by_xpath(xpath).click()
        time.sleep(random.randrange(3, 5))

    def __findhangul(self, sentence):
        hangul = re.compile('[ㄱ-ㅣ가-힣]+')
        hangul_list = hangul.findall(sentence)
        return hangul_list

    def __checkfilename(self, name):
        filename = re.sub('[\\\/:*?"<>|]+','',name)
        return filename

    # db저장을 오류방지 위한 파싱
    def __replace(self, sentence):
        character = re.compile('[ㄱ-ㅣ가-힣a-zA-Z0-9\s`~!@#$%^&*()-=_+{}\[\],./<>?;\'":|\\\]+')

        sentence_replace = sentence.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
        character_list = character.findall(sentence_replace.strip())
        content = ''.join(character_list)
        return content

    def __video_simple_information(self, word):
        hangul_video = []
        url_driver = self.__driverget('https://www.youtube.com/results?search_query=' + word)  # 입력 받은 검색어로 유튜브 검색
        self.__scroll(url_driver)

        video_html = BeautifulSoup(url_driver.page_source, 'html.parser')  # 스크롤로 인해서 업데이트된 웹을 html로 파싱

        url_driver.quit()

        video_list = video_html.find_all('ytd-video-renderer',
                                         {'class': 'style-scope ytd-item-section-renderer'})  # 모든 동영상에 대한 정보 태그를 다 가져옴

        for video in video_list:
            video_title = video.select_one('#dismissable > div > div > div > h3 > a').text

            if not self.__findhangul(video_title):
                continue

            try:
                video_view = int(
                    video.select_one('#dismissable > div > div > div > h3 > a')['aria-label'].split('조회수 ')[1][:-1].replace(',', ''))
            except:
                video_view = 0

            video_url = 'https://www.youtube.com' + \
                        video.select_one('#dismissable > div > div > div > h3 > a')['href']

            channel_name = video.select_one(
                'div#dismissable > div > div > ytd-video-meta-block > #metadata > #byline-container > ytd-channel-name > #container > #text-container > yt-formatted-string > a').text
            channel_url = 'https://www.youtube.com' + video.select_one(
                'div#dismissable > div > div > ytd-video-meta-block > #metadata > #byline-container > ytd-channel-name > #container > #text-container > yt-formatted-string > a')['href']

            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            }
            try:
                channel_subscribe_count = int(
                    requests.get(channel_url, headers=header).text.split('subscriberCountText":{"runs":[{"text":"구독자 ')[
                        1].split('명')[0].replace(',', ''))
            except:
                channel_subscribe_count = None

            hangul_video.extend([{
                'title': self.__replace(video_title),
                'view': video_view,
                'video_url': video_url,
                'channel_name': self.__replace(channel_name),
                'channel_url': channel_url,
                'channel_subscribe_count': channel_subscribe_count
            }])

        print("Get videos: {}개".format(len(hangul_video)))

        if not os.path.isdir('./'+word):
            os.mkdir('./'+word)

        return hangul_video

    def video_hard_information(self, word):
        video_list = self.__video_simple_information(word)
        check = self.__video_information(video_list, word)
        check_video_list = []
        while len(check) != 0:
            for index in check:
                check_video_list.append(video_list[index])
            check = self.__video_information(check_video_list, word)
        print(word + '크롤링 완료')

    def __video_information(self, video_list, word):
        error_page = []
        for idx in range(len(video_list)):
            print("[동영상 크롤링 시작]")
            if os.path.isfile('./'+ word + '/' +self.__checkfilename(video_list[idx]['title'])+ '_video.json'):
                print(video_list[idx]['title']+'은 이미 크롤링한 동영상입니다.')
                continue
            html = self.__video_html_information(video_list[idx]['video_url'])
            if html == None:
                print("동영상 페이지의 html을 가져오는데 실패했습니다. Error리스트에 해당 video 추가")
                error_page.append(idx)
                continue

            date, content, category = self.__immutabilityvideoinformation(html)
            like, dislike = self.__variabilityvideoinformation(html)
            comment_count, comments = self.__getcomment(html)

            video_information = []

            video_information.extend([{
                'title': video_list[idx]['title'],
                'view': video_list[idx]['view'],
                'video_url': video_list[idx]['video_url'],
                'channel_name': video_list[idx]['channel_name'],
                'channel_url': video_list[idx]['channel_url'],
                'channel_subscribe_count': video_list[idx]['channel_subscribe_count'],
                'upload_date': str(date),
                'video_description': content,
                'category': category,
                'like': like,
                'dislike': dislike,
                'comment_count': comment_count,
                'comments': comments
            }])

            with open('./' + word + '/' + self.__checkfilename(video_list[idx]['title']) + '_video.json', 'w', encoding='utf-8') as j:
                json.dump(video_information, j, ensure_ascii=False, indent='\t')
            print("[동영상 크롤링 완료]" + self.__checkfilename(video_list[idx]['title']) + '_video.json' + "[JSON파일 생성]")

        return error_page

    def __video_html_information(self, video_url):
        video_driver = self.__driverget(video_url)  # 동영상 링크 입력받아 동적으로 웹에 실행
        video_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        time.sleep(random.randrange(3, 5))

        try:
            try:
                self.__button(video_driver, "//*[@id='label']")
                self.__button(video_driver, "//*[@id='menu']/a[2]")  # 댓글 최근날짜순으로 정렬위한 클릭
            except:
                print('댓글을 달 수 없는 동영상입니다. comment return []')

            try:
                self.__button(video_driver, "//*[@id='more']/yt-formatted-string")
            except:
                pass

        except Exception as e:
            print(e, '알 수 없는 문제 발생 추후 수정')
            print(video_url)
            video_driver.quit()
            return None

        self.__scroll(video_driver)

        try:
            video_html = BeautifulSoup(video_driver.page_source, 'html.parser')
        except:
            print("Maxretryerror 발생")
            return None

        video_driver.quit()
        return video_html

    def __immutabilityvideoinformation(self, video_html):
        upload_date = video_html.find('span', {'class': 'date style-scope ytd-video-secondary-info-renderer'}).text
        y, m, d = upload_date.split(':')[1][:-1].split('.')
        upload_date_format = dt.datetime.strptime(y.strip() + '-' + m.strip() + '-' + d.strip(), "%Y-%m-%d").date()

        video_content_text = video_html.find('yt-formatted-string', {
            'class': 'content style-scope ytd-video-secondary-info-renderer'}).text
        video_content = self.__replace(video_content_text)

        find_category = video_html.find('div', {'id': 'collapsible'})
        category = find_category.find_all('ytd-metadata-row-renderer', {
            'class': 'style-scope ytd-metadata-row-container-renderer'})

        video_category = ''
        for idx in category:
            if idx.select_one('#collapsible > ytd-metadata-row-renderer > h4 > yt-formatted-string').text == "카테고리":
                video_category = idx.select_one(
                    '#collapsible > ytd-metadata-row-renderer > div > yt-formatted-string > a').text
                break

        return upload_date_format, self.__replace(video_content), self.__replace(video_category)

    def __variabilityvideoinformation(self, video_html):
        like_or_dislike = video_html.find_all('yt-formatted-string',
                                              {'class': 'style-scope ytd-toggle-button-renderer style-text'})
        try:
            like = int(like_or_dislike[0]['aria-label'].split(' ')[1][:-1].replace(',', ''))
        except:
            print('좋아요가 없습니다. like return 0')
            like = None

        try:
            dislike = int(like_or_dislike[1]['aria-label'].split(' ')[1][:-1].replace(',', ''))
        except:
            print('싫어요가 없습니다. dislike return 0')
            dislike = None

        return like, dislike

    def __getcomment(self, video_html):
        comments = []

        try:
            video_comment_text = video_html.find_all('yt-formatted-string',
                                                     {'id': 'content-text'})  # 한 동영상에 대한 모든 댓글 태그 가져옴
            video_comment_writer = video_html.find_all('a',
                                                       {'id': 'author-text'})
        except:
            return len(comments), comments


        for i in range(len(video_comment_text)):
            comment = self.__replace(video_comment_text[i].text)
            if not self.__findhangul(comment):
                continue

            comments.extend([{
                'comment_writer': video_comment_writer[i].text.strip(),
                'comment': comment
            }])

        comment_count = len(comments)
        return comment_count, comments