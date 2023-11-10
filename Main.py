
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from PIL import Image
from io import BytesIO
import time
import requests
from YTProject import *
from YouTubeSQL import*
from ExecSql import*

st.set_page_config(page_title= "YoutubeDataHarvesting",
                   layout= "wide",)

selected_menu = option_menu(None,["Select Channels","MySQL","Queries"],
                icons=["house","cloud-upload",'gear'],
                orientation='horizontal')

if selected_menu=='Select Channels':
        left,center,right=st.columns([3.5,5.5,2])
        with left:
            channel_id=st.text_input('Enter channel ID:')
            if st.button('SEARCH'):
                with st.spinner('Fetching channel information...'):
                    time.sleep(2)
                with center:
                    channel_data = get_channel_data(youtube, channel_id)
                    df = pd.DataFrame(channel_data, index=['Channel Information'])
                    channel = df.T
                    name=channel_data["channel_name"]
                    st.write(f"##### ***:red[You searched] {name} :red[youtube channel]***")
                    st.dataframe(channel,width=400)
                
            if st.button('UPLOAD TO MONGODB DATABASE'):
                with st.spinner('uploading channel information ...'):
                    with left:
                        def channel_video_comment():
                            channel_data= get_channel_data(youtube, channel_id)
                            playlist_id = channel_data['playlist_id']
                            video_id = get_video_ids(youtube, playlist_id)
                            video_data = get_video_data(youtube, video_id)
                            comment_data = get_comment_data(youtube, video_id)
                            channel = {
                                'channel_info': channel_data,
                                'video_info': {}
                            }
                            for count, vid_data in enumerate(video_data, 1):
                                v_id = f"Video_Id_{count}"
                                cmt = {}
                                for i in comment_data:
                                    if i["Video_id"] == vid_data["video_id"]:
                                        c_id = f"Comment_Id_{len(cmt) + 1}"
                                        cmt[c_id] = {
                                            "Comment_Id": i.get("Comment_Id", 'comments_disabled'),
                                            "Comment_Text": i.get("Comment_Text", 'comments_disabled'),
                                            "Comment_Author": i.get("Comment_Author", 'comments_disabled'),
                                            "Comment_Published_At": i.get("Comment_Published_At", 'comments_disabled')
                                        }
                                vid_data["Comments"] = cmt
                                channel['video_info'][v_id] = vid_data
                            return channel
                        channel=channel_video_comment()
                        try:
                            check_existing_document = collection.find_one({"channel_info.channel_id": channel_id})
                            if check_existing_document is None:
                                collection.insert_one(channel)
                                st.success('Successfully uploaded ',icon='✔️')
                                st.info('Please select an option Database to view and migrate the channel data',icon='ℹ️')
                            else:
                                st.error("  OOPS  channel_ID already uploaded Try with different channel_ID",icon='❕')
                        except Exception as e:
                            print(f"Error occurred while uploading channel information: {str(e)}")


if selected_menu == 'MySQL':
        nosql,sql=st.columns([2,2])
        with nosql:
            with st.spinner('Fetching ...'):
                channel_list=channel_list()
                option=st.selectbox('UPLOADED CHANNEL NAME LIST',['Please select channel name']+channel_list)

        for result in collection.find({"channel_info.channel_name": option}):
            channel_info = result['channel_info']
            video_info = result['video_info']

        with sql:
            if st.button('MIGRATE TO SQL'):
                with st.spinner('Migrating ...'):
                    channel_name_to_find = option
                    channel_df, playlist_df,video_df, comment_df = NOSQL_TO_SQL(channel_name_to_find)
                    
                    channel_df.to_sql('channel_data', con=engine, if_exists='append', index=False)
                    playlist_df.to_sql('playlist_data', con=engine, if_exists='append', index=False)
                    video_df.to_sql('video_data', con=engine, if_exists='append', index=False)
                    comment_df.to_sql('comment_data', con=engine, if_exists='append', index=False)
                    st.success(f"{channel_name_to_find} channel migrated successfully", icon='✅')



if selected_menu == 'Queries':
        select_question = st.selectbox("Select the Queries", ('Select question here',
                                                                            '1. What are the names of all the videos and their corresponding channels?',
                                                                            '2. Which channels have the most number of videos, and how many videos do they have?',
                                                                            '3. What are the top 10 most viewed videos and their respective channels?',
                                                                            '4. How many comments were made on each video, and what are their corresponding video names?',
                                                                            '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                                                            '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                                                            '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                                                            '8. What are the names of all the channels that have published videos in the year 2022?',
                                                                            '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                                                            '10. Which videos have the highest number of comments, and what are their corresponding channel names?'))

        if select_question== '1. What are the names of all the videos and their corresponding channels?':

            st.write(qust_1())
        elif select_question=='2. Which channels have the most number of videos, and how many videos do they have?':
            st.write(qust_2())
        elif select_question=='3. What are the top 10 most viewed videos and their respective channels?':
            st.write(qust_3())
        elif select_question=='4. How many comments were made on each video, and what are their corresponding video names?':
            st.write(qust_4())
        elif select_question=='5. Which videos have the highest number of likes, and what are their corresponding channel names?':
            st.write(qust_5())
        elif select_question=='6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
            st.write(qust_6())
        elif select_question=='7. What is the total number of views for each channel, and what are their corresponding channel names?':
            st.write(qust_7())
        elif select_question=='8. What are the names of all the channels that have published videos in the year 2022?':
            st.write(qust_8())
        elif select_question=='9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
            st.write(qust_9())
        elif select_question== '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
            st.write(qust_10())
