# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from ssl import PROTOCOL_TLS_SERVER
from urllib.parse import parse_qsl
import sys
import urllib.request
import urllib.parse
import json
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup
import re
import jdatetime

_current_videos_list_data=[]
_date_format='%Y-%m-%d'
_baseUrl = 'https://api.telewebion.com/v3/'
_channels_path = _baseUrl+'channels'
_channel_videos_path = _baseUrl+'episodes/content-archive?channel_desc={channel_id}&date={date}&page={page}'
_video_path=_baseUrl+'episodes/{id}/details?download_link=1&device=tv&enforce_copyright=1&'
_videoUrl = _baseUrl+'video/videohash/{vidUid}'
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url,urllib.parse.urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """

    response =urllib.request.urlopen( create_request(_channels_path))
    catsData = json.loads(response.read())
# categories is an array of this structure:
# {"id":"22","link":"https:\/\/www.aparat.com\/game","name":"\u06af\u06cc\u0645","videoCnt":"1221861","imgSrc":"https:\/\/www.aparat.com\/public\/public\/images\/etc\/category\/22.png?3","patternBgColor":"#1a1a1c","patternBgSrc":"https:\/\/www.aparat.com\/public\/public\/images\/etc\/category\/22_pattern.jpg?3","patternIconSrc":"https:\/\/www.aparat.com\/public\/public\/images\/etc\/category\/22_onpattern.png?3"}
    return catsData['data']


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    print('urlencode='+urllib.parse.urlencode(kwargs))
    return '{0}?{1}'.format(_url, urllib.parse.urlencode(kwargs))


def get_videos(channel_id,page):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or API.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    date=jdatetime.date.today()
    date=date.replace(day=date.day-1)
    url = _channel_videos_path.format(channel_id=channel_id,date=date.strftime(_date_format),page=page)
    response = urllib.request.urlopen(create_request( url))
    vidsData = json.loads(response.read())
    return vidsData['data']


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Aparat')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # category object struct: {"id":"22","link":"https:\/\/www.aparat.com\/game","name":"\u06af\u06cc\u0645","videoCnt":"1221861","imgSrc":"https:\/\/www.aparat.com\/public\/public\/images\/etc\/category\/22.png?3","patternBgColor":"#1a1a1c","patternBgSrc":"https:\/\/www.aparat.com\/public\/public\/images\/etc\/category\/22_pattern.jpg?3","patternIconSrc":"https:\/\/www.aparat.com\/public\/public\/images\/etc\/category\/22_onpattern.png?3"}

    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category['name'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({
                          'icon': category['image_name']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category['name'],
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(
            action='videos', channel_id=category['descriptor'], channel_name=category['name'], page=0,
            date=jdatetime.date.today().strftime(_date_format))
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)



def list_videos(channel_id, channel_name, page,date,append):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, channel_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_videos(channel_id,page)
    add_videos(videos,channel_name)

    #Add a next page item
    load_more_url = get_url(action='nextpage',type='videos',channel_id=channel_id,
    channel_name=channel_name, page=page+1,date=date)
    load_more_list_item = xbmcgui.ListItem(label='بیشتر...')
    xbmcplugin.addDirectoryItem(_handle,load_more_url,load_more_list_item,True)
    
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def add_videos(videos,channel_name):
    print("vidscount="+str(len(videos)))
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['program']['title'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['program']['title'] + ' - ' + video['title'],
                                    'genre': channel_name,
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt(
            {'thumb': video['picture_path'], 'icon': video['program']['cover_image_name'],
             'fanart': video['large_picture_path']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4

     

        url = get_url(action='play', video_id=video['id'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

def get_playable_video_url(videoPageUrl):
    return 'https://sdm.telewebion.com/vod/_definst_//media_b/telewebion/tv3/2021-06-07/normalProgram/124529/file.mp4/chunk.m3u8?wmsAuthSign=aXNfZnJlZT0xJnNlcnZlcl90aW1lPTYvMTAvMjAyMSAxMToxOTozMCBBTSZoYXNoX3ZhbHVlPUlwWmJmM0YrZlFYbVhmdUhXWE1WOXc9PSZ2YWxpZG1pbnV0ZXM9NjAwMA==&origin=sa14.telewebion.com'
    # this method can be improved by returning the most appropriate quality
    # based on the connection quality
    # currently, it returns the highest quality video available based on a tricky descending sort
    xbmc.log(videoPageUrl)
    url = urllib.request.urlopen(create_request( videoPageUrl))
    soup = BeautifulSoup(url.read())
    playerScript = soup.findAll('script')[-1]
    scriptStr =playerScript.string
    allJsonObjectStrings = re.findall('{"[^}]+}', scriptStr)
    allJsonObjectStrings.sort(reverse=True)
    for s in allJsonObjectStrings:
        try:
            j = json.loads(s)
            if j.has_key('type') and j['type'].startswith('video'):
                return j['src']
        except:  # s is not json-ish
            continue
    return None


def get_video_data(video_id):
    url = _video_path.format(id=video_id)
    response = urllib.request.urlopen(create_request( url))
    vidsData = json.loads(response.read())
    return vidsData['data']

def play_video(video_id):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    video_data=get_video_data(video_id)[0]
    video_size=video_data['file_size']*1000
    thumb= {'thumb':video_data['cover_image_name']}
    poster={'poster':video_data['large_picture_path']}
        
    video_info=[{'video':[{'size':video_size},
        {'date':jdatetime.date.today().strftime(_date_format)},
        {'genre':video_data['show_time']},
        {'playcount':video_data['view_count']},
        {'duration':video_data['duration_seconds']}]}]

    playable_link = video_data['vod_link'][-1:][0]['link']
    if playable_link != None:
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=playable_link)
        
        play_item.setArt(poster)
        play_item.setArt(thumb)
        play_item.setInfo('video', video_info)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def create_request(url):
    return urllib.request.Request(url,headers={'Origin':'https://pwa.telewebion.com/','Referer':'https://pwa.telewebion.com/'})


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    print('parameters='+paramstring)
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'videos':
            # Play a video from a provided URL.
            list_videos(params['channel_id'], params['channel_name'],
                        int(params['page']),params['date'],False)
        elif params['action'] == 'nextpage' and params['type']=='videos':
             list_videos(params['channel_id'], params['channel_name'],
                        int( params['page']),params['date'],True)
        elif params['action'] == 'play':
            play_video(params['video_id'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
