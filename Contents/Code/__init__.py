import re, string, time
from datetime import timedelta, datetime, tzinfo
import datetime

####################################################################################################

LLEWTUBE_PREFIX     = "/video/carpool"
LLEWTUBE_RSS_URL    = "http://feeds.feedburner.com/LlewTube"
MEDIA_NAMESPACE     = {'media':'http://search.yahoo.com/mrss/'}
BLIP_NAMESPACE      = {'blip':'http://blip.tv/dtd/blip/1.0'}
DEBUG_XML_RESPONSE  = False
CACHE_INTERVAL      = 1800

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(LLEWTUBE_PREFIX, MainMenu, L("carpool"), "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup('_List', viewMode='List', mediaType='items')
  MediaContainer.title1 = L("carpool")
  MediaContainer.content = 'Items'
  #MediaContainer.art = R('art-default.jpg')
  MediaContainer.viewGroup = 'Details'
  HTTP.SetCacheTime(CACHE_INTERVAL)

#def UpdateCache():
#  HTTP.Request(LLEWTUBE_RSS_URL)

def MainMenu():

  dir = MediaContainer(viewGroup='_List')

  dir.Append(Function(DirectoryItem(ListEpisodes, title=L('mostrecent'), thumb=R('icon-default.png')), order='mostrecent'))
  dir.Append(Function(DirectoryItem(ListEpisodes, title=L('atoz'), thumb=R('icon-default.png')), order='atoz'))

  return dir


def ListEpisodes(sender, order):

  # Top level menu
  # Show available episodes

  dir = MediaContainer()
  dir.title2 = L(order)

  page = HTML.ElementFromURL(LLEWTUBE_RSS_URL)

  episodes = page.xpath("//channel/item")

  videos = {}

  for episode in episodes:

    episodeTitle = episode.xpath("./title/text()")[0]
    # Strip 'CarPool' from the title
    episodeTitle = re.sub ("CarPool", "", episodeTitle)
    episodeTitle = re.sub ("Car Pool", "", episodeTitle)
    episodeTitle = re.sub ("Carpool", "", episodeTitle)
    episodeTitle = re.sub ("iPhone ", "", episodeTitle, re.I)
    episodeTitle = TidyString(episodeTitle)

    # Set the subtitle to the date
    episodeDate = episode.xpath("./datestamp/text()", namespaces=BLIP_NAMESPACE)
    episodeDate = re.search(r"\'(.*)\'", str(episodeDate)).group(1)
    episodeSubtitle = ' '.join(episodeDate[:-1].split('T'))
    
    # Get the description
    episodeDescription = TidyString(episode.xpath("./puredescription/text()", namespaces=BLIP_NAMESPACE)[0])
    episodeImage = episode.xpath("./thumbnail", namespaces=MEDIA_NAMESPACE)[0].get('url')

    # Episodes are available in flv or in a higher quality in either mp4 or m4v
    episodeHq = episode.xpath("./group/content[not(@type='video/x-flv')]")[0].get('url')
    #episodeFlv = episode.xpath("./group/content[@type='video/x-flv']")[0].get('url')

    episodeLengthSeconds = episode.xpath("./runtime/text()", namespaces=BLIP_NAMESPACE)[0]
    episodeLength = str(int(episodeLengthSeconds) * 1000)

    video = VideoItem(episodeHq, episodeTitle, episodeSubtitle, episodeDescription, episodeLength, episodeImage)

    if order == 'mostrecent':
      dir.Append(video)
    else:
      videos[episodeTitle] = video

  if order == 'atoz':
    titles = videos.keys()
    titles.sort(key=str.lower)
    for title in titles:
      dir.Append(videos[title])

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def TidyString(stringToTidy):
  # Function to tidy up strings works ok with unicode, 'strip' seems to have issues in some cases so we use a regex
  if stringToTidy:
    # Strip new lines
    stringToTidy = re.sub(r'\n', r' ', stringToTidy)
    # Strip leading / trailing spaces
    stringSearch = re.search(r'^\s*(\S.*?\S?)\s*$', stringToTidy)
    if stringSearch == None: 
      return ''
    else:
      return stringSearch.group(1)
  else:
    return ''
