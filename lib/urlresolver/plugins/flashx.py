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

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2
from urlresolver import common
import os
import re
import xbmcgui

error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')


class FlashxResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "flashx"
    domains = ["flashx.tv"]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        self.pattern = 'http://((?:www.|play.)?flashx.tv)/(?:embed-)?([0-9a-zA-Z/-]+)(?:.html)?'
        self.headers = {'Referer': 'http://www.flashx.tv/',
                        'Host': 'www.flashx.tv'}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        smil = ''
        try:
            html = self.net.http_GET(web_url, headers=self.headers).content
            swfurl = 'http://static.flashx.tv/player6/jwplayer.flash.swf'
            r = re.search('"(http://.+?\.smil)"', html)
            if r: smil = r.group(1)
            else:
                r = re.search('\|smil\|(.+?)\|sources\|', html)
                if r: smil = 'http://flashx.tv/' + r.group(1) + '.smil'
            if smil:
                html = self.net.http_GET(smil, headers=self.headers).content
                r = re.search('<meta base="(rtmp://.*?flashx\.tv:[0-9]+/)(.+/)".*/>', html, re.DOTALL)
                if r:
                    rtmp = r.group(1)
                    app = r.group(2)
                    sources = re.compile('<video src="(.+?)" height="(.+?)" system-bitrate="(.+?)" width="(.+?)".*/>').findall(html)
                    vid_list = []
                    url_list = []
                    best = 0
                    quality = 0
                    if sources:
                        if len(sources) > 1:
                            for index, video in enumerate(sources):
                                if int(video[1]) > quality: best = index
                                quality = int(video[1])
                                vid_list.extend(['FlashX - %sp' % quality])
                                url_list.extend([video[0]])
                    if len(sources) == 1: vid_sel = sources[0][0]
                    else:
                        if self.get_setting('auto_pick') == 'true': vid_sel = url_list[best]
                        else:
                            result = xbmcgui.Dialog().select('Choose a link', vid_list)
                            if result != -1: vid_sel = url_list[result]
                            else: return self.unresolvable(0, 'No link selected')
                    if vid_sel: return '%s app=%s playpath=%s swfUrl=%s pageUrl=%s swfVfy=true' % (rtmp, app, vid_sel, swfurl, web_url)

            raise Exception("File Link Not Found")

        except urllib2.URLError, e:
            common.addon.log_error('flashx.tv: got http error %d fetching %s' % (e.reason, web_url))
            common.addon.show_small_popup('Error','flashx.tv: HTTP error: %s' % e, 5000, error_logo)
            return self.unresolvable(code=3, msg=e)
        
        except Exception, e:
            common.addon.log_error('flashx.tv: general error occured: %s' % e)
            common.addon.show_small_popup(title='[B][COLOR white]FLASHX.TV[/COLOR][/B]', msg='[COLOR red]%s[/COLOR]' % e, delay=5000, image=error_logo)
            return self.unresolvable(code=0, msg=e)

    def get_url(self, host, media_id):
        urlhash = re.search('([a-zA-Z0-9]+)(?:-+[0-9]+[xX]+[0-9]+)', media_id)
        if urlhash: media_id = urlhash.group(1)
        return 'http://flashx.tv/embed-%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r: return r.groups()
        else: return False

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (self.__class__.__name__)
        return xml