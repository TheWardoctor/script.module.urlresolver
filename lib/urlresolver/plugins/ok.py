"""
OK urlresolver XBMC Addon
Copyright (C) 2016 Seberoth

Version 0.0.1

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
"""
import re
import json
import os
import time
import xbmcgui
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common

class OKResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "ok.ru"
    domains = ["ok.ru", "www.ok.ru"]
    profile_path = common.profile_path
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)
    id_file = os.path.join(profile_path, '%s.id' % name)
    useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"
    header = {"User-Agent":useragent}

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        self.pattern = '//((?:www\.)?ok\.ru)/(?:videoembed|video)/(.+)'
        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

    def get_media_url(self, host, media_id):
        vids = self.__get_Metadata(media_id)

        purged_jsonvars = {}
        lines = []
        best = '0'

        for entry in vids['urls']:
            quality = self.__replaceQuality(entry['name'])
            lines.append(quality)
            if vids['vdtkn'] is not None:
                purged_jsonvars[quality] = entry['url'] + "&vdsig=" + vids['vtkn'] + "|User-Agent=" + self.useragent + "&Cookie=vdtkn%3D" + vids['vdtkn']
            else:
                purged_jsonvars[quality] = entry['url'] + "&vdsig=" + vids['vtkn'] + "|User-Agent=" + self.useragent
            if int(quality) > int(best): best = quality

        if vids['vdtkn'] is not None:
            if vids['vdtkn'][0] == '^':
                vids['vdtkn'] = vids['vdtkn'][1:]

        if len(lines) == 1:
            return purged_jsonvars[lines[0]].encode('utf-8')
        else:
            if self.get_setting('auto_pick') == 'true':
                return purged_jsonvars[str(best)].encode('utf-8')
            else:
                result = xbmcgui.Dialog().select('Choose the link', lines)

        if result != -1:
            return purged_jsonvars[lines[result]].encode('utf-8')
        else:
            raise UrlResolver.ResolverError('No link selected')

        raise UrlResolver.ResolverError('No video found')

    def __replaceQuality(self, qual):
        if qual == "full":
            return "1080"
        if qual == "hd":
            return "720"
        if qual == "sd":
            return "480"
        if qual == "low":
            return "360"
        if qual == "lowest":
            return "240"
        if qual == "mobile":
            return "144"
        common.addon.log_debug('Unknown quality: %s' % (qual))
        return "000"

    def __get_Metadata(self, media_id):
        url = "http://www.ok.ru/dk?cmd=videoPlayerMetadata&mid=" + media_id
        html = self.net.http_GET(url, headers=self.header).content
        json_data = json.loads(html)
        info = self.__get_vdsig(json_data['security']['url'])
        info['urls'] = []
        for entry in json_data['videos']:
            info['urls'].append(entry)
        return info

    def __get_vdsig(self, url):
        info = dict()

        vdsig = self.__loadSig()

        if vdsig is not None:
            info['vtkn'] = vdsig
            info['vdtkn'] = None
        else:
            params = dict()
            params[''] = ""
            response = self.net.http_POST(url, params, headers=self.header)
            cookies = self.net.get_cookies()
            html = response.content
            json_data = json.loads(html)
            self.__saveSig(json_data['vtkn'], cookies['.mycdn.me']['/']['vdtkn'].expires)
            info['vtkn'] = json_data['vtkn']
            info['vdtkn'] = cookies['.mycdn.me']['/']['vdtkn'].value

        return info

    def __loadSig(self):
        try:
            f = open(self.id_file, 'r')
            data = f.read()
            f.close()

            info = data.split(";")

            if (float(info[1]) <= time.time()):
                return
            else:
                return info[0]
        except:
            return

    def __saveSig(self, vdsig, expires):
        try:
            data = vdsig + ";" + str(expires)
            f = open(self.id_file, 'w')
            f.write(data)
            f.close()
            return True
        except:
            return False

    def get_url(self, host, media_id):
        return 'http://%s/videoembed/%s' % (host, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false':
            return False
        return re.search(self.pattern, url)

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (self.__class__.__name__)
        return xml