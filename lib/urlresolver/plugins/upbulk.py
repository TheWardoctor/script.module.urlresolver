"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from t0mm0.common.net import Net
import urllib2
import urllib
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import xbmcgui

class VideoweedResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "upbulk.com"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        dialog = xbmcgui.Dialog()
        
        #grab stream details
        try:
            html = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            common.addon.log_error('upbulk: got http error %d fetching %s' %
                                    (e.code, web_url))
            return False
        
        r = re.search('<iframe.+?src=\'(http://www.dailymotion.com/embed/video/.+?)\?syndication',html, re.DOTALL)

        #use api to find stream address
        if r:
            api_call = r.group(1).replace("embed/", "")
        else:
            dialog.ok(' Videoweed ', ' The video no longer exists ', '', '')
            return False

        try:
            link = self.net.http_GET(api_call).content
        except urllib2.URLERROR, e:
            common.addon.log_error('upbulk: failed to call the video API: ' +
                                   'got http error %d fetching %s' %
                                                            (e.code, api_call))
            return False

        sequence = re.compile('"sequence":"(.+?)"').findall(link)
        newseqeunce = urllib.unquote(sequence[0]).decode('utf8').replace('\\/', '/')
        imgSrc = re.compile('og:image" content="(.+?)"').findall(link)
        if(len(imgSrc) == 0):
                imgSrc = re.compile('/jpeg" href="(.+?)"').findall(link)
        dm_low = re.compile('"sdURL":"(.+?)"').findall(newseqeunce)
        dm_high = re.compile('"hqURL":"(.+?)"').findall(newseqeunce)
        videoUrl = ''
        if(len(dm_high) == 0):
                videoUrl = dm_low[0]
        else:
                videoUrl = dm_high[0]
        return videoUrl

    def get_url(self, host, media_id):
        return 'http://www.upbulk.com/media/video.php?id=%s' % media_id
        
        
    def get_host_and_id(self, url):
        r = re.search('//(?:embed.)?(.+?)/media/(?:video.php\?id=)' + 
                      '([0-9a-z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        return re.match('http://(www.|embed.)?upbulk.(?:com)/media/(video.php\?id=)' +
                        '(?:[0-9a-z]+|width)', url) or 'upbulk' in host

