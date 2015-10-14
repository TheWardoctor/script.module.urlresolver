"""
    urlresolver XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

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

    Adapted for use in xbmc from:
    https://github.com/einars/js-beautify/blob/master/python/jsbeautifier/unpackers/packer.py
    
    usage:

    if detect(some_string):
        unpacked = unpack(some_string)


Unpacker for Dean Edward's p.a.c.k.e.r
"""

import re

def detect(source):
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    source = source.replace(' ', '')
    if re.search('eval\(function\(p,a,c,k,e,(?:r|d)', source): return True
    else: return False

def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError('Malformed p.a.c.k.e.r. symtab.')

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError('Unknown p.a.c.k.e.r. encoding.')

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word = match.group(0)
        return symtab[unbase(word)] or word

    source = re.sub(r'\b\w+\b', lookup, payload)
    return _replacestrings(source)

def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    argsregex = (r"}\('(.*)', *(\d+), *(\d+), *'(.*?)'\.split\('\|'\)")
    args = re.search(argsregex, source, re.DOTALL).groups()

    try:
        return args[0], args[3].split('|'), int(args[1]), int(args[2])
    except ValueError:
        raise UnpackingError('Corrupted p.a.c.k.e.r. data.')

def _replacestrings(source):
    """Strip string lookup table (list) and replace values in source."""
    match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = '%s[%%d]' % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return source


class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""
    ALPHABET = {
        62: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        95: (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
    }
    
    def __init__(self, base):
        self.base = base

        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            if base < 62:
                self.ALPHABET[base] = self.ALPHABET[62][0:base]
            elif 62 < base < 95:
                self.ALPHABET[base] = self.ALPHABET[95][0:base]
            # Build conversion dictionary cache
            try:
                print self.ALPHABET[base]
                self.dictionary = dict((cipher, index) for index, cipher in enumerate(self.ALPHABET[base]))
                print self.dictionary
            except KeyError:
                raise TypeError('Unsupported base encoding.')

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base ** index) * self.dictionary[cipher]
        return ret

class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""
    pass


if __name__ == "__main__":
    # test = '''eval(function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);return p}('4(\'30\').2z({2y:\'5://a.8.7/i/z/y/w.2x\',2w:{b:\'2v\',19:\'<p><u><2 d="20" c="#17">2u 19.</2></u><16/><u><2 d="18" c="#15">2t 2s 2r 2q.</2></u></p>\',2p:\'<p><u><2 d="20" c="#17">2o 2n b.</2></u><16/><u><2 d="18" c="#15">2m 2l 2k 2j.</2></u></p>\',},2i:\'2h\',2g:[{14:"11",b:"5://a.8.7/2f/13.12"},{14:"2e",b:"5://a.8.7/2d/13.12"},],2c:"11",2b:[{10:\'2a\',29:\'5://v.8.7/t-m/m.28\'},{10:\'27\'}],26:{\'25-3\':{\'24\':{\'23\':22,\'21\':\'5://a.8.7/i/z/y/\',\'1z\':\'w\',\'1y\':\'1x\'}}},s:\'5://v.8.7/t-m/s/1w.1v\',1u:"1t",1s:"1r",1q:\'1p\',1o:"1n",1m:"1l",1k:\'5\',1j:\'o\',});l e;l k=0;l 6=0;4().1i(9(x){f(6>0)k+=x.r-6;6=x.r;f(q!=0&&k>=q){6=-1;4().1h();4().1g(o);$(\'#1f\').j();$(\'h.g\').j()}});4().1e(9(x){6=-1});4().1d(9(x){n(x)});4().1c(9(){$(\'h.g\').j()});9 n(x){$(\'h.g\').1b();f(e)1a;e=1;}',36,109,'||font||jwplayer|http|p0102895|me|vidto|function|edge3|file|color|size|vvplay|if|video_ad|div||show|tt102895|var|player|doPlay|false||21600|position|skin|test||static|1y7okrqkv4ji||00020|01|type|360p|mp4|video|label|FFFFFF|br|FF0000||deleted|return|hide|onComplete|onPlay|onSeek|play_limit_box|setFullscreen|stop|onTime|dock|provider|391|height|650|width|over|controlbar|5110|duration|uniform|stretching|zip|stormtrooper|213|frequency|prefix||path|true|enabled|preview|timeslidertooltipplugin|plugins|html5|swf|src|flash|modes|hd_default|3bjhohfxpiqwws4phvqtsnolxocychumk274dsnkblz6sfgq6uz6zt77gxia|240p|3bjhohfxpiqwws4phvqtsnolxocychumk274dsnkba36sfgq6uzy3tv2oidq|hd|original|ratio|broken|is|link|Your|such|No|nofile|more|any|availabe|Not|File|OK|previw|jpg|image|setup|flvplayer'.split('|')))'''
    # test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('y.x(A(\'%0%f%b%9%1%d%8%8%o%e%B%c%0%e%d%0%f%w%1%7%3%2%p%d%1%n%2%1%c%0%t%0%f%7%8%8%d%5%6%1%7%e%b%l%7%1%2%e%9%q%c%0%6%1%z%2%0%f%b%1%9%c%0%s%6%6%l%G%4%4%5%5%5%k%b%7%5%8%o%i%2%k%6%i%4%2%3%p%2%n%4%5%7%6%9%s%4%j%q%a%h%a%3%a%E%a%3%D%H%9%K%C%I%m%r%g%h%L%v%g%u%F%r%g%3%J%3%j%3%m%h%4\'));',48,48,'22|72|65|6d|2f|77|74|61|6c|63|4e|73|3d|6f|6e|20|4d|32|76|59|2e|70|51|64|69|62|79|31|68|30|7a|34|66|write|document|75|unescape|67|4f|5a|57|55|3a|44|47|4a|78|49'.split('|'),0,{}))'''
    # test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('x.w(z(\'%1%f%9%b%0%d%7%7%m%e%A%c%1%e%d%1%f%v%0%3%i%2%o%d%0%s%2%0%c%1%q%1%f%3%7%7%d%6%5%0%3%e%9%l%3%0%2%e%b%g%c%1%5%0%y%2%1%f%9%0%b%c%1%r%5%5%l%E%4%4%6%6%6%n%9%3%6%7%m%k%2%n%5%k%4%2%i%o%2%s%4%6%3%5%b%r%4%8%D%h%C%a%F%8%H%B%I%h%i%a%g%8%u%a%q%j%t%j%g%8%t%h%p%j%p%a%G%4\'));',45,45,'72|22|65|61|2f|74|77|6c|5a|73|55|63|3d|6f|6e|20|79|59|6d|4d|76|70|69|2e|62|7a|30|68|64|44|54|66|write|document|75|unescape|67|51|32|6a|3a|35|5f|47|34'.split('|'),0,{}))'''
    # test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('q.r(s(\'%h%t%a%p%u%6%c%n%0%5%l%4%2%4%7%j%0%8%1%o%b%3%7%m%1%8%a%7%b%3%d%6%1%f%0%v%1%5%D%9%0%5%c%g%0%4%A%9%0%f%k%z%2%8%1%C%2%i%d%6%2%3%k%j%2%3%y%e%x%w%g%B%E%F%i%h%e\'));',42,42,'5a|4d|4f|54|6a|44|33|6b|57|7a|56|4e|68|55|3e|47|69|65|6d|32|45|46|31|6f|30|75|document|write|unescape|6e|62|6c|2f|3c|22|79|63|66|78|59|72|61'.split('|'),0,{}))'''
    test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('1I A(k){5 q="1T/+1S=";5 l,u,I,M,J,s,C,m,i=0,p=\'\';1P{M=q.w(k.t(i++));J=q.w(k.t(i++));s=q.w(k.t(i++));C=q.w(k.t(i++));m=M<<18|J<<12|s<<6|C;l=m>>16&F;u=m>>8&F;I=m&F;N(s==V)p+=G.H(l);X N(C==V)p+=G.H(l,u);X p+=G.H(l,u,I)}1M(i<k.1N);1L p}5 R="9/1R";5 Q="7://c.a.g/";5 U="1K/1Q/1B/1C/1A/1D/1J/1E/1H/y/1G/W/1F/1O/21/2j/2f/2h";5 11="2o/2i+2e==";5 Y="";5 S=4;5 P="2n";5 K=2g;N(S==4){K=2+8-15/3}5 E=Q+P+K+R+"2m.o";5 D=A(U);5 L=A(11);5 2l=A(Y);5 d=\'<1h 2k="r" 1U="2c:20-2d-22-1Z-1Y" 1k="1j" 1i="1g">\';d+=\'<B n="1V" z="7://c.a.g/c.o" />\';d+=\'<B n="1W" z="h" />\';d+=\'<B n="1m" z="1f" />\';d+=\'<B n="Z" z="13=7://c.a.g/O-1.o,\'+E+\'&b.T=\'+D+\'&e.10=7://j.a.f/c.1e&e.1u=v&e.14=1s-1q&e.1p=8&1n=7://c.a.g/1o.1t&1x=1z&1y=1v.f&1w=7://j.a.f&1r=h&b.1l=7://j.a.f/1c.1d&b.1b=r&b.1a=v&b.17=h&b.19=\'+L+\'" />\';d+=\'<d n="r" 1X="7://c.a.g/c.o" Z="13=7://c.a.g/O-1.o,\'+E+\'&b.T=\'+D+\'&e.10=7://j.a.f/c.1e&e.1u=v&e.14=1s-1q&e.1p=8&1n=7://c.a.g/1o.1t&1x=1z&1y=1v.f&1w=7://j.a.f&1r=h&b.1l=7://j.a.f/1c.1d&b.1b=r&b.1a=v&b.17=h&b.19=\'+L+\'" 23="24/x-2a-2b" 29="h" 1m="1f" 1k="1j" 1i="1g" /></1h>\';28.25("26").27=d;',62,149,'|||||var||http|||shush|proxy|player|embed|logo|se|tv|true||www|data|o1|bits|name|swf|enc|GtvnaF|flashplayer|h3|charAt|o2|false|indexOf|||value|fQSohVadGYm|param|h4|gZSsoeXVEdi|linkproxy|0xff|String|fromCharCode|o3|h2|jyt|cfg|h1|if|timeslidertooltipplugin|fgEAStrVJxUno|DvXdEnYalM|gio3|lwq|link|PUqxZnp|64||else|sb|FlashVars|file|po||plugins|position|||nocachexml||pluginslistname|reloader|embedid|loading|jpg|png|always|503|object|height|854|width|image|allowScriptAccess|skin|darksunset|margin|right|smoothing|bottom|zip|hide|Shush|aboutlink|volume|abouttext|100|WhWUjmtBg|tUt6tCMHWm5|GmfUW|WBoQWBght|t0Wma2Gmymq9DoqZlXtBOKWBt28mt0WBb08mMKt|GUMUG9ymq9WbWZM689t6tBDm8CM28|GmMXGUtKGUWhtCO28Blstmjm8Z8Q8Zz0qBO6GBtK8BNXtKjoqZbHtKNsGKt6W|tKtBO3G9MHGCG6tCMKWBb08mjoqZlP8ByhtBpmWBO68CO3GUMKqCOXqBG28ZN3W|function|5mt|lUo3lUadGKzXWBM689O6WZOHGByoqZDhW9DQqCG28ZNXtmN0G98hWZoht|return|while|length|8mWmQb8ZjQ8ZWhWBt2tBy|do|NPqZMKtKy|pro|r1dxnSA46s0KP3UH2XJcFREk|zgwZM59Lfy7eGWqYODTBNjCit8IvlpuVaohmbQ|classid|movie|allowFullScreen|src|444553540000|96B8|D27CDB6E|GBasWZl0WBbH8Ba3GUO6WZyQGZzHGm5|11cf|type|application|getElementById|playerload|innerHTML|document|allowfullscreen|shockwave|flash|clsid|AE6D|oSvz|8ZaH8|127|OXqCtU8Z8o8BDQ8ZyQ|N0e|GUy|id|sub|xy|ce9boreB|89jbNmpHN'.split('|'),0,{}))'''
    print unpack(test)
