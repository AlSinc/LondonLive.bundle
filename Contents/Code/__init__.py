TITLE = 'London Live'
PREFIX = '/video/londonlive'

URL = 'http://www.londonlive.co.uk'
URL_LIVE = URL + '/tv'

def Start():
        Log.Debug('Start')


@handler(PREFIX, TITLE)
def Main():
        oc = ObjectContainer(title2 = 'Live Stream')
        
	content = HTML.ElementFromURL(URL_LIVE, errors='ignore', cacheTime=1800)

        url = content.xpath('//video/source/@src')[0]
        thumb = content.xpath('//video/@poster')[0]
        Log.Debug(url)
        
        oc.add(VideoClipObject(url = url,
                               title = 'Live', 
                               summary = 'Live stream',
                               thumb = thumb,
                               items = [ MediaObject( parts = [ 
                                                        PartObject( key = HTTPLiveStreamURL(url)) 
                                                        ] 
                                                     )
                                        ]
                                )
                )
        oc.add(DirectoryObject(title = 'Categories',
                               key = Callback(GetCategories),
                               summary = 'Browse programms by Category'))
        return oc

def GetCategories():
        oc = ObjectContainer()
        
        content = HTML.ElementFromURL(URL, errors='ignore', cacheTime=1800)
        categories = content.xpath("//li[@class='categories__item']/a")

        for category in categories:
                url = category.xpath("@href")[0]
                title = category.text
                oc.add(DirectoryObject(key=Callback(GetVideosInCategory, url=url), title=title))
        return oc

def GetVideosInCategory(url):
        oc = ObjectContainer()
        content = HTML.ElementFromURL(URL + url)
        programms = content.xpath("//div[@class='clip-tile']")

        for program in programms:
                title = program.xpath(".//h3[@class='clip-tile__title']")[0].text
                thumb = program.xpath("a/span/noscript/img/@src")[0]
                url = program.xpath("a[@class='clip-tile__link']/@href")[0]
                oc.add(VideoClipObject(title=title, thumb=thumb, url=URL+url))
                Log.Debug(title)
                Log.Debug(thumb)
        return oc

