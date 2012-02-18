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
        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

    def GetURL(self, url):
    #print 'processing url: '+url

    # use cookie, if logged in.
        if self.cookie_file is not None and os.path.exists(self.cookie_file):
            cj = cookielib.LWPCookieJar()
            cj.load(self.cookie_file)
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')   
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            response = opener.open(req)

            #check if we might have been redirected (megapremium Direct Downloads...)
            finalurl = response.geturl()

            #if we weren't redirected, return the page source
            if finalurl is url:
                link=response.read()
                response.close()
                return link

            #if we have been redirected, return the redirect url
            elif finalurl is not url:               
                return finalurl
    

    #UrlResolver methods
    def get_media_url(self, host, media_id):
        print 'in get_media_url %s' % media_id
        url = 'http://real-debrid.com/ajax/deb.php?lang=en&sl=1&link=%s' % media_id
        source = self.GetURL(url)
        print '************* %s' % source
        if source == '<span id="generation-error">Your file is unavailable on the hoster.</span>':
            return None
        if re.search('This hoster is not included in our free offer', source):
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
            self.allHosters = self.GetURL(url)
        return self.allHosters 

    def valid_url(self, url, host):
        print 'in valid_url %s : %s' % (url, host)
        tmp = re.compile('//(.+?)/').findall(url)
        print 'r is %s ' % tmp[0]
        domain = tmp[0].replace('www.', '')
        print 'domain is %s ' % domain
        if re.search(domain, self.get_all_hosters()) is not None:
            return True
        else:
            return False

    def  checkLogin(self):
        url = 'http://real-debrid.com/lib/api/account.php'
        source = self.GetURL(url)
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
            source = self.GetURL(url)
            if re.search('OK', source):
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
