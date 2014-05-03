TITLE = 'London Live'
PREFIX = '/video/londonlive'

URL = 'http://www.londonlive.co.uk'
URL_LIVE = URL + '/tv'

def Start():
        Log.Debug('Start')


@handler(PREFIX, TITLE)
def Main():
        oc = ObjectContainer(title2 = 'London Live')
        
	content = HTML.ElementFromURL(URL_LIVE, errors='ignore', cacheTime=1800)

        thumb = content.xpath('//video/@poster')[0]
        
        oc.add(VideoClipObject(title = 'Live',
                               summary = 'Live stream',
                               thumb = thumb,
                               url = URL_LIVE))

        oc.add(DirectoryObject(title = 'Categories',
                               key = Callback(GetCategories),
                               summary = 'Browse programms by Category'))
        return oc

def GetCategories():
        oc = ObjectContainer(title2 = 'Categories')
        
        content = HTML.ElementFromURL(URL, errors='ignore', cacheTime=1800)
        categories = content.xpath("//li[@class='categories__item']/a")

        for category in categories:
                category_path = category.xpath("@href")[0]
                title = category.text
                oc.add(DirectoryObject(key=Callback(GetVideosInCategory, url=URL + category_path), title=title))
        return oc

def GetVideosInCategory(url):
        oc = ObjectContainer()
        content = HTML.ElementFromURL(url)
        programms = content.xpath("//div[@class='clip-tile']")

        for program in programms:
                playable = program.xpath(".//a[@class='clip-tile__play']")
                if len(playable) > 0:
                        title = program.xpath(".//h3[@class='clip-tile__title']")[0].text
                        thumb = program.xpath("a/span/noscript/img/@src")[0]
                        video_url = program.xpath("a[@class='clip-tile__link']/@href")[0]
                        oc.add(VideoClipObject(title=title, thumb=thumb, url=URL+video_url))
                        Log.Debug(title)
                        Log.Debug(thumb)
        return oc
