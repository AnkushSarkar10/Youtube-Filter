from app import app
from flask import render_template, flash , redirect , url_for
from app.forms import ChannelSearch

from apiclient.discovery import build
import json
key = "AIzaSyBnLNVcQOXkkeWgeBP1jWup5NYTDcUbUGQ"
youtube = build('youtube','v3',developerKey = key)

# THICC FUNCTIONS
def get_all_channels(channel_name):
    req_1 = youtube.search().list(part = 'snippet',q = channel_name,type = 'channel',maxResults = 5).execute()["items"]
    channels_dict = {}
    for i in req_1:
        channel_title = i["snippet"]["title"]
        channel_id = i["snippet"]["channelId"]
        req_2 = youtube.channels().list(id = channel_id,part = 'statistics').execute()
        sub_count = req_2["items"][0]["statistics"]["subscriberCount"]
        channels_dict[channel_id] = [channel_title,sub_count,channel_id]
    return channels_dict

def get_vid_stats(vid_ids):
    stats = []
    for i in range(0, len(vid_ids),50):
        res = youtube.videos().list(id = ','.join(vid_ids[i:i+50]),
                                    part = 'statistics').execute()
        stats += res['items']
    return stats
    

def get_name(channel_id):
    req = youtube.channels().list(id = channel_id,part = 'snippet').execute()
    name = req['items'][0]["snippet"]["title"]
    return name

def get_no_of_views(vid_id):
    req = youtube.videos().list(id = vid_id,part = 'statistics').execute()
    views = req['items'][0]['statistics']['viewCount']
    return views

def get_no_of_dislikes(vid_id):
    req = youtube.videos().list(id = vid_id,part = 'statistics').execute()
    dislikes = req['items'][0]['statistics']['dislikeCount']
    return dislikes

def get_no_of_likes(vid_id):
    req = youtube.videos().list(id = vid_id,part = 'statistics').execute()
    likes = req['items'][0]['statistics']['likeCount']
    return likes


def get_all_vids(channel_id):

    # req = youtube.search().list(part = 'snippet',q = channel_name,type = 'channel',maxResults = 1).execute()
    # channel_id = req['items'][0]['id']['channelId']

    channel = youtube.channels().list(id = channel_id,part = 'contentDetails').execute()
    uploads_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    vids = []
    next_page_token = None
    while True:
        uploads = youtube.playlistItems().list(playlistId = uploads_id
                    ,part = 'snippet',maxResults = 50,pageToken = next_page_token).execute()
        vids += uploads['items']
        next_page_token = uploads.get('nextPageToken')

        if next_page_token is None:
            break
    return vids

#routs

@app.route('/',methods = ['GET','POST'])
def home():
    form = ChannelSearch()
    if form.validate_on_submit():
        channel_dict = get_all_channels(form.name.data)
        return render_template("html/channels.html",channel_dict=channel_dict)
    return render_template("html/home.html", form = form)

@app.route('/channels')
def channels():
    return render_template("html/channels.html")
    
@app.route('/about')
def about():
    return render_template("html/about.html")


@app.route('/stats/<channel_id>')
def stats(channel_id):
    vid_ids = list(map(lambda x:x['snippet']['resourceId']['videoId'],get_all_vids(channel_id)))
    
    statistics = get_vid_stats(vid_ids) #big boi stats. need something? print this and figure it out! trust me its frikin lit!

    name = get_name(channel_id)

    most_liked = sorted(statistics, key = lambda x:int(x['statistics']['likeCount']), reverse=True)[0]
    most_liked_id = most_liked['id']
    no_of_likes = get_no_of_likes(most_liked_id)
    most_liked_embeded = f'<iframe class="embed-responsive-item" width="800" height="420" align="left" src="https://www.youtube.com/embed/{most_liked_id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'


    most_disliked = sorted(statistics, key = lambda x:int(x['statistics']['dislikeCount']), reverse=True)[0]
    most_disliked_id = most_disliked['id']
    no_of_dislikes = get_no_of_dislikes(most_disliked_id)
    most_disliked_embeded = f'<iframe class="embed-responsive-item" width="800" height="420" align="left" src="https://www.youtube.com/embed/{most_disliked_id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

    most_viewed = sorted(statistics, key = lambda x:int(x['statistics']['viewCount']), reverse=True)[0]
    most_viewed_id = most_viewed['id']
    no_of_views = get_no_of_views(most_viewed_id)
    most_viewed_embeded = f'<iframe class="embed-responsive-item" width="800" height="420" align="left" src="https://www.youtube.com/embed/{most_viewed_id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

    return render_template("html/stats.html",name = name,most_liked_embeded=most_liked_embeded,no_of_likes=no_of_likes,most_disliked_embeded=most_disliked_embeded,no_of_dislikes=no_of_dislikes,most_viewed_embeded=most_viewed_embeded,no_of_views=no_of_views)