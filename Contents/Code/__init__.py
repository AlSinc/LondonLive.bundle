TITLE = 'London Live'
PREFIX = '/video/londonlive'

LL_URL = 'http://www.londonlive.co.uk'
LL_URL_LIVE = LL_URL + '/tv'
LL_URL_A_TO_Z = LL_URL + '/schedule/letter/a'

def Start():
        Log.Debug('Start')


@handler(PREFIX, TITLE)
def Main():
        oc = ObjectContainer(title2 = 'London Live')
        
	content = HTML.ElementFromURL(LL_URL_LIVE, errors='ignore', cacheTime=1800)

        thumb = content.xpath('//video/@poster')
        if len(thumb)>0:
                thumb = thumb[0]
        else:
                thumb = ''
 
                oc.add(VideoClipObject(title = 'Live',
                                       summary = 'Live stream',
                                       thumb = thumb,
                                       url = LL_URL_LIVE))

        oc.add(DirectoryObject(title = 'Categories',
                               key = Callback(GetCategories),
                               summary = 'Browse programmes by Category'))

        oc.add(DirectoryObject(title = 'A to Z',
                               key = Callback(GetAtoZ),
                               summary = 'Browse programmes by A-Z'))
        return oc

def GetCategories():
        oc = ObjectContainer(title2 = 'Categories')
        
        content = HTML.ElementFromURL(LL_URL, errors='ignore', cacheTime=1800)
        categories = content.xpath("//li[@class='categories__item']/a")

        for category in categories:
                category_path = category.xpath("@href")[0]
                title = category.text
                oc.add(DirectoryObject(key=Callback(GetVideosInCategory, url=LL_URL + category_path), title=title))
        return oc

def GetAtoZ():
        oc = ObjectContainer(title2 = 'A to Z')

        content = HTML.ElementFromURL(LL_URL_A_TO_Z, errors='ignore', cacheTime=1800)
        letters = content.xpath("//div[@class='atoz-nav js-atoz-nav']/ul[@class='atoz-nav__list']/li[@class='atoz-nav__item']/a")
        Log.Debug('letters found: %d'%len(letters))
        for letter in letters:
                oc.add(DirectoryObject(title = letter.text,
                                       key = Callback(GetVideosByLetter, letter = letter.text, url = LL_URL + letter.get('href'))
                                      ))

        return oc

def GetVideosInCategory(url):
        oc = ObjectContainer()
        content = HTML.ElementFromURL(url)
        programmes = content.xpath("//div[@class='clip-tile']")

        for programme in programmes:
                playable = programme.xpath(".//a[@class='clip-tile__play']")
                if len(playable) > 0:
                        title = programme.xpath(".//h3[@class='clip-tile__title']")[0].text
                        thumb = programme.xpath("a/span/noscript/img/@src")[0]
                        desc = programme.xpath(".//p[@class='clip-tile__text']")[0].text
                        video_url = programme.xpath("a[@class='clip-tile__link']/@href")[0]
                        oc.add(VideoClipObject(title=title, thumb=thumb, 
                                               url=LL_URL+video_url,
                                               summary = desc))
                        Log.Debug(title)
                        Log.Debug(thumb)
        return oc

def GetVideosByLetter(letter, url):
        oc = ObjectContainer(title2 = letter)

        content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)
        programmes = content.xpath("//div[@class='tv-programmes__item tv-programme']")
        for programme in programmes:
                prog_url = programme.xpath(".//a[@class='tv-programme__link']/@href")[0]
                prog_title = programme.xpath(".//h3[@class='tv-programme__title']")[0].text
                prog_desc = programme.xpath(".//p[@class='tv-programme__description']")[0].text
                prog_thumb = programme.xpath(".//span[@class='picture']/noscript/img/@src")[0]

                oc.add(VideoClipObject(title = prog_title, thumb=prog_thumb,
                                               url = LL_URL + prog_url,
                                               summary = prog_desc))
        return oc

