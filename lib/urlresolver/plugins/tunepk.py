'''
tunepk urlresolver plugin
Copyright (C) 2013 icharania

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

import re
import urllib2
import urllib

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common


class TunePkResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "tune.pk"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net(user_agent='Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5')

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        try:
            link = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            return self.unresolvable(3, str(e))

        vfiles = re.compile("(?:hq_video_file|normal_video_file)\s+\=\s+\'([\w\.\/\:\?\=]+)\'").findall(link)
        return vfiles[0]

    def get_url(self, host, media_id):
        return 'http://embed.tune.pk/play/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/player/embed_player\.php\?vid\=(\w+)', url)
        return r.groups()

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http://(www\.)?tune.pk/player/embed_player\.php\?vid\=(\w+)', url) or \
               self.name in host