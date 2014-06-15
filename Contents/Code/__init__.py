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
		prog_title = programme.xpath(".//h3[@class='clip-tile__title']/text()")[0].strip()
		prog_descs = programme.xpath(".//p[@class='clip-tile__text']")
		if len(prog_descs)>0:
			prog_desc = prog_descs[0].text
		else:
			prog_desc = ""
		prog_thumb = programme.xpath("a/span/noscript/img/@src")[0]
		prog_url = programme.xpath("a[@class='clip-tile__link']/@href")[0]
		oc.add(DirectoryObject(title = prog_title, thumb = prog_thumb, summary = prog_desc, 
		                        key = Callback(GetProgram, url = LL_URL + prog_url  )))

        return oc

def GetVideosByLetter(letter, url):
        oc = ObjectContainer(title2 = letter)

        content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)
        programmes = content.xpath("//div[@class='tv-programmes__item tv-programme']")
        for programme in programmes:
                prog_title = programme.xpath(".//h3[@class='tv-programme__title']")[0].text
                prog_desc = programme.xpath(".//p[@class='tv-programme__description']")[0].text
                prog_thumb = programme.xpath(".//span[@class='picture']/noscript/img/@src")[0]
                prog_url = programme.xpath(".//a[@class='tv-programme__link']/@href")[0]

                oc.add(DirectoryObject(title = prog_title, thumb = prog_thumb, summary = prog_desc,
                                       key = Callback(GetProgram, url = LL_URL + prog_url  )))
        return oc

def GetProgram(url, season = None):
        oc = ObjectContainer()
	series_info = []

	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)
	series = content.xpath("//div[contains(@class, 'js-series-content')]")
	if len(series)==0:
		prog_title = content.xpath("//span[@class='media-marquee-text__title-text']")[0].text
		prog_desc = content.xpath("//div[@class='media-marquee-text__info']")[0].text
		prog_thumb = content.xpath("//head/meta[@property='og:image']/@content")[0]
		oc.add(VideoClipObject(title = prog_title,
                                       summary = prog_desc,
				       thumb = prog_thumb,
                                       url = url))
	else:		
		if season is None:		
			seasons = content.xpath("//li[contains(@class, 'series-content-season')]")
			if len(seasons)>0:
				for season in seasons:
					data_season = season.get("data-season")
					season_title_label = season.xpath(".//span/text()")
					if len(season_title_label)>0:
						season_title = season_title_label[0]
					else:
						season_title = ""
					season_title = season_title+ season.xpath(".//div/text()")[1].strip()
					Log.Debug("season_title: %s"%season_title)
					oc.add(DirectoryObject(title = season_title,
		                                           key = Callback(GetProgram, url = url, season = data_season)))
				return oc
	
		data_api_url = series[0].get("data-api-url")
		brand = series[0].get("data-api-brand")
		info_url = LL_URL + data_api_url + "?brand=" + brand
		if not season is None:
			info_url = info_url + "&series=%s"%season		
		try:
			series_info = JSON.ObjectFromURL(info_url)
		except:
			Log.Debug("series info fetch failed")			

		if len(series_info)>0:
			for episode in series_info["Episodes"]:
				prog_title = episode["Title"]
				prog_desc = episode["Summary"]
				prog_url = episode["Url"]
				oc.add(VideoClipObject(title = prog_title,
                                       summary = prog_desc,
                                       url = LL_URL + prog_url))
		else:
			episodes = content.xpath("//li[contains(@class, 'episodes-carousel__item')]")
			for episode in episodes:
				prog_title = episode.xpath(".//h3[contains(@class, 'episodes-carousel__title')]")[0].text
				prog_desc = episode.xpath(".//p[contains(@class, 'episodes-carousel__text')]")[0].text
				prog_url = episode.xpath(".//a[contains(@class, 'episodes-carousel__link')]")[0].get("href")
				prog_thumb = episode.xpath(".//span[contains(@class, 'episodes-carousel__image')]/span/@data-src")[0]
				url = LL_URL + prog_url
				oc.add(VideoClipObject(title = prog_title,
                                       summary = prog_desc,
				       thumb = prog_thumb,
                                       url = LL_URL + prog_url))

	return oc

