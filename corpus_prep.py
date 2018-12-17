# coding=utf-8

import collections
from cStringIO import StringIO
import datetime
import itertools
import os
import re

maindir = "."


def get_html_path(pdfpath):
    htmlpath = pdfpath.replace(".pdf",".html")
    return htmlpath


def convert_pdf_to_html(path, save=True):
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import HTMLConverter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFSyntaxError
    # works with PDFMiner version 20140328
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = "utf-8"
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, "rb")
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0 # use 0 to ensure all pages are processed
    caching = True
    pagenos=set()
    pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True)
    pagecount = 0
    try:
        for page in pages:
            pagecount += 1
            interpreter.process_page(page)
    except PDFSyntaxError:
        print "Invalid PDF", path
        fp.close()
        return
    fp.close()
    device.close()
    text = retstr.getvalue()
    retstr.close()
    if pagecount < 2:
        print "No content!", path
        return
    elif save:
        savepath = get_html_path(path)
        open(savepath,"w").write(text)
        return savepath
    else: 
        return text

    
def directory_to_html(directory, skip=True):
    existing_files = set([os.path.join(directory, x) for x in os.listdir(directory)])
    pdf_paths = [x for x in existing_files if x.lower().endswith(".pdf")]
    for path in pdf_paths:
        htmlpath = path.replace(".pdf",".html")
        if htmlpath in existing_files and skip is True:
            continue
        try:
            output = convert_pdf_to_html(path)
        except Exception, e:
            print str(e), path
            continue
        print(output)


def stem_KO(text):
    raw_stems = kosimple.stem_text(text, keep_sequence=True, hangul_only=True, hangul_out=True)
    return raw_stems


def stem_EN(text):
    doc = metapy.index.Document()
    doc.content(text.decode('utf-8'))
    tok = metapy.analyzers.ICUTokenizer()
    tok = metapy.analyzers.LowercaseFilter(tok)
    tok = metapy.analyzers.Porter2Filter(tok)
    tok.set_content(doc.content())
    exclude = ["<s>", "</s>"]
    raw_stems = [t for t in tok if t not in exclude]
    return raw_stems


def get_raw_stems(text, language="KO"):
    if language == "KO":
        raw_stems = stem_KO(text)
    elif language == "EN":
        raw_stems = stem_EN(text)
    else:
        raise NotImplementedError
    return raw_stems


def stem_and_index_directory(directory="KR", indexpath="KR.index", language=None):
    import textract
    from collections import Counter, defaultdict
    if directory.endswith("KR"):
        global kosimple
        import kosimple
        kosimple.setup() # need verb list for stemming
        language = "KO"
    elif language == "EN":
        global metapy
        import metapy
    htmls = [os.path.join(directory, x) for x in os.listdir(directory) if x.endswith("html")]
    raw_index = defaultdict(list)
    for html in htmls:
        print html
        textpath = html.replace(".html", ".txt")
        if os.path.exists(textpath):
            text = open(textpath).read()
        else:
            text = textract.process(html)
        text = text.split("(54)", 1)[-1] 
        # The first occurrence of "(54)" typically 
        # signifies the beginning of the patent text, 
        # so this excludes most bibliographic data.
        open(textpath, "w").write(text)
        raw_stems = get_raw_stems(text, language)
        tallies = Counter(raw_stems).most_common()
        print len(tallies)
        stems_out = ""
        valid_stems = set()
        for t in tallies:
            if not t[0].strip():
                continue
            if t[0].isdigit(): # numerals are unlikely to be helpful in identifying topical docs
                continue
            valid_stems.add(t[0])
            stems_out += t[0].encode("utf-8", "ignore") + "\t" + str(t[1]) + "\n"
        stempath = html.replace(".html",".stems")
        open(stempath, "w").write(stems_out)
        for stem in dict(tallies).keys():
            raw_index[stem].append(html)
        print len(raw_index)
    rawpath = indexpath
    raw_out = ""
    linecount = 0
    for stem in raw_index.keys():
        if len(raw_index[stem]) > 0.25 * len(htmls):
            print "Excluding", stem, len(raw_index[stem]) # over corpus of 1248 KR patents, this excludes approximately 570 high-frequency stems
            continue
        if len(raw_index[stem]) < 2:
            continue # over corpus of 1248 patents, this excludes approximately 60k out of 100k stems
        line = stem.encode("utf-8", "ignore") + "\t" + ", ".join(raw_index[stem]) + "\n"
        raw_out += line
        linecount += 1
    print linecount, "lines"
    open(rawpath, "w").write(raw_out)
    
        
def process_directory(directory, indexpath, language):
    directory_to_html(directory)
    stem_and_index_directory(directory, indexpath, language)


def doneyet(items, limit, total):
    done = False
    if len(items) >= total:
        print "True at 0"
        return True
    if limit is not False:
        if len(items) >= limit:
            print "True at 1"
            return True
    done = bool(len(items) % 50)
    if not done:
        if not items:
            print "True at 2"
            done = True 
    return done


def chunkify(page):
    items = []
    chunks = page.split("<TR>")[1:]
    catchme = "<TD valign=top><A  HREF="
    chunks = [x for x in chunks if catchme in x]
    for chunk in chunks:
        url = chunk.split(catchme,1)[1].split(">")[0]
        patnum = re.search(">([DRE\d\,]{5,15})<",chunk).group(1)
        patnum = patnum.replace(",","")
        if not patnum:
            print chunk
            continue
        title = chunk.split(url+">")[-1].split("<")[0]
        title = title.strip().replace("\n"," ").replace("  "," ")
        items.append((url,patnum,title))
    return items
    
    
def most_recent_tuesday(today=False):
    if today is False: 
        today = datetime.date.today()
    delta = datetime.timedelta(1)
    while today.weekday() != 1:
        today -= delta
    return today


def encode_unless(string):
    if type(string) == unicode:
        return string.encode('utf-8','ignore')
    elif type(string) == str:
        return string
    else:
        return str(string)


def extract_KR_abstract(htmlpath):
    text = open(htmlpath).read()
    text = text.split('<a name="2">')[0]
    detagged = re.sub("<.+?>","",text)
    title = detagged.split("(54)")[1].split("\n")[0]
    try:
        title = title.split("명칭")[1].strip()
    except IndexError:
        pass
    if "\n본" in detagged:
        abs = "본"+detagged.split("\n본")[1]
    return abs, title


def uspto_info(page):
    title = page.split('size="+1">')[1].split("\n")[0].strip()
    try:
        pagefornum = page.split("Foreign Application Priority Data")[1]
    except IndexError:
        pagefornum = page
    kornum = re.search("\d\d[-\s]\d{4}[-\s]\d+",pagefornum).group(0) # rarely shown with spaces instead of hyphens
    ipc = page.split("International Class:")[1].split("</TD>")[1].split(">")[1]
    attyfinder = ">Attorney, Agent or Firm:<"
    if attyfinder in page:
        atty = page.split(attyfinder)[1].split(">",1)[1].split("\n")[0].strip()
    else:
        atty = ""
    atty = re.sub("<.*?>","",atty)
    if ">Abstract<" in page:
        abstract = page.split(">Abstract<")[1]
        abstract = abstract.split("</p>")[0].split("</P>")[0]
        abstract = re.sub("<.+?>","",abstract).strip()
        if len(abstract) > 5000:
            abstract = abstract.split("\r\n\r\n")[0]
    else:
        abstract = ""
    try:
        corp = page.split("Applicant:")[1]
        corp = corp.split("<TR> <TD>")[1]
        corp = corp.split("</TD")[0]
    except IndexError, e:
        print e
        print page
        corp = page
    corp = re.sub("<.*?>","",corp).strip()
    inventors = page.split('Inventors:')[1].split('"90%">')[1].split("</TD")[0].strip()
    inventors = re.sub("<.*?>","",inventors)
    inventors = inventors.replace("\n",", ")
    grantdate = re.search("[A-Z][a-z]+ \d{1,2}, \d\d\d\d",page).group(0)
    allthestuff = (title,kornum,atty,inventors,corp,grantdate,abstract,ipc)
    return allthestuff

    
def search_items_for_field(fieldvalues,fieldnum=2,directory=".",suffix="-2.tsv",returnfield=False):
    if type(fieldvalues) == str:
        fieldvalues = [fieldvalues]
    fieldvalues = set(fieldvalues)
    filenames = os.listdir(directory)
    filenames = [os.path.join(directory,x) for x in filenames if x.endswith(suffix)]
    found = collections.defaultdict(list)
    print len(filenames)
    for path in filenames:
        items = load_from_tsv(path)
        items = [x for x in items if x[fieldnum] in fieldvalues]
        for i in items:
            if returnfield is False:
                found[i[fieldnum]].append(i)
            else:
                found[i[fieldnum]].append(i[returnfield])
    return found
    

def crude_concordance(searchterm, krdir="KR", usdir="US", limit=2, endat=10): # launch window with KR file containing term and corresponding US file
    import kosimple
    import webbrowser
    import time
    # first, get KR files containing term
    krfiles = kosimple.search(searchterm, endat=endat)
    krnums = [os.path.split(x)[-1].split(".")[0] for x in krfiles]
    krnums = [re.sub("(\d\d)(\d\d\d\d)(\d+)","\\1-\\2-\\3",x) for x in krnums]
    print len(krnums)
    usnums = search_items_for_field(fieldvalues=krnums, fieldnum=2, returnfield=0)
    realfiles = set(os.listdir(usdir))
    found = []
    for krnum, usnum in usnums.items():
        if type(usnum) == list:
            usnum = usnum[0]
        usnumpath = usnum+".html"
        if usnumpath not in realfiles:
            continue
        else:
            usnumpath = os.path.join(usdir,usnumpath)
        krnum = krnum.replace("-","")
        krnumpath = os.path.join(krdir,krnum+".html")
        found.append((usnumpath,krnumpath))
        if len(found) > limit:
            continue
        webbrowser.open(krnumpath)
        time.sleep(1)
        webbrowser.open(usnumpath)
        time.sleep(1)
    return found


def refresh_specs(directory="KR",overwrite=False):
    print str(overwrite)
    htmls = [x for x in os.listdir(directory) if x.endswith(".html")]
    htmls = [os.path.join(directory,x) for x in htmls]
    paths = set()
    if overwrite is False:
        done = set([os.path.join(directory,x).split("-")[0] for x in os.listdir(directory) if x.endswith("-spec.txt")])
        todo = [x for x in htmls if x.split(".")[0] not in done]
    else:
        todo = htmls
    for t in todo:
        if not todo.index(t) % 100:
            print todo.index(t), len(todo)
        path = get_spec(t)
        paths.add(path)
    return paths


def get_spec(htmlpath="",html="",save=True,savepath="",returnclaims=False):
    if save:
        sendback = False
        if not savepath:
            savepath = htmlpath.split(".")[0]+"-spec.txt"
    else:
        sendback = True
    if html:
        text = html
    else:
        text = open(htmlpath).read()
    findme1 = ">명세서"
    findme2 = ">명 세 서"
    probs = []
    if findme2 in text: # if present, definitely the heading, so put first
        spec = text.split(findme2,1)[1]
    elif findme1 in text:
        spec = text.split(findme1,1)[1]
    else:
        print "No spec!", htmlpath,len(text)
        return ""
    startlen = len(spec)
    startspec = str(spec)
    claimfinders = ["청구의","청구범","특허청구"]
    prefixes = [">",")","> ",") "]
    findthese = []
    for p in prefixes: # spool up various spacing possibilities
        newfinders = [p+x for x in claimfinders]
        findthese.extend(newfinders)
        newfinders = [p+(" ".join(list(x))) for x in claimfinders]
        findthese.extend(newfinders)
    found = [text.count(x) for x in findthese]
    counts = sum(found)
    claims = ""
    if counts == 0:
        print "No claims found for %s." % htmlpath
    elif counts > 1: # rare but annoying
        brevities = [(x,[y.split("\n")[0] for y in text.split(x)[1:]]) for x in findthese if x in text]
        for b in brevities: # whichever the real Claims header is, it will be the shortest
            b[1].sort()
        brevities = [(len(x[1][0].strip()),x[0],x[1][0]) for x in brevities]
        brevities.sort()
        the_one = brevities[0]
        findme = the_one[1]+the_one[2]
        if findme in spec:
            claims = spec.split(findme)[1]
            spec = spec.split(findme)[0]
    elif counts == 1:
        splitter = [x for x in findthese if found[findthese.index(x)]][0]
        spec = spec.split(splitter)[0]
        try:
            claims = spec.split(splitter,1)[1]
        except IndexError:
            pass
    if len(spec) < 0.5 * startlen: # claims within spec? If so, reverse.
        spec = startspec
        splitter = ">발명"
        if splitter not in spec:
            splitter = ">발 명"
        try:
            spec = spec.split(splitter,1)[1]
        except IndexError:
            print "We seem to have a problem at %s." % htmlpath
    # remove page numbers
    spec = re.sub("<.+?>-\s+\d+\s+-","",spec)
    spec = re.sub("<.+?>Page\s+\d+\s*<.+?>","",spec)
    spec = re.sub("<.+?>공개특허 \d\d-\d\d\d\d-\d+","",spec)
    spec = re.sub("<.+?>\[0\d{3}\]","",spec)
    # and now nuke all tags
    spec = re.sub("<.+?>","",spec)
    if savepath:
        open(savepath,"w").write(spec)
    if returnclaims:
        if claims:
            return spec,claims
        else:
            found = [text.find(x) for x in findthese if x in text]
            if found:
                found.sort()
                pos = found[0]
                endpos = text.find(">명")
                claimhtml = text[pos:endpos]
                claims = re.sub("<.+>","",claimhtml)
            return spec,claims
    else:
        if sendback:
            return spec
        else:
            return savepath


def consolidate_logs(directory=".", prefix="uspto-kr", suffix="-2.tsv"):
    data = []
    logs = [os.path.join(directory,x) for x in os.listdir(directory) if x.startswith(prefix) and x.endswith(suffix)]
    krfiles = [x for x in os.listdir(os.path.join(directory, "KR")) if x.endswith(".html")]
    krids = set([x.split(".")[0] for x in krfiles])
    for logpath in logs:
        print logpath
        logfile = open(logpath)
        for line in logfile:
            if line.strip():
                try:
                    usnum, ustitle, krnum, owner, date, usabstract, ipc = line.split("\t")
                except ValueError:
                    usnum, ustitle, krnum, agent, inventor, owner, date, usabstract, ipc = line.split("\t")
            krid = krnum.replace("-","")
            if krid not in krids:
                continue
            clean_ipc = [x.strip().replace("&nbsp"," ") for x in ipc.split(";")]
            joined_ipc = "; ".join(clean_ipc)
            data.append((usnum, krid, ustitle, "", usabstract, "", joined_ipc))
    krnums = [x[1] for x in data]
    import collections
    counts = collections.Counter(krnums)
    exclude = set()
    for krnum in counts.keys():
        if counts[krnum] > 1:
            exclude.add(krnum)
    data = [x for x in data if x[1] not in exclude]
    data.sort()
    return data


def move_files(src, dest, mapping_path="mappings.tsv", exclude=[".pdf"]): # move files and leave supernumerary files behind
    import shutil
    usdict = dict([(x.split("\t")[0],x) for x in open(mapping_path).read().split("\n")])
    krdict = dict([(x.split("\t")[1],x) for x in open(mapping_path).read().split("\n")])
    usids = set(usdict.keys())
    krids = set(krdict.keys())
    print list(usids)[:10]
    print list(krids)[:10]
    krdir_old = os.path.join(src, "KR")
    krdir_new = os.path.join(dest, "KR")
    usdir_old = os.path.join(src, "US")
    usdir_new = os.path.join(dest, "US")
    if not os.path.exists(krdir_new):
        os.mkdir(krdir_new)
    krfiles = os.listdir(krdir_old)
    print len(krfiles)
    for filename in krfiles:
        fileid = filename.split(".")[0]
        if any([(x in filename) for x in exclude]):
            continue
        if fileid not in krids:
            continue
        oldpath = os.path.join(krdir_old, filename)
        shutil.copy(oldpath, krdir_new)
    if not os.path.exists(usdir_new):
        os.mkdir(usdir_new)
    usfiles = [x for x in os.listdir(usdir_old) if not any([(y in x) for y in exclude])]
    for filename in usfiles:
        fileid = filename.split(".")[0]
        if any([(x in filename) for x in exclude]):
            continue
        if fileid not in usids:
            continue
        oldpath = os.path.join(usdir_old, filename)
        shutil.copy(oldpath, usdir_new)
