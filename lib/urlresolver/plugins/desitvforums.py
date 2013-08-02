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
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import xbmcgui

class DesitvforumsResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "desitvforums.net"

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
            common.addon.log_error('desitvforums: got http error %d fetching %s' %
                                    (e.code, web_url))
            return False
        
        # there can be 2 sources either
        regex_1 = 'http://embed.(?:videoweed|nowvideo).(?:.+?)/embed.php\?v=[0-9a-z]+'
        #regex_2 = 'http://www.dailymotion.com/embed/video/xuowet_chakarwyuh-2012-dvd-scr-watch-online-by-desitvforum-net-part1_shortfilms?syndication=109150'
        regex_2 = 'http://www.dailymotion.com/embed/video/(?:.+?)\?syndication=[0-9a-z]+'

        r = re.search(regex_1, html, re.DOTALL)
    
        if r is None:
            r = re.search(regex_2, html, re.DOTALL)

        if r:
            web_url = r.group()
            try:
                html = self.net.http_GET(str(web_url)).content
            except urllib2.URLError, e:
                common.addon.log_error('desitvforums: got http error %d fetching %s' %
                                    (e.code, web_url))
                return False
        else:
            return False

        r = re.search('flashvars.domain="(.+?)".*flashvars.file="(.+?)".*' + 
                      'flashvars.filekey="(.+?)"', html, re.DOTALL)
        
        #use api to find stream address
        if r:
            domain, fileid, filekey = r.groups()
            api_call = ('%s/api/player.api.php?user=undefined&codes=1&file=%s' +
                        '&pass=undefined&key=%s') % (domain, fileid, filekey)
        else:
            dialog.ok(' desitvforums ', ' The video no longer exists ', '', '')
            return False

        try:
            api_html = self.net.http_GET(api_call).content
        except urllib2.URLERROR, e:
            common.addon.log_error('desitvforums: failed to call the video API: ' +
                                   'got http error %d fetching %s' %
                                                            (e.code, api_call))
            return False

        rapi = re.search('url=(.+?)&title=', api_html)
        if rapi:
            stream_url = rapi.group(1)
        else:
            common.addon.log_error('desitvforums: stream url not found')

        return stream_url


    def get_url(self, host, media_id):
        #return 'http://www.desitvforums.net/video.php?id=%s' % media_id
        return host + media_id
        
        
    def get_host_and_id(self, url):
        r = re.search('(http://www.(?:desitvforums.net|upbulk.com)/(?:media/video|video|media/dtfdownload).php\?id=)([0-9a-z]+)',url)
        #r = re.search('//(.+?)/(?:media/video.php\?id=|video.php\?id=|media/dtfdownload.php\?id=)' + 
        #              '([0-9a-z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        #return re.match('http://www.desitvforums.net/(media/video|video|media/dtfdownload).php\?id=' +
        #                '(?:[0-9a-z]+|width)', url) or 'desitvforums' in host
        return re.match('http://www.(?:desitvforums.net|upbulk.com)/(?:media/video|video|media/dtfdownload).php\?id=' +
                        '(?:[0-9a-z]+|width)', url) or 'desitvforums' in host

