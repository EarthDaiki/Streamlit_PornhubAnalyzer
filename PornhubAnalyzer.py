#webdrive is installed from packages.txt

import matplotlib.pyplot as plt
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import json
import datetime
from datetime import timedelta
import streamlit as st
from yt_dlp import YoutubeDL
import os
import subprocess
from streamlit_modal import Modal
import streamlit.components.v1 as components

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option("display.max_colwidth", 200)

st.set_page_config(
    page_title='PornhubAnalyzer🔥', 
    page_icon="./data/MetaHumanIcon.png", 
    layout="centered", 
    initial_sidebar_state="auto", 
    menu_items={
        "Get help": "https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md#supported-sites",
        "Report a Bug": "https://twitter.com/_EarthStation_",
        'About': "詳細はこちら:"
        }
    )
Filename = None

@st.cache_data
def FindElements(url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    sleep(2)
    VideoTime = driver.find_element(By.CSS_SELECTOR, 'span.mgp_total').get_attribute("innerHTML")

    player = driver.find_element(By.ID, 'player')
    hotspots = player.find_element(By.CSS_SELECTOR, 'script[type="text/javascript"]').get_attribute("innerHTML")
    return VideoTime, hotspots

def Formating(VideoTime):
    if len(VideoTime) == 2:
        VideoTime = f"00:00:{VideoTime}"

    if len(VideoTime) == 4:
        VideoTime = f"00:0{VideoTime}"

    if len(VideoTime) == 5:
        VideoTime = f"00:{VideoTime}"

    print(VideoTime)
    return VideoTime

def ToSecond(VideoTime):
    TimeDelta = pd.to_timedelta(VideoTime)
    Seconds = TimeDelta.total_seconds()
    return Seconds

def ExtractHotspotsFromString(hotspots):
    hotspots_data = None
    if 'hotspots' in hotspots:
        start_index_hot = hotspots.index('"hotspots"')
        start_index_url = hotspots.index(',"toprated_url"')
        hotspots_data = hotspots[start_index_hot:start_index_url]
        hotspots_data = "{" + hotspots_data + "}"
    with open('Pornhub.json', 'w') as data:
        data.write(hotspots_data)
    with open('Pornhub.json', 'r') as data:
        hotspots_data = json.load(data)
        IntensityList = hotspots_data["hotspots"]
    return IntensityList

def CheckInterval(Seconds, IntensityList):
    Split = int(Seconds) / len(IntensityList)
    print(f"Interval {int(Split)}")
    print(f"Len of hotspots list {len(IntensityList)}")
    return Split

def DoDataFrame(IntensityList, Split):
    secondlist = []
    Int_IntensityList = []
    TimeDeltaList = []
    count = 0
    for i in IntensityList:
        Int_IntensityList.append(int(i))
        secondlist.append(count)
        count = int(Split) + count

    for Time in secondlist:
        Minutes = datetime.timedelta(seconds=Time)
        if len(str(Minutes)) == 7:
            Minutes = '0'+ str(Minutes)
        TimeDeltaList.append(Minutes)

    df = pd.DataFrame({'Time':TimeDeltaList, 'Intensity':Int_IntensityList})
    df_sorted = df.sort_values('Intensity', ascending=False, key=lambda x: x.astype(int))
    #print(f"\nNot Sorted DataFrame\n{df}\n")
    print(f"Sorted DataFrame\n{df_sorted}\n")
    return TimeDeltaList, Int_IntensityList, df, df_sorted


def Graphing(TimeDeltaList, Int_IntensityList):
    x = TimeDeltaList
    y = Int_IntensityList

    plt.plot(x, y)

    plt.xlabel('Time (00:00:00)')
    plt.ylabel('Value')
    plt.title('Replayed')

    plt.xticks(range(0, len(TimeDeltaList), 25))

    plt.show()

def ShowChart(df):
    st.line_chart(df, x='Time', y='Intensity')

def ShowDataframes(df, df_sorted):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('時間順')
        st.dataframe(df)
    with col2:
        st.markdown('視聴順')
        st.dataframe(df_sorted)

def ErrorMessage(Error):
    if Error == "FilledIn":
        st.error('記入されていない項目があります')
    elif Error == "URL":
        st.error('URLの処理でエラーが起きました')
    elif Error == "Replay":
        st.error("リプレイ情報が存在しません")
    elif Error == "Convert":
        st.error('mp4にコンバートする際にエラーが起きました')

def GetVideos(i):
    Start_Seconds = 0
    End_Seconds = 0
    Time = datetime.datetime.strptime(i, '%H:%M:%S')

    Start = Time - timedelta(seconds=int(Split))
    if Start < datetime.datetime.strptime("00:00:00", "%H:%M:%S"):
        Start = datetime.datetime.strptime("00:00:00", "%H:%M:%S")
    Start = datetime.datetime.strftime(Start, "%H:%M:%S")

    End = Time + timedelta(seconds=int(Split))
    End = datetime.datetime.strftime(End, "%H:%M:%S")

    
    Start = datetime.datetime.strptime(Start, '%H:%M:%S').time()
    Start_Seconds = timedelta(hours=Start.hour, minutes=Start.minute, seconds=Start.second).total_seconds()

    End = datetime.datetime.strptime(End, '%H:%M:%S').time()
    End_Seconds = timedelta(hours=End.hour, minutes=End.minute, seconds=End.second).total_seconds()
    # st.markdown(Start)
    # print(int(Start_Seconds))
    # st.markdown(End)
    # print(int(End_Seconds))
    return int(Start_Seconds), int(End_Seconds)
    

def PartVideoDownloader(number, Start_Seconds, End_Seconds, Format):

    def set_download_ranges(info_dict, self):
        duration_opt = [{
            'start_time': Start_Seconds,
            'end_time': End_Seconds
        }]
        return duration_opt
    
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        VideoFormat = 'bestvideo+bestaudio[ext=m4a]/best'
    else:
        VideoFormat = 'bestvideo+bestaudio/best'

    ydl_options={
        "format" : VideoFormat,
        'download_ranges': set_download_ranges,
        'outtmpl': f'%(title)s[%(id)s]{number}.%(ext)s'
    }
    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url)
        Filename = ydl.prepare_filename(info)
        try:
            if Format == 'mp4' or Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
                Filename = ConvertToMP4(Filename)
        except:
            ErrorMessage('Convert')
            exit()
        st.markdown(Start_Seconds)
        st.markdown(End_Seconds)
        st.video(Filename)

    return Filename

@st.cache_data(max_entries=1)
def VideoDownloader():
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        VideoFormat = 'bestvideo+bestaudio[ext=m4a]/best'
    else:
        VideoFormat = 'bestvideo+bestaudio/best'

    ydl_options={
        "format" : VideoFormat,
        'outtmpl': '%(title)s[%(id)s].%(ext)s'
    }

    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(UrlForDownload)
        Filename = ydl.prepare_filename(info)
        try:                
            if Format == 'mp4' or Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
                Filename = ConvertToMP4(Filename, info)
        except:
            ErrorMessage('Convert')
            exit()
        st.video(Filename)
    return Filename

def ShowVideo(Filename):
    st.video(Filename)

def VideoDownloadBtn(Filename):
    with open (Filename, 'rb') as data:
        st.download_button(label=':red[Download]🍿', data=data, file_name=Filename, mime='video/mp4')

def PartVideoDownloadBtn(Filename):
    # Filename = Filename.replace('.webm', '.mp4')
    with open (Filename, 'rb') as data:
        st.download_button(label=':red[Download]🍿', data=data, file_name=Filename, mime='video/mp4')

@st.cache_data(max_entries=1)
def AudioDownloader():
    ydl_options={
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0'
        }],
        # 'outtmpl': '%(title)s[%(id)s].mp3'
        # 'cookiesfrombrowser': ('chrome', )
    }
    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(UrlForDownload)
        Filename = ydl.prepare_filename(info)
        Filename = Filename.replace('.webm', '.mp3').replace('.mp4', '.mp3')
        st.audio(Filename, format="audio/mp3")
    return Filename

def AudioDownloadBtn(Filename):
    with open (Filename, 'rb') as data:
        st.download_button(label=':red[Download]🎵', data=data, file_name=Filename, mime='audio/mp3')

def ConvertToMP4(Filename, info):
    WebmFilename = Filename
    if Format == 'mp4':
        MP4Filename = Filename.replace('.webm', '.mp4')
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        MP4Filename = Filename.replace('.mkv', '.mp4')
        MP4Filename = "libx264" + MP4Filename
    if os.path.exists(MP4Filename):
        if not info['ext'] == 'mp4':
            os.remove(MP4Filename)
    if Format == 'mp4':
        if not info['ext'] == 'mp4':
            command = f'ffmpeg -i "{WebmFilename}" -c:v copy -c:a copy "libx264{MP4Filename}"'
            subprocess.run(command, shell=True)
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        command = f'ffmpeg -i "{WebmFilename}" -c:v libx264 -profile:v high -level:v 4.0 -crf 22 -c:a copy "{MP4Filename}"'
        subprocess.run(command, shell=True)
    if not info['ext'] == 'mp4':
        os.remove(WebmFilename)
    return MP4Filename

def OpenModal(modal):
    if modal.is_open():
        with modal.container():
            html_string = '''
                <h1>HTML string in RED</h1>
                <script language="javascript">
                document.querySelector("h1").style.color = "red";
                </script>
                '''
            components.html(html_string)
            okay = st.button('Okay')
            if okay:
                modal.close()

def EmbedVideo():
    video_id = url.split('=')[-1]
    embed_url = f'https://www.pornhub.com/embed/{video_id}'
    style = "display: flex; justify-content: center; align-items: center;"
    video_embed = f'''
    <iframe src="{embed_url}" frameborder="0" width="560" height="340" scrolling="no" allowfullscreen></iframe>
    '''
    st.markdown(video_embed, unsafe_allow_html=True)

def OnChangeVideo(Filename):
    if not Filename == None:
        os.remove(Filename)
    VideoDownloader.clear()

def OnChangeAudio():
    AudioDownloader.clear()

if "Submit" not in st.session_state:
    st.session_state.Submit = False
if "download_video" not in st.session_state:
    st.session_state.download_video = False
if "download_audio" not in st.session_state:
    st.session_state.download_audio = False
if "popup" not in st.session_state:
    st.session_state.popup = False
if "age" not in st.session_state:
    st.session_state.age = False

modal = Modal("Demo Modal", key='1')
col1, col2 = st.columns(2)
st.title('Pornhub Analyzer🚀')
with st.form('Graph'):
    url = st.text_input('**MostReplayedが存在する動画のURLを入れてください**', placeholder='https://www.pornhub.com/view_video.php?viewkey=')
    submit = st.form_submit_button('Start Analyzing')

if submit or st.session_state.Submit:
    if url == '':
        ErrorMessage('FilledIn')
        exit()
    # if st.session_state.age:
    with st.spinner('情報取得中・・・'):
        st.session_state.Submit = True
        # try:
        VideoTime, hotspots = FindElements(url)
        # except:
        #     ErrorMessage('URL')
        #     exit()
        VideoTime = Formating(VideoTime)
        Seconds = ToSecond(VideoTime)
        try:
            IntensityList = ExtractHotspotsFromString(hotspots)
        except:
            ErrorMessage('Replay')
            exit()
        Split = CheckInterval(Seconds, IntensityList)
        TimeDeltaList, Int_IntensityList, df, df_sorted = DoDataFrame(IntensityList, Split)
        ShowDataframes(df, df_sorted)
        ShowChart(df)
        EmbedVideo()
        # NumberOfVideos = st.number_input('**上位何個のビデオをダウンロードしますか：**', 1, 99, 1)
        # PartDownload = st.button('ビデオを表示する')
        # if PartDownload:
        #     head = df_sorted.head(NumberOfVideos)
        #     for number, i in enumerate(head['Time']):
        #         with st.spinner('ダウンロード中・・・'):
        #             number, Start_Seconds, End_Seconds = GetVideos(i)
        #             if Start_Seconds == 0:
        #                 st.markdown('0秒から始まる映像は省きました')
        #             if not Start_Seconds == 0:
        #                 Format = st.radio('**形式を選んでください**', ('webm', 'mp4', 'mp4+m4a(スマートフォンの場合はこちらを選択してください)'), horizontal=True, key=f'MostReplayed_key{number}', help='スマートフォンからアクセスの場合はmp4選択してください')
        #                 Filename = PartVideoDownloader(number, Start_Seconds, End_Seconds, Format)
        #                 PartVideoDownloadBtn(Filename)

st.title('動画ダウンロード🚀', help='最高品質でダウンロードできます！(mp4)  \n*ログインが必要な動画はダウンロードできません  \n*音声または映像が再生されない場合は動画再生アプリを変更してください(推奨: VLC Media Player)')
with st.form(key='download'):
    UrlForDownload = st.text_input('**ダウンロードしたい動画のURLを入れてください**', placeholder='https://www.youtube.com/watch?v=, https://www.twitch.tv/videos/, etc...')
    col1, col2 = st.columns(2)
    with col1:
        Format = st.radio('**形式を選んでください**', ('mp4', ), horizontal=True, key='downloader', help='現在はmp4のみのサポートとなっています')
        VideoDownload = st.form_submit_button('動画全体をダウンロード', on_click=OnChangeVideo, args=(Filename,))
    with col2:
        st.markdown('**音声ファイルはmp3です**')
        AudioDownload = st.form_submit_button('音声のみをダウンロード', on_click=OnChangeAudio)

col1, col2, col3 = st.columns(3)
with col1:
    if VideoDownload or st.session_state.download_video:
        if not UrlForDownload:
            ErrorMessage('FilledIn')
            exit()
        with st.spinner('ロード中・・・'):
            try:
                Filename = VideoDownloader()
            except:
                ErrorMessage('URL')
                exit()
            st.session_state.download_video = True
            VideoDownloadBtn(Filename)
with col2:
    if AudioDownload or st.session_state.download_audio:
        if not UrlForDownload:
            ErrorMessage('FilledIn')
            exit()
        with st.spinner('ロード中・・・'):
            try:
                Filename = AudioDownloader()
            except:
                ErrorMessage('URL')
                exit()
            st.session_state.download_audio = True
            AudioDownloadBtn(Filename)

refresh = st.button("キャッシュを消す")
if refresh:
    st.cache_data.clear()