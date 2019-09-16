import json
import requests

class youtube_crawling_api:
    def __init__(self):
        self.KEY = "" #본인의 발급받은 key를 사용하세요

    def __request(self, query):
        response = requests.get(query).json()
        return response

    def __video_list(self, word, videocount):
        token = ""
        video_list = []
        while videocount > 0:
            video_list_query = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&maxResults=50&q=" + word + "&pageToken=" + token + "&regionCode=KR&hl=ko_KR&type=video&key=" + self.KEY
            video_list_response = self.__request(video_list_query)

            if len(video_list_response["items"]) > videocount:
                video_list.extend(video_list_response["items"][:videocount])
                return video_list

            elif len(video_list_response["items"]) == videocount:
                video_list.extend(video_list_response["items"])
                return video_list

            else:
                videocount -= len(video_list_response["items"])
                video_list.extend(video_list_response["items"])

                try:
                    token = video_list_response["nextPageToken"]
                except:
                    return video_list

    def __video_details_information(self, video_id):
        video_details_query = "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=" + video_id + "&regionCode=KR&hl=ko_KR&key=" + self.KEY

        video_details_response = self.__request(video_details_query)

        for details_information in video_details_response["items"]:
            description = details_information["snippet"]["description"]

            category_id = details_information["snippet"]["categoryId"]
            category = self.__video_category_information(category_id)

            try:
                view_count = details_information["statistics"]["viewCount"]
            except:
                view_count = 0

            try:
                like_count = details_information["statistics"]["likeCount"]
            except:
                like_count = 0

            try:
                dislike_count = details_information["statistics"]["dislikeCount"]
            except:
                dislike_count = 0

            return description, category, view_count, like_count, dislike_count

    def __video_category_information(self, category_id):
        video_category_query = "https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&id=" + category_id + "&hl=ko_KR&key=" + self.KEY

        video_category_response = self.__request(video_category_query)

        for category_information in video_category_response["items"]:
            category = category_information["snippet"]["title"]
            return category

    def __video_comment(self, video_id, comment_count):
        token = ""
        comment_list = []
        while comment_count > 0:
            video_comment_query = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet%2Creplies&maxResults=100&order=time&textFormat=plainText&videoId=" + video_id + "&pageToken=" + token + "&key=" + self.KEY
            video_comment_response = self.__request(video_comment_query)

            if len(video_comment_response["items"]) > comment_count:
                comment_list.extend(video_comment_response["items"][:comment_count])
                return comment_list

            elif len(video_comment_response["items"]) == comment_count:
                comment_list.extend(video_comment_response["items"])
                return comment_list

            else:
                comment_count -= len(video_comment_response["items"])
                comment_list.extend(video_comment_response["items"])

                try:
                    token = video_comment_response["nextPageToken"]
                except:
                    return comment_list

    def __comment_information(self, comment_list, reply_count):
        comments = []
        for comment in comment_list:
            comment_author = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
            text = comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            timestamp = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            parent_id = comment["id"]

            if comment["snippet"]["totalReplyCount"] > 0:
                reply_comment_list = self.__reply_comment(parent_id, reply_count)
                reply_comments = self.__reply_comment_information(reply_comment_list)
                comments.extend([{
                    'comment_writer': comment_author,
                    'comment': text,
                    'replies': reply_comments
                }])

            else:
                comments.extend([{
                    'comment_writer': comment_author,
                    'comment': text,
                }])

        return comments

    def __reply_comment(self, parent_id, reply_count):
        token = ""
        reply_comment_list = []
        while reply_count > 0:
            reply_comment_query = "https://www.googleapis.com/youtube/v3/comments?part=id%2Csnippet&maxResults=100&parentId=" + parent_id + "&pageToken=" + token + "&key=" + self.KEY
            reply_comment_response = self.__request(reply_comment_query)

            if len(reply_comment_response["items"]) > reply_count:
                reply_comment_list.extend(reply_comment_response["items"][:reply_count])
                return reply_comment_list

            elif len(reply_comment_response["items"]) == reply_count:
                reply_comment_list.extend(reply_comment_response["items"])
                return reply_comment_list

            else:
                reply_count -= len(reply_comment_response["items"])
                reply_comment_list.extend(reply_comment_response["items"])

                try:
                    token = reply_comment_response["nextPageToken"]
                except:
                    return reply_comment_list

    def __reply_comment_information(self, reply_comment_list):
        replies = []
        for reply in reply_comment_list:
            reply_comment_author = reply["snippet"]["authorDisplayName"]
            reply_text = reply["snippet"]["textOriginal"]
            reply_timestamp = reply["snippet"]["publishedAt"]

            replies.extend([{
                'reply_comment_writer': reply_comment_author,
                'reply_comment': reply_text
            }])

        return replies

    def __channel_subscribe_information(self, channel_id):
        channel_subscribe_query = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=" + channel_id + "&hl=ko_KR&key=" + self.KEY

        channel_subscribe_response = self.__request(channel_subscribe_query)

        for subscribe_information in channel_subscribe_response["items"]:
            try:
                subscribecount = subscribe_information["statistics"]["subscriberCount"]
            except:
                subscribecount = 0

        return subscribecount

    def __video_information(self, video_list, comment_count, reply_count):
        temp = []

        for video in video_list:
            video_title = video["snippet"]["title"]
            video_id = video["id"]["videoId"]
            video_url = "https://www.youtube.com/watch?v=" + video_id
            timestamp = video["snippet"]["publishedAt"].split('.')[0]

            description, category, view_count, like_count, dislike_count = self.__video_details_information(video_id)

            comment_list = self.__video_comment(video_id, comment_count)
            comments = self.__comment_information(comment_list, reply_count)

            channel_title = video["snippet"]["channelTitle"]
            channel_id = video["snippet"]["channelId"]
            channel_url = "https://www.youtube.com/channel/" + channel_id
            channel_subscribe_count = self.__channel_subscribe_information(channel_id)

            temp.extend([{
                'title': video_title,
                'view': view_count,
                'video_url': video_url,
                'channel_name': channel_title,
                'channel_url': channel_url,
                'channel_subscribe_count': channel_subscribe_count,
                'uploade_date': timestamp,
                'video_description': description,
                'category': category,
                'like': like_count,
                'dislike': dislike_count,
                'comments': comments
            }])

        with open('./videos.json', 'w', encoding='utf-8') as j:
            json.dump(temp, j, ensure_ascii=False, indent='\t')

    def crawling(self, word, videocount, commentcount, replycount):
        video_list = self.__video_list(word, videocount)
        self.__video_information(video_list, commentcount, replycount)