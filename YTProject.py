import googleapiclient.discovery

import pymongo
api_service_name = "youtube"
api_version = "v3"

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey='AIzaSyBwI7Cids-F3dlk79osPiZsnJ5xXmrkjUE')

mongodburl="mongodb://localhost:27017/"
db_name="YouTube"
client=pymongo.MongoClient(mongodburl)
db=client[db_name]
collection_name="YouTube_Channels"
collection=db[collection_name]


# channel_id='UC4muYPMCSYigqIwRjVWkQ2Q'


def get_channel_data(youtube, channel_id):
    channel_info_request = youtube.channels().list(
        part="snippet,contentDetails,statistics,status,topicDetails",
        id=channel_id
    ).execute()

    channel = channel_info_request['items'][0]
    # channel_image = dict(image=channel['snippet']['thumbnails']['medium']['url'])

    channel_type = channel_info_request['items'][0]['topicDetails']['topicCategories']
    filtered_type = [i for i in channel_type if 'Lifestyle' not in i]
    type_of_channel = filtered_type[0].split('/')[-1] if filtered_type else channel_type[0].split('/')[-1]

    channel_data = {
        'channel_id': channel_id,
        'channel_name': channel['snippet']['title'],
        'subscribers_count': channel['statistics']['subscriberCount'],
        'video_count': channel['statistics']['videoCount'],
        'view_count': channel['statistics']['viewCount'],
        'channel_description': channel['snippet']['description'],
        'Channel_Status': channel['status']['privacyStatus'],
        'Channel_Type': type_of_channel,
        'playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
    }
    return channel_data

def get_video_ids(youtube, playlist_id):
    video_ids = []
    next_page_token = None
    while True:
        try:
            video_id_request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=2,
                pageToken=next_page_token
            ).execute()

            v_id = video_id_request['items']
            for item in v_id:
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            next_page_token = video_id_request.get('nextPageToken')
            if next_page_token is None:
                break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break
    return video_ids


def get_video_data(youtube, video_id):
    videos_data = []
    for video_ids in video_id:
        video_data_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            
            id=video_ids,
            
        ).execute()

        video_info = video_data_request['items'][0]

        video_data = {
            'video_id': video_info['id'],
            'channel_id': video_info['snippet']['channelId'],
            'video_name': video_info['snippet']['title'],
            'video_description': video_info['snippet']['description'],
            'published_date': video_info['snippet']['publishedAt'],
            'channel_title': video_info['snippet']['channelTitle'],
            'category_id': video_info['snippet']['categoryId'],
            'view_count': video_info['statistics']['viewCount'],
            'like_count': video_info['statistics'].get('likeCount', 0),
            "dislike_Count": video_info['statistics'].get('dislikeCount', 0),
            "favorite_Count": video_info['statistics'].get('favoriteCount', 0),
            'comment_count': video_info['statistics'].get('commentCount', 0),
            'duration': video_info['contentDetails']['duration'],
            'thumbnail': video_info['snippet']['thumbnails']['default']['url'],
            'caption_status': video_info['contentDetails']['caption']
        }
        videos_data.append(video_data)
    return videos_data

def get_comment_data(youtube, video_id):
    comments_data = []
    for ids in video_id:
        try:
            video_data_request = youtube.commentThreads().list(
                part="snippet",
                videoId=ids,
                maxResults=20
            ).execute()
            video_info = video_data_request['items']
            for comment in video_info:
                comment_info = {
                    'Video_id': comment['snippet']['videoId'],
                    'Comment_Id': comment['snippet']['topLevelComment']['id'],
                    'Comment_Text': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                    'Comment_Author': comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'Comment_Published_At': comment['snippet']['topLevelComment']['snippet']['publishedAt'],
                }
                comments_data.append(comment_info)
        except Exception as e:
            if e.resp.status == 403 and 'disabled comments' in str(e):
                comment_info = {
                    'Video_id': ids,
                    'Comment_Id': 'comments_disabled',
                }
                comments_data.append(comment_info)
            else:
                print(f"An error occurred while retrieving comments for video: {ids}")
                print(f"Error details: {e}")
    return comments_data


# def channel_video_comment():
#                             channel_data = get_channel_data(youtube, channel_id)
#                             playlist_id = channel_data['playlist_id']
#                             video_id = get_video_ids(youtube, playlist_id)
#                             video_data = get_video_data(youtube, video_id)
#                             comment_data = get_comment_data(youtube, video_id)
#                             channel = {
#                                 'channel_info': channel_data,
#                                 'video_info': {}
#                             }
#                             for count, vid_data in enumerate(video_data, 1):
#                                 v_id = f"Video_Id_{count}"
#                                 cmt = {}
#                                 for i in comment_data:
#                                     if i["Video_id"] == vid_data["video_id"]:
#                                         c_id = f"Comment_Id_{len(cmt) + 1}"
#                                         cmt[c_id] = {
#                                             "Comment_Id": i.get("Comment_Id", 'comments_disabled'),
#                                             "Comment_Text": i.get("Comment_Text", 'comments_disabled'),
#                                             "Comment_Author": i.get("Comment_Author", 'comments_disabled'),
#                                             "Comment_Published_At": i.get("Comment_Published_At", 'comments_disabled')
#                                         }
#                                 vid_data["Comments"] = cmt
#                                 channel['video_info'][v_id] = vid_data
#                             return channel
# channel=channel_video_comment()
# try:
#                             check_existing_document = collection.find_one({"channel_info.channel_id": channel_id})
#                             if check_existing_document is None:
#                                 collection.insert_one(channel)
                                
                    
# except Exception as e:
#                             print(f"Error occurred while uploading channel information: {str(e)}")


