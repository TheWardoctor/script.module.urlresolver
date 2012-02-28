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

import os
import random
import re
import urllib, urllib2

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import SiteAuth
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
import xbmc
import cookielib
from t0mm0.common.net import Net


class RealDebridResolver(Plugin, UrlResolver, SiteAuth, PluginSettings):
    implements = [UrlResolver, SiteAuth, PluginSettings]
    name = "realdebrid"
    profile_path = common.profile_path    
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)
    media_url = None
    allHosters = None

    def __init__(self):
        p = self.get_setting('priority') or 1
        self.priority = int(p)
        self.net = Net()
        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

    #UrlResolver methods
    def get_media_url(self, host, media_id):
        print 'in get_media_url %s' % media_id
        url = 'http://real-debrid.com/ajax/deb.php?lang=en&sl=1&link=%s' % media_id
        source = self.net.http_GET(url).content
        print '************* %s' % source
        if source == '<span id="generation-error">Your file is unavailable on the hoster.</span>':
            return None
        if re.search('This hoster is not included in our free offer', source):
            return None
        if re.search('No server is available for this hoster.', source):
            return None
        link =re.compile('ok"><a href="(.+?)"').findall(source)
        print 'link is %s' % link[0]
        self.media_url = link[0]
        return link[0]
        
    def get_url(self, host, media_id):
        return media_id
        
        
    def get_host_and_id(self, url):
        return 'www.real-debrid.com', url

    def get_all_hosters(self):
        if self.allHosters is None:
            url = 'http://real-debrid.com/lib/api/hosters.php'
            self.allHosters = self.net.http_GET(url).content
        return self.allHosters 

    def valid_url(self, url, host):
        print 'in valid_url %s : %s' % (url, host)
        tmp = re.compile('//(.+?)/').findall(url)
        print 'r is %s ' % tmp[0]
        domain = tmp[0].replace('www.', '')
        print 'domain is %s ' % domain
        print 'allHosters is %s ' % self.get_all_hosters()
        if re.search(domain, self.get_all_hosters()) is not None:
            print 'in if'
            return True
        else:
            print 'in else'
            return False

    def  checkLogin(self):
        url = 'http://real-debrid.com/lib/api/account.php'
        if not os.path.exists(self.cookie_file):
               return True
        source =  self.net.http_GET(url).content
        if re.search('expiration', source):
            return False
        else:
            return True
    
    #SiteAuth methods
    def login(self):
        if self.checkLogin(): 
            login_data = urllib.urlencode({'user' : self.get_setting('username'), 'pass' : self.get_setting('password')})
            url = 'https://real-debrid.com/ajax/login.php?' + login_data
            print url
            source = self.net.http_GET(url).content
            if re.search('OK', source):
                self.net.save_cookies(self.cookie_file)
                self.net.set_cookies(self.cookie_file)
                return True
            else:
                return False
        else:
            return True

    #PluginSettings methods
    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="RealDebridResolver_login" '
        xml += 'type="bool" label="login" default="false"/>\n'
        xml += '<setting id="RealDebridResolver_username" enable="eq(-1,true)" '
        xml += 'type="text" label="username" default=""/>\n'
        xml += '<setting id="RealDebridResolver_password" enable="eq(-2,true)" '
        xml += 'type="text" label="password" option="hidden" default=""/>\n'
        return xml
