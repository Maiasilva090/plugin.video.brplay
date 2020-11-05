# -*- coding: utf-8 -*-

import requests
import datetime
import time
import player
from scraper_vod import FANART


POSTER_URL = 'http://i.cdn.turner.com/tntla/images/portal/fixed/cards/{titleId}_424x636{lang}.jpg'

CHANNEL_MAP = {
    'TNTLA_BR': 'TNT',
    'TNTSLA_BR': 'TNT Series',
    'SPACELA_BR': 'Space',
}

LOGO_MAP = {
    'TNTLA_BR': 'https://turner-latam-prod.akamaized.net/PROD-LATAM/live-channels/tnt_left.png',
    'TNTSLA_BR': 'https://turner-latam-prod.akamaized.net/PROD-LATAM/live-channels/tnts-pt.png',
    'SPACELA_BR': 'https://turner-latam-prod.akamaized.net/PROD-LATAM/live-channels/space.png',
}


PLAYER_HANDLER = player.__name__


def get_live_channels():
    # epg_url = 'http://schedule.dmti.cloud/schedule?from=2020-09-24T00:00:00&to=2020-10-01T00:00:00&feed=TNTLA_BR&mapped=true'
    # title_details = 'http://schedule.dmti.cloud/show-detail?id=1600898464519&mapped=true&output=json'
    # url = 'https://apac.ti-platform.com/AGL/1.0/R/PT/PCTV/TNTGO_LATAM_BR/LIVE/CHANNELS'

    channel_ids = '1000036824,1000036827,1000036819'
    language = 'POR'  # 'ENG'

    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_timestamp = to_timestamp(today)
    end_timestamp = to_timestamp(today + datetime.timedelta(days=1))
    epg_url = 'https://api.tntgo.tv/AGL/1.0/a/{language}/PCTV/TNTGO_LATAM_BR/CHANNEL/EPG?channelId={channels}&startTimeStamp={startTimeStamp}&endTimeStamp={endTimeStamp}&channel=PCTV'.format(language=language, channels=channel_ids, startTimeStamp=start_timestamp, endTimeStamp=end_timestamp)

    channels = requests.get(epg_url).json().get('resultObj', {}).get('channelList', [])

    now_timestamp = to_timestamp(datetime.datetime.now())

    results = []
    for channel in channels:

        programmes = channel.get('programList', []) or []
        programme = next((p for p in programmes if p.get('startTime', 0) <= now_timestamp <= p.get('endTime', 0)), {})

        program_details_url = 'http://schedule.dmti.cloud/show-detail?id={id}&mapped=true&output=json'.format(id=programme.get('contentId', ''))
        program_details_response = requests.get(program_details_url).json()

        details_key = next(iter(program_details_response.keys()), None)
        details = program_details_response.get(details_key, {}) or {}

        channel_name = CHANNEL_MAP.get(channel.get('callLetter'), channel.get('channelName', '')) or channel.get('channelName', '')

        title = programme.get('title', '')
        subtitle = programme.get('subtitle', '') if programme.get('subtitle', '') != title else u''
        plot = programme.get('contentDescription', '')
        plotoutline = programme.get('shortDescription', '')

        start_time = datetime.datetime.utcfromtimestamp(programme.get('startTime', 0))

        lang = details.get('lang', '')

        poster_lang = '_pt' if lang == 'pt' else ''

        poster_url = POSTER_URL.format(titleId=details.get('titleId', ''), lang=poster_lang)

        logo = LOGO_MAP.get(channel.get('callLetter'))

        program_name = title + (u': ' + subtitle if subtitle else u'')

        results.append({
            'handler': PLAYER_HANDLER,
            'method': 'playlive',
            'id': channel.get('channelId', ''),
            'IsPlayable': True,
            'livefeed': True,
            'label': u"[B]" + channel_name + u"[/B][I] - " + program_name + u"[/I]",
            'title': u"[B]" + channel_name + u"[/B][I] - " + program_name + u"[/I]",
            'studio': 'TNT Play',
            # 'title': subtitle,
            # 'originaltitle': details.get('originalTitle'),
            # 'tvshowtitle': title,
            'sorttitle': program_name,
            'channel_id': channel.get('channelId', ''),
            'dateadded': datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S'),
            'plot': plot,
            'plotoutline': plotoutline,
            'duration': programme.get('duration', 0) or 0,
            'adult': False,
            'cast': details.get('actorList', []).split(','),
            'director': details.get('directorList', []).split(','),
            'genre': details.get('genreList'),
            'rating': details.get('rate'),
            'year': details.get('releaseYear'),
            'country': details.get('country'),
            'episode': details.get('episode'),
            'season': details.get('season'),
            'art': {
                'thumb': poster_url,
                'tvshow.poster': poster_url,
                'clearlogo': logo,
                'fanart': FANART,
            }
        })

    return results


def to_timestamp(date):
    return int((time.mktime(date.timetuple()) + date.microsecond / 1000000.0))
