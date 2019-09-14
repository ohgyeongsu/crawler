import json
import requests

class youtube_crawling_api:
    def __init__(self):
        self.KEY = "" #본인의 발급받은 key를 사용하세요

    def crawling(self, word, videocount):
        self.__videos_query(word, videocount)

    def __videos_query(self, searchword, videocount):
        token = ""
        temp = []
        while videocount > 0:
            if token == "":
                videos_query = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&maxResults=50&q=" + searchword + "&regionCode=KR&hl=ko_KR&type=video&key=" + self.KEY
            else:
                videos_query = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&maxResults=50&q=" + searchword + "&pageToken=" + token + "&regionCode=KR&hl=ko_KR&type=video&key=" + self.KEY

            videos_query_response = requests.get(videos_query).json()

            videos = videos_query_response["items"]

            for video in videos:
                videoid = video["id"]["videoId"]
                videourl = "https://www.youtube.com/watch?v=" + videoid
                videoview, like, dislike, description, category, comments = self.__video_statistics(videoid)
                title = video["snippet"]["title"]
                timestamp = video["snippet"]["publishedAt"].split('.')[0]
                channelid = video["snippet"]["channelId"]
                channelurl = "https://www.youtube.com/channel/" + channelid
                subscribecount = self.__channel_statisticses(channelid)
                channeltitle = video["snippet"]["channelTitle"]

                temp.extend([{
                    'title': title,
                    'view': videoview,
                    'video_url': videourl,
                    'channel_name': channeltitle,
                    'channel_url': channelurl,
                    'channel_subscribe_count': subscribecount,
                    'uploade_date': timestamp,
                    'video_description': description,
                    'category': category,
                    'like': like,
                    'dislike': dislike,
                    'comments': comments
                }])

            try:
                token = videos_query_response["nextPageToken"]
                videocount -= 1
            except:
                break

        with open('./videos.json', 'w', encoding='utf-8') as j:
            json.dump(temp, j, ensure_ascii=False, indent='\t')


    def __video_statistics(self, videoid):
        temp = []
        video_statistics_query = "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=" + videoid + "&regionCode=KR&hl=ko_KR&key=" + self.KEY
        video_statistics_query_response = requests.get(video_statistics_query).json()
        video_statisticses = video_statistics_query_response["items"]

        for video_statistics in video_statisticses:
            description = video_statistics["snippet"]["description"]
            categoryid = video_statistics["snippet"]["categoryId"]

            video_category_query = "https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&id=" + categoryid + "&hl=ko_KR&key=" + self.KEY
            video_category_query_response = requests.get(video_category_query).json()
            video_categories = video_category_query_response["items"]
            for video_category in video_categories:
                category = video_category["snippet"]["title"]

            try:
                videoview = video_statistics["statistics"]["viewCount"]
            except:
                videoview = 0

            try:
                like = video_statistics["statistics"]["likeCount"]
            except:
                like = 0

            try:
                dislike = video_statistics["statistics"]["dislikeCount"]
            except:
                dislike = 0

        comment_token = ""
        while True:
            if comment_token == "":
                video_comments_query = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet%2Creplies&maxResults=100&order=time&textFormat=plainText&videoId=" + videoid + "&key=" + self.KEY
            else:
                video_comments_query = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet%2Creplies&maxResults=100&order=time&textFormat=plainText&videoId=" + videoid + "&pageToken=" + comment_token + "&key=" + self.KEY

            video_comments_response = requests.get(video_comments_query).json()
            comments = video_comments_response["items"]

            for comment in comments:
                commentauthor = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                text = comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
                timestamp = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                parentid = comment["id"]
                replycount = comment["snippet"]["totalReplyCount"]

                if replycount > 0:
                    reply_token = ""
                    while True:
                        if reply_token == "":
                            reply_comments_query = "https://www.googleapis.com/youtube/v3/comments?part=id%2Csnippet&maxResults=100&parentId=" + parentid + "&key=" + self.KEY
                        else:
                            reply_comments_query = "https://www.googleapis.com/youtube/v3/comments?part=id%2Csnippet&maxResults=100&parentId=" + parentid + "&pageToken=" + comment_token + "&key=" + self.KEY

                        reply_comments_response = requests.get(reply_comments_query).json()

                        replies = reply_comments_response["items"]
                        replycomment = []

                        for reply in replies:
                            reply_commentauthor = reply["snippet"]["authorDisplayName"]
                            reply_text = reply["snippet"]["textOriginal"]
                            reply_timestamp = reply["snippet"]["publishedAt"]

                            replycomment.extend([{
                                'reply_comment_writer': reply_commentauthor,
                                'reply_comment': reply_text
                            }])

                        temp.extend([{
                            'comment_writer': commentauthor,
                            'comment': text,
                            'replies': replycomment
                        }])

                        try:
                            reply_token = reply_comments_response["nextPageToken"]
                        except:
                            break

                else:
                    temp.extend([{
                        'comment_writer': commentauthor,
                        'comment': text,
                }])

            try:
                comment_token = video_comments_response["nextPageToken"]
            except:
                break

        return videoview, like, dislike, description, category, temp

    def __channel_statisticses(self, channelid):
        channel_statistics_query = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=" + channelid + "&hl=ko_KR&key=" + self.KEY
        channel_statistics_query_response = requests.get(channel_statistics_query).json()
        channel_statisticses = channel_statistics_query_response["items"]
        for channel_statistics in channel_statisticses:
            try:
                subscribecount = channel_statistics["statistics"]["subscriberCount"]
            except:
                subscribecount = 0

        return subscribecount