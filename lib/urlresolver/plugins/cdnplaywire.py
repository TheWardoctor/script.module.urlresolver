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
import urlresolver
import xbmc
import os

#SET ERROR_LOGO# THANKS TO VOINAGE, BSTRDMKR, ELDORADO
error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')

class VideoweedResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "cdn.playwire.com"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        
        try:
            resp = self.net.http_GET(web_url)
            html = resp.content
            if html.find('File Not Found') >= 0:
                err_title = 'Content not available.'
                err_message = 'The requested video was not found.'
                common.addon.log_error(self.name + ' - fetching %s - %s - %s ' % (web_url,err_title,err_message))
                xbmc.executebuiltin('XBMC.Notification([B][COLOR white]'+__name__+'[/COLOR][/B] - '+err_title+',[COLOR red]'+err_message+'[/COLOR],8000,'+error_logo+')')
                return self.unresolvable(1, err_message)
        
            # get the video location
            r = re.search('mp4:(.+?)</src>',html)
            if r:
                videoId = r.group(1)
                r = re.search('(.+?)/embed/(.+?)',media_id)
                publisherId = r.group(1)
                return 'http://cdn.playwire.com/%s/%s' % (publisherId,videoId)

        except BaseException, e:        
            common.addon.log_error(self.name + ' - Exception: %s' % e)
            return self.unresolvable(code=0, msg='Exception: %s' % e)


    def get_url(self, host, media_id):
        return '%s/%s.xml' % (host,media_id)
        
        
    def get_host_and_id(self, url):
        #r = re.search('(http://(?:.+?))/(.+?)/embed/(.+?).js', url)
        r = re.search('(http://(?:.+?))/((?:.+?)/embed/(?:.+?)).js', url)
        if r:
            #return (r.group(1),(r.group(2),r.group(3)))
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http://cdn.playwire.com/(.+?)/embed/(.+?).js',url)

