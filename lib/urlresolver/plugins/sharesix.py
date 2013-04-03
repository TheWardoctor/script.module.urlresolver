'''
sharesix urlresolver plugin
Copyright (C) 2011 humla

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re
import urllib2
from urlresolver import common
import os, xbmcgui

class SharesixResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "sharesix"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        try:
           # Otherwise just use the original url to get the content. For sharesix
            html = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            raise Exception('Unable to establish connection with the website')
            return False


        # To build the streamable link, we need 
        # # the IPv4 addr (first 4 content below)
        # # the hash of the file
        metadata = re.compile('\|\|?(\d+)\|\|?(\d+)\|\|?(\d+)\|\|?(\d+)\|.+?video\|(.+?)\|\|?file').findall(html)

        if (len(metadata) > 0):
            metadata = metadata[0]
            stream_url="http://"+metadata[3]+"."+metadata[2]+"."+metadata[1]+"."+metadata[0]+"/d/"+ metadata[4]+"/video.flv"
            return stream_url
            
        if 'file you were looking for could not be found' in html:
            raise Exception("File has been removed.")
            return False

        raise Exception(' Error while retrieving playable link')
        return False

    def get_url(self, host, media_id):
        return 'http://%s/%s' % (host, media_id)
        
    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z/]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?sharesix.com/' +
                         '[0-9A-Za-z]+', url) or
                         'sharesix' in host)