#!/usr/bin/env python3


import sys
import json
import requests
import subprocess
from random import random
from math import floor

def get_access_token(stream_name):
    robj = {
            "operationName": "PlaybackAccessToken_Template",
            "query": "query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!) {  streamPlaybackAccessToken(channelName: $login, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isLive) {    value    signature    __typename  }  videoPlaybackAccessToken(id: $vodID, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isVod) {    value    signature    __typename  }}",
            "variables": {
                "isLive": True,
                "login": stream_name,
                "isVod": False,
                "vodID": "",
                "playerType": "site"
        }
    }

    json_data = json.dumps(robj)
    # header copied from twitch, should be anonymous
    headers = {'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko'}
    response = requests.post("https://gql.twitch.tv/gql", data=json_data, json=True, headers=headers)
    rjson = json.loads(response.text)

    return rjson['data']['streamPlaybackAccessToken']

def get_m3u8_streams(channel, atoken):
    sig = atoken['signature']
    value = atoken['value']
    p = floor(random() * 99999) + 1

    url_template = f'https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8?allow_source=true&fast_bread=true&p={p}&player_backend=mediaplayer&playlist_include_framerate=true&reassignments_supported=true&sig={sig}&supported_codecs=avc1&token={value}&cdm=wv&player_version=1.10.0'
    headers = {'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko'}
    response = requests.get(url_template, headers=headers)
    return response.text

# TODO: actually parse the m3u8 text so we can select a stream with specific quality
def get_stream_m3u8(streams_text):
    lines = streams_text.split('\n')
    for line in lines:
        if line.startswith('https://'):
            return line

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: vlctwitch.py <stream name>")
        exit(1)

    atoken = get_access_token(sys.argv[1])
    streams = get_m3u8_streams(sys.argv[1], atoken)
    link = get_stream_m3u8(streams)
    subprocess.call(['vlc', link])
