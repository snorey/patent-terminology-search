class Query:
    
    def __init__(self, inputform):
        self.include_kr_compiled = ""
        self.exclude_kr_compiled = ""
        self.include_us_compiled = ""
        self.exclude_us_compiled = ""

class SearchResult:
    
    def __init__(self, query, us_num, us_title, kr_num, kr_title, kr_type=None):
        self.us_num = us_num
        self.us_link = "http://patft.uspto.gov/netacgi/nph-Parser?Sect2=PTO1&Sect2=HITOFF&p=1&u=/netahtml/PTO/search-bool.html&r=1&f=G&l=50&d=PALL&RefSrch=yes&Query=PN/" + us_num
        self.us_title = us_title
        self.kr_num = kr_num
        self.kr_type = kr_type
        self.kr_link = ""
        self.kr_title = kr_title
        self.us_localpath = "US/%s.html" % us_num
        self.kr_localpath = "KR/%s.html" % kr_num
        self.include_kr = None
        self.include_us = None
        
    def prepare_example_match(self):
        pass
        
    def prepare_frameset(self):
        highlighter = r'<span style="background-color: #FFFF00">\1</span>'
        kr_html = open(self.kr_localpath).read()
        us_html = open(self.us_localpath).read()
        if self.query.include_kr_compiled:
            kr_matches = re.sub(include_kr_compiled, highlighter)
            kr_html = kr_html.replace('style="background-color: #FFFF00">', 'style="background-color: #FFFF00" id="first-kr-match">')
        if self.query.include_us_compiled:
            us_matches = re.sub(include_us_compiled, highlighter)
            us_html = us_html.replace('style="background-color: #FFFF00">', 'style="background-color: #FFFF00" id="first-us-match">')
        

def print_single_result(result):
    uspatlink = 
    print '                    <li><a href="%s" target="blank">US patent: %s</a></li>' % (result.us_link, result.us_title)
    print '                    <li><a href="%s" target="blank">Korean patent: %s</a></li>' (result.kr_link, result.kr_title)
    print '                    <li>Example match: %s '
    print '                    <br/>(<a href="%s" target="blank">View</a>)'
    print '                    </li>'



def print_results(results):
    print '<html>'
    print '    <head>'
    print '        <title>Search results</title>'
    print '    </head>'
    print '    <body>'
    print '        <h1>Searched for %s</h1>'
    print '        <p>The following %d search results were found:</p>'
    print '        <ol>'
    print '            <li>'
    print '                <ul>'
    for r in results:
        print_single_result(r)
    print '                </ul>'
    print '            </li>'
    print '        </ol>'
    print '    </body>'
    print '</html>'
