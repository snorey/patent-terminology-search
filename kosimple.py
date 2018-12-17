# -*- coding: utf-8 -*-

import os
import re
from htmlentitydefs import name2codepoint
from string import punctuation as punct

workingdir = "."
verbfilepath=os.path.join(workingdir, "koverbs.txt")
global verbage
global verbdic

try:
    print len(verbage)
except NameError:
    print "resetting verbage..."
    verbage = set()
moreverbs=[]

class Syllable:
    vowels=["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
    initials=["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "#", "j", "jj", "ch", "k", "t", "p", "h"]
    finals=["#", "g", "kk", "ks", "n", "nj", "nh", "d", "l", "lk", "lm", "lb", "ls", "lt", "lp", "lh", "m", "b", "bs", "s", "ss", "ng", "j", "ch", "k", "t", "p", "h"]
    raw=""
    def __init__(self, text):
        self.raw=text
        if type(text) == str:
            try: text=unicode(text, "utf-8")
            except UnicodeDecodeError: text=unicode(text, "cp949")
        text = text.strip()
        self.text=text
        if len(text) != 1:
            raise LengthError
        self.number=ord(text)
        if self.number < 44032 or self.number > 55203: 
#            print self.number
#            raise TypeError
            self.rom=""
        else:
            self.number -= 44032
            self.consonumber = int(self.number/588)
            self.endnumber = self.number % 28
            self.vowelnumber = int((self.number % 588)/28)
            self.rom = ".".join([self.initials[self.consonumber], self.vowels[self.vowelnumber], self.finals[self.endnumber]])
    
    def __str__(self):
        return self.rom
        
        
class LengthError(Exception):
    def __init__(self):
        print "Syllable is too short or too long!"
        
        
class koWord:
    def __init__(self, text):
        self.syllables = []
        self.stemmed = ""
        self.aporiai = []
        self.raw = text
        if type(text) == str:
            try: text=unicode(text, "utf-8")
            except UnicodeDecodeError: text=unicode(text, "cp949")
        text = text.strip()
        self.text = text
        self.hangul = -1
        for t in text:
            if ord(t) < 44032 or ord(t) > 55203:
                self.hangul=self.hangul * 2
                self.syllables.append((0, t))
            else:
                self.hangul=abs(self.hangul)
                self.syllables.append((1, Syllable(t)))
        if self.hangul % 2: #if still odd, no non-Kore script chars
            self.hangul=True
            self.mixed=False
        elif self.hangul > 0: #non-Kore script chars, but also Kore
            self.hangul=True
            self.mixed=True
        else:
            self.hangul=False
            self.mixed=False
        self.rom=self.romanize()

    def __len__(self):
            return len(self.syllables)
            
    def process(self, noun=[], firstpass=True, restrict=False, thisform=""):
        if not self.hangul: 
            try:
                print "not hangul", self.text.encode('utf-8')[:100]
            except:
                pass
            return self.text
        self.rom = self.romanize()
        if not thisform: thisform=self.rom
        global verbdic
        global verbs
        try:
            if not self.syllables[-1][0]: 
                return self.text
        except IndexError:
            return self.text
        self.notdone=False
        afterparticles=""
        if len(self.syllables) > 1:
            if thisform.endswith("#---r.eu.l") and firstpass: #object
                if thisform[:-2] not in verbs: # .. .
                    self.stemmed = thisform[:-9]
                else:
                    self.stemmed = thisform[:-1]+"#---d.a.#"
            elif thisform.endswith("---#.eu.l") and firstpass:
                    if not thisform.endswith("#---#.eu.l"):
                        self.stemmed=self.rom[:-9]
            elif thisform.endswith("#---g.a.#"): #subject
                if thisform.endswith("---d.a.#---g.a.#"):
                    self.stemmed=self.rom[:-16]+"---d.a.#"
                else:
                    self.stemmed=self.rom[:-8]
            elif thisform.endswith("---#.i.#"):
                if not thisform.endswith("#---#.i.#"):
                        self.stemmed = thisform[:-8]
            elif thisform.endswith("#---n.eu.n") and firstpass: #topic
                if thisform[:-9] not in verbs and thisform[:-10]+"l" not in verbs and firstpass:
                    self.stemmed = thisform[:-9]
                elif thisform[:-9] in verbs:
                    self.stemmed = thisform[:-9]
                elif thisform[:-10]+"l" in verbs:
                    self.stemmed = thisform[:-10]+"l"
            elif thisform.endswith("---#.eu.n") and firstpass:
                if not thisform.endswith("#---#.eu.n"):
                        self.stemmed = thisform[:-9]
                        self.notdone=True
            elif thisform.endswith("---r.o.#"): 
                self.stemmed=self.rom[:-8]
                if thisform.endswith("---#.eu.#---r.o.#"):
                    if not thisform.endswith("#---#.eu.#---r.o.#"):
                            self.stemmed = thisform[:-17]
            elif thisform.endswith("#---r.o.#---s.eo.#"):
                self.stemmed = thisform[:-17]
                if thisform.endswith("---#.eu.#---r.o.#---s.eo.#"):
                    if not thisform.endswith("#---#.eu.#---r.o.#---s.eo.#"):
                            self.stemmed = thisform[:-26]
            elif thisform.endswith("#---r.o.#---ss.eo.#"): 
                self.stemmed = thisform[:-18]
                if thisform.endswith("---#.eu.#---r.o.#---ss.eo.#"):
                    if not thisform.endswith("#---#.eu.#---r.o.#---ss.eo.#"):
                            self.stemmed = thisform[:-27]
            elif thisform.endswith("---#.e.#"):
                self.stemmed = thisform[:-8]
            elif thisform.endswith("---#.e.#---g.e.#"):
                self.stemmed = thisform[:-16]
            elif thisform.endswith("---kk.e.#"):
                self.stemmed = thisform[:-9]
            elif thisform.endswith("---#.e.#---s.eo.#"):
                self.stemmed = thisform[:-17]
            elif thisform.endswith("---kk.e.#---s.eo.#"):
                self.stemmed = thisform[:-18]
            elif thisform.endswith("---kk.a.#---j.i.#"):
                self.stemmed = thisform[:-17]
            elif thisform.endswith("---b.u.#---t.eo.#"):
                self.stemmed = thisform[:-17]
            elif thisform.endswith("---#.ui.#") and firstpass:
                self.stemmed = thisform[:-9]
            elif thisform.endswith("---d.eu.l"):
                self.stemmed = thisform[:-9]
            elif thisform.endswith("---#.i.n"):
                self.stemmed = thisform[:-8]
            elif thisform.endswith("#---#.wa.#"):
                self.stemmed = thisform[:-9]
            elif thisform.endswith("---g.wa.#") and not thisform.endswith("#---g.wa.#"):
                    self.stemmed=self.rom[:-9]
            elif thisform.endswith("---d.o.#"):
                self.stemmed = thisform[:-8]
            elif thisform.endswith("---m.a.n"):
                self.stemmed = thisform[:-8]
            elif thisform.endswith("---ch.eo.#---r.eo.m"):
                self.stemmed = thisform[:-19]
            elif thisform.endswith("---m.a.l---#.ya.#"):
                self.stemmed = thisform[:-17]
            afterparticles = self.stemmed
            if afterparticles != thisform:
                nounish = True
            else:
                nounish = False
            if self.stemmed.endswith("d.oe.#"): #cleanup
                self.stemmed=self.stemmed[:-9]
            elif not nounish:
                if self.stemmed:
                    self.stemmed = suggestoverb(self.stemmed)
                else:
                    self.stemmed = suggestoverb(thisform)
            else:
                thelist = ["---g.i.#", "m"]
                self.stemmed = suggestoverb(thisform, thelist=thelist)
        if not self.stemmed: 
            self.stemmed=self.rom
        if self.stemmed in verbs:
            if not self.stemmed == afterparticles or not len(self.stemmed.split("---")) < 2:
                self.stemmed=verbs[self.stemmed]
        elif self.stemmed.endswith("#.i.#---d.a.#") and len(self.stemmed) > 16: # assuming not a verb in its own right, attached copula
            self.stemmed=self.stemmed[:-16]
        if firstpass and self.stemmed != self.rom:
            self.process(firstpass=False, thisform=self.stemmed, restrict=restrict)
            after_one = str(self.stemmed)
        self.inflections=set([self.rom, self.stemmed])
        return self.stemmed
        
    def romanize(self):
        try:
            output="---".join([str(Syllable(x)) for x in self.mainform])
        except TypeError:
            return ""
        except LengthError:
            return ""
        return output


def romanize(word):
        if type(word) != unicode: 
            word = unicode(word, "utf-8", "ignore")
        word = word.strip()
        output = "---".join([str(Syllable(x)) for x in word])
        return output


def stem_alt(text):
        from string import punctuation
        for p in punctuation: text=text.replace(p, " ")
        if type(text) == str:
            try: text=unicode(text, "utf-8")
            except UnicodeDecodeError: text=unicode(text, "cp949")
        rawwords=[x for x in re.split("[\s\r\n\t]+", text) if x.strip()]
        print len(rawwords)
        words = set()
        for w in rawwords:
            words.add(koWord(w))
        print len(words)
        stems=[(x, x.process()) for x in words]
        print len(stems)
        stems=[x for x in stems if x[0]]
        return stems


def stem_text(text, vocab=set(), callme=False, 
keep_sequence=False, hangul_out=False, hangul_only=False): 
    if type(text) != unicode:
        text = text.decode('utf-8', 'ignore')
    words = text2words(text)
    vocab = set(words)
    lemmata = dict([(x, x) for x in vocab])
    sequenced = []
#    print len(lemmata)
    todo = words
    k = 0
    for t in todo:
        if callme is not False: # callback function for progress meter
            callme(k, len(todo))
            k += 1
        lemma = process_word(t, vocab)
        if type(lemma) != unicode:
            lemma = lemma.decode('utf-8', "ignore")
        vocab.add(lemma)
        if keep_sequence:
            sequenced.append(lemma)
        else:
            lemmata[t] = lemma
    if keep_sequence:
        if hangul_out:
            final = [hangulize(x, hangul_only=hangul_only) for x in sequenced]
            final = [x for x in final if x.strip()]
            return final
        else: 
            return sequenced
    else:
        lemmata_processed = set(lemmata.values())
        if hangul_out:
            return set([hangulize(x, hangul_only=hangul_only) for x in lemmata_processed])
        else:
            return lemmata_processed


def text2words(text):
    rawwords=[]
    splitter="[%s]+" % (re.escape(punct)+"\r\n\t\s")
    splat = re.split(splitter, text)
    for x in splat:
        if not x.strip(): continue
        try:
            rawwords.append(romanize(x))
        except TypeError:
            continue
        except LengthError:
            continue
    return rawwords


def get_sentences(text):
    if type(text) != unicode:
        text = text.decode("utf-8", "ignore")
    enders=[u". ", u"? ", u"! ", u'." ']
    for e in enders:
        text = text.replace(e, e+u"|||")
    sentences = text.split(u"|||")
    sentences=[x.strip() for x in sentences]
    sentences=[x for x in sentences if x]
    return sentences


def frequentize(text, vocab=set()):
    freqs={}
    words = text2words(text)
    lemmata = stem(text, vocab=vocab)
    for w in set(words):
        lemma = lemmata[w]
        if lemma in freqs.keys():
            freqs[lemma]+=words.count(w)
        else:
            freqs[lemma]=words.count(w)
    return freqs


def unescape(text): 
#From code by Fredrik Lundh at http://effbot.org/zone/re-sub.htm#-html
# Licensed to the public domain at http://effbot.org/zone/copyright.htm
# Seems to work better than BeautifulSoup for this purpose
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            try:
                text = unichr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("\&\#?\w+\;", fixup, text)


def romanize(word):
    if type(word) != unicode: word=unicode(word, "utf-8", "ignore")
    word = word.strip()
    syllables=[Syllable(x) for x in word if x.strip()]
    syllables=[str(x) for x in syllables if x.rom]
    output="---".join(syllables)
    if re.match("\w+", word) and not syllables:
        output = word.encode("utf-8", "ignore")
    return output


def romanize_jamo(word): # For inputs in Unicode jamo rather than syllabic blocks
    initials=["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "#", "j", "jj", "ch", "k", "t", "p", "h"]
    vowels=["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
    finals=["g", "kk", "ks", "n", "nj", "nh", "d", "l", "lk", "lm", "lb", "ls", "lt", "lp", "lh", "m", "b", "bs", "s", "ss", "ng", "j", "ch", "k", "t", "p", "h"]
    if type(word) != unicode: word=unicode(word, "utf-8", "ignore")
    word = word.strip()
    chars = list(word)
    syllables=[]
    currentsyll=""
    for c in chars:
        codepoint = ord(c)
        if 4351 < codepoint < 4371:
            rom = initials[codepoint-4352]
            if currentsyll.endswith("."): # ended in jungseong?
                syllables.append(currentsyll+"#")
            currentsyll = rom+"."
        elif 4448 < codepoint < 4470:
            rom = vowels[codepoint-4449]
            currentsyll += rom+"."
        elif 4519 < codepoint < 4547:
            rom = finals[codepoint-4520]
            currentsyll += rom
            syllables.append(currentsyll)
        else:
            break
    if syllables:
        if currentsyll != syllables[-1]:
            if currentsyll.endswith("."): # ended in jungseong?
                syllables.append(currentsyll+"#")
            else:
                syllables.append(currentsyll)
    return "---".join(syllables)


def get_verb_forms(romstem, romverb):
    forms=[romstem]
    polite=""
    polite1="" #unkludge this
    if not romstem.endswith("#"): # consonant
        extra = romstem+"---#.eu.#"
        forms.append(extra)
        if romstem.endswith(".s"):
            alt = romstem[:-1]+"#---#.eu.#"
            forms.append(alt)
        elif romstem.endswith(".p"):
            alt = romstem[:-1]+"#---#.u.#"
            forms.append(alt)
            polite = romstem[:-1]+"#---#.wo.#"
            forms.append(polite)
        elif romstem.endswith(".d"):
            alt = romstem[:-1]+"r"
            forms.append(alt)
            themevowel = romstem[-3]
            polite = romstem[:-1]+"r---#.%s.#" % themevowel
            forms.append(polite)
    elif romstem.endswith(".i.#"):
        polite1 = romstem+"#.eo.#"
        polite2 = romstem[:-3]+"yeo.#"
        forms.append(polite1)
        forms.append(polite2)
    elif romstem.endswith(".u.#"):
        polite1 = romstem+"---#.eo.#"
        polite2 = romstem[:-3]+"wo.#"
        forms.append(polite1)
        forms.append(polite2)
    elif romstem.endswith("h.a.#"):
        polite1 = romstem+"---#.yeo.#"
        polite2 = romstem[:-3]+"ae.#"
        forms.append(polite1)
        forms.append(polite2)
    elif romstem.endswith("d.oe.#"):
        polite1 = romstem+"---#.eo.#"
        polite2 = romstem[:-4]+"wae.#"
        forms.append(polite1)
        forms.append(polite2)
    elif romstem.endswith(".e.#") or romstem.endswith(".ae.#"):
        forms.append(romstem+"---#.eo.#")
    elif romstem.endswith(".l"):
        forms.append(romstem[:-1]+"#")
    elif romstem.endswith("#---r.eu.#"):
        polite = romstem.replace("#---r.eu.#", "l---r.a.#")
        forms.append(polite)
    if not romstem.endswith("#"):
        themevowel = romstem.split(".")[-2]
        if themevowel in ["a", "ya", "o", "yo", "wa"]:
            polite = romstem+"---#.a.#"
        else:
            polite = romstem+"---#.eo.#"
        forms.append(polite)
    if romstem.endswith(".o.#"):
        polite = romstem[:-3]+"wa.#"
        forms.append(polite)
    if polite:
        past = polite[:-1]+"ss"
        forms.append(past)
    elif polite1:
        past1 = polite1[:-1]+"ss"
        past2 = polite2[:-1]+"ss"
        forms.append(past1)
        forms.append(past2)
    else: # polite = mainform
        past = romstem[:-1]+"ss"
        forms.append(past)
    forms = set(forms)
    return forms


def process_verb(romstem, romverb, romverbs=set()):
    polite1=""
    polite2=""
    polite=""
    global verbage
    verbage.add((romstem, romverb)) #have to use set of tuples, not dict, to guard against overlaps
    if not romstem.endswith("#"): # consonant
        extra = romstem+"---#.eu.#"
        verbage.add((extra, romverb))
        if romstem.endswith(".s"):
            alt = romstem[:-1]+"#---#.eu.#"
            verbage.add((alt, romverb))
        elif romstem.endswith(".p"):
            alt = romstem[:-1]+"#---#.u.#"
            verbage.add((alt, romverb))
            polite = romstem[:-1]+"#---#.wo.#"
            verbage.add((polite, romverb))
        elif romstem.endswith(".d"):
            alt = romstem[:-1]+"r"
            verbage.add((alt, romverb))
            themevowel = romstem[-3]
            polite = romstem[:-1]+"r---#.%s.#" % themevowel
            verbage.add((polite, romverb))
    elif romstem.endswith(".i.#"):
        polite1 = romstem+"#.eo.#"
        polite2 = romstem[:-3]+"yeo.#"
        verbage|=set([(polite1, romverb), (polite2, romverb)])
    elif romstem.endswith(".u.#"):
        polite1 = romstem+"---#.eo.#"
        polite2 = romstem[:-3]+"wo.#"
        verbage |= set([(polite1, romverb), (polite2, romverb)])
    elif romstem.endswith("h.a.#"):
        polite1 = romstem+"---#.yeo.#"
        polite2 = romstem[:-3]+"ae.#"
        verbage|=set([(polite1, romverb), (polite2, romverb)])
        if romstem.replace("---h.a.#", "---d.oe.#") not in romverbs:
            moreverbs.append(romstem.replace("---h.a.#", "---d.oe.#"))
    elif romstem.endswith("d.oe.#"):
        polite1 = romstem+"---#.eo.#"
        polite2 = romstem[:-4]+"wae.#"
        verbage|=set([(polite1, romverb), (polite2, romverb)])
    elif romstem.endswith(".e.#") or romstem.endswith(".ae.#"):
        verbage.add((romstem+"---#.eo.#", romverb))
    elif romstem.endswith(".l"):
        verbage.add((romstem[:-1]+"#", romverb))
    elif romstem.endswith("#---r.eu.#"):
        polite = romstem.replace("#---r.eu.#", "l---r.a.#")
        verbage.add((polite, romverb))
    if not romstem.endswith("#"):
        themevowel = romstem.split(".")[-2]
        if themevowel in ["a", "ya", "o", "yo", "wa"]:
            polite = romstem+"---#.a.#"
        else:
            polite = romstem+"---#.eo.#"
        verbage.add((polite, romverb))
    if romstem.endswith(".o.#"):
        polite = romstem[:-3]+"wa.#"
        verbage.add((polite, romverb))
    if polite:
        past = polite[:-1]+"ss"
        verbage.add((past, romverb))
    elif polite1:
        past1 = polite1[:-1]+"ss"
        past2 = polite2[:-1]+"ss"
        verbage|=set([(past1, romverb), (past2, romverb)])
    else: # polite = mainform
        past = romstem[:-1]+"ss"
        verbage.add((past, romverb))
    return (polite1, polite2, polite)


def suggestoverb(thisform, vocab=set(), thelist=False):
    maybestem = ""
    if not thelist: 
        thelist = [
            "---m.a.#",
            "---d.o.#---r.o.g",
            "---j.i.#---m.a.n",
            "---m.eu.#---r.o.#",
            "---d.eo.#---n.i.#",
            "---d.eo.#---r.a.#",
            "b---n.i.#---d.a.#",
            "b---s.i.#---d.a.#",
            "b---s.i.#---#.o.#",
            "---s.i.#---#.o.#",
            "---g.eo.#---n.a.#",
            "---g.eo.#---n.i.#---.wa.#",
            "---d.a.n---d.a.#",
            "---d.a.#",
            "---d.a.n",
            "---#.yo.#",
            "---g.eo.#---d.eu.n",
            "---g.o.#",
            "---g.u.#",
            "---r.a.#",
            "---r.i.#",
            "---n.i.#",
            "---n.a.#",
            "---j.a.#",
            "---s.e.#",
            "---s.eo.#",
            "---m.yeo.n",
            "---m.yeo.#",
            "---d.eo.n",
            "---d.eu.n",
            "---d.eu.s",
            "---#.eu.#---m.yeo.#",
            "---g.u.#---n.a.#",
            "---g.u.n",
            "---g.e.ss---#.eu.#",
            "---g.e.ss---#.eo.#",
            "---g.e.ss",
            "n---d.a.#",
            "---n.eu.n---d.e.#",
            "---r.eo.#",
            "---r.yeo.#",
            "ss---d.a.#",
            "ss---d.a.#---g.o.#",
            "---g.e.#",
            "l---kk.a.#",
            "l---kk.e.#",
            "---j.i.#",
            "---#.eu.n",
            "---n.eu.n",
            "---#.ya.#",
            "l",
            "n",
            "m",
            "---g.i.#",
            "---j.i.#",
            "---j.yeo.#",
            "---j.yeo.ss",
            "---#.eo.ss",
            "---s.i.#",
            "---s.yeo.#",
            "---s.yeo.ss",
            "---d.a.#",
# adjuncts
            "---b.o.#",
            "---b.wa.#",
            "---b.o.#---#.a.ss",
            "---b.wa.ss",
            "---b.eo.#---r.i.#",
            "---b.eo.#---r.yeo.#",
            "---b.eo.#---r.yeo.ss",
            "---j.u.#---#.eo.#",
            "---j.wo.#",
            "---j.u.#",
            "---j.u.#---#.eo.ss",
            "---j.wo.ss",
            "---#.i.ss",
            "---#.i.ss---#.eu.#",
            "---#.i.ss---#.eo.#",
            "xxx",
        ]
    stemmed = thisform
    for ending in thelist:
        if thisform.endswith(ending):
            maybestem = thisform[:-len(ending)]
            if not ending.startswith("---"):
                maybestem += "#"
            thisform = maybestem
#            print maybestem
            if maybestem in verbs:
                stemmed = verbdic[maybestem]
                break
        elif ending=="xxx": #finished cycle
            if not verbs or not maybestem:
                pass
            else:
                if maybestem in verbs:
                    stemmed = verbdic[maybestem]
                elif maybestem.endswith("---#.i.#"): # copula
                    if maybestem[:-8] in vocab:
                        stemmed = maybestem[:-8]
                        stemmed = maybestem[:-8]
                elif maybestem.endswith("#---d.a.#"): #elided copula
                    if maybestem[:-8] in vocab:
                        stemmed = maybestem[:-8]
                elif maybestem.endswith("---s.eu.#---r.eo.#"):
                    stemmed = maybestem[:-18]
                elif maybestem.endswith("---s.eu.#---r.eo.#---#.u.#"):
                    stemmed = maybestem[:-26]
    return stemmed
    

def text2romwords(text):
    splitter="[%s\r\n\t\s]+" % re.escape(punct)
    words = set(re.split(splitter, text))
    romwords=[romanize(x) for x in words]
    return set(romwords)

    


def find_nouns(wordset):
    nounage = set()
    for word in wordset:
        if word+"---d.eu.l" in wordset:
            nounage.add(word)
        elif word.endswith("#"):
            if word+"---g.a.#" in wordset and not word.endswith("---d.a.#"):
                nounage.add(word)
            elif word+"---r.eu.l" in wordset:
                nounage.add(word)
            elif word+"---r.o.#" in wordset:
                nounage.add(word)
        elif not word.endswith("h"): # avoid trickery of johda, anhda &c.
            if word+"---#.i.#" in wordset:
                nounage.add(word)
            elif word+"---#.eu.l" in wordset:
                if word not in dict(verbage).keys():
                    nounage.add(word)
            elif word+"---#.eu.#---r.o.#" in wordset:
                nounage.add(word)
    return nounage


def process_word(word, vocab=set(), noun=[], firstpass=True, restrict=False, thisform=""): # romanized word
        if not thisform: 
            thisform = word
        stemmed = thisform
        global verbdic
        global verbs
        notdone = False
        afterparticles = ""
        nounish = False
        if len(word.split("---")) > 1: # syllable count
            if thisform.endswith("#---r.eu.l") and firstpass: #direct object
                if thisform[:-2] not in verbs: # ...
                    stemmed = thisform[:-9]
                else:
                    stemmed = thisform[:-1]+"#---d.a.#"
            elif thisform.endswith("---#.eu.l") and firstpass:
                    if not thisform.endswith("#---#.eu.l"):
                        stemmed = word[:-9]
            elif thisform.endswith("#---g.a.#"): #subject
                if thisform.endswith("---d.a.#---g.a.#"):
                    stemmed = word[:-16]+"---d.a.#"
                else:
                    stemmed = word[:-8]
            elif thisform.endswith("---#.i.#"):
                if not thisform.endswith("#---#.i.#"):
                        stemmed = thisform[:-8]
            elif thisform.endswith("#---n.eu.n") and firstpass: #topic
                if thisform[:-9] not in verbs and thisform[:-10]+"l" not in verbs and firstpass:
                    stemmed = thisform[:-9]
                elif thisform[:-9] in verbs:
                    stemmed = thisform[:-9]
                elif thisform[:-10]+"l" in verbs:
                    stemmed = thisform[:-10]+"l"
            elif thisform.endswith("---#.eu.n") and firstpass:
                if not thisform.endswith("#---#.eu.n"):
                        stemmed = thisform[:-9]
                        notdone = True
            elif thisform.endswith("---r.o.#"): 
                stemmed = word[:-8]
                if thisform.endswith("---#.eu.#---r.o.#"):
                    if not thisform.endswith("#---#.eu.#---r.o.#"):
                            stemmed = thisform[:-17]
            elif thisform.endswith("#---r.o.#---s.eo.#"):
                stemmed = thisform[:-17]
                if thisform.endswith("---#.eu.#---r.o.#---s.eo.#"):
                    if not thisform.endswith("#---#.eu.#---r.o.#---s.eo.#"):
                            stemmed = thisform[:-26]
            elif thisform.endswith("#---r.o.#---ss.eo.#"): 
                stemmed = thisform[:-18]
                if thisform.endswith("---#.eu.#---r.o.#---ss.eo.#"):
                    if not thisform.endswith("#---#.eu.#---r.o.#---ss.eo.#"):
                            stemmed = thisform[:-27]
            elif thisform.endswith("---#.e.#"):
                stemmed = thisform[:-8]
            elif thisform.endswith("---#.e.#---g.e.#"):
                stemmed = thisform[:-16]
            elif thisform.endswith("---#.e.#---g.e.#---s.eo.#"):
                stemmed = thisform[:-25]
            elif thisform.endswith("---kk.e.#"):
                stemmed = thisform[:-9]
            elif thisform.endswith("---#.e.#---s.eo.#"):
                stemmed = thisform[:-17]
            elif thisform.endswith("---kk.e.#---s.eo.#"):
                stemmed = thisform[:-18]
            elif thisform.endswith("---kk.a.#---j.i.#"):
                stemmed = thisform[:-17]
            elif thisform.endswith("---b.u.#---t.eo.#"):
                stemmed = thisform[:-17]
            elif thisform.endswith("---#.ui.#") and firstpass: # correct for stuff like ..
                stemmed = thisform[:-9]
            elif thisform.endswith("---d.eu.l"):
                stemmed = thisform[:-9]
            elif thisform.endswith("---#.i.n"):
                stemmed = thisform[:-8]
            elif thisform.endswith("#---#.wa.#"):
                stemmed = thisform[:-9]
            elif thisform.endswith("---g.wa.#") and not thisform.endswith("#---g.wa.#"):
                    stemmed = word[:-9]
            elif thisform.endswith("---d.o.#"):
                stemmed = thisform[:-8]
            elif thisform.endswith("---ch.eo.#---r.eo.m"):
                stemmed = thisform[:-19]
            elif thisform.endswith("---m.a.n"):
                stemmed = thisform[:-8]
            elif thisform.endswith("---m.a.l---#.ya.#"):
                stemmed = thisform[:-17]
            if stemmed.endswith("---d.eu.l"):
                if stemmed[:-1]+"#" not in verbs:
                    stemmed = stemmed[:-9]
            afterparticles = stemmed
            if afterparticles != thisform:
                nounish = True
            becomings = ["d.oe.#", "d.oe.n", "d.oe.l", "d.oe.m"]
            for beco in becomings: 
                if stemmed.endswith(beco): #cleanup
                    stemmed = stemmed[:-9]
                    break
            if not nounish:
                if stemmed:
                    stemmed = suggestoverb(stemmed, vocab=vocab)
                else:
                    stemmed = suggestoverb(thisform, vocab=vocab)
            else:
                thelist = ["---g.i.#", "m"]
                stemmed = suggestoverb(stemmed, thelist=thelist, vocab=vocab)
        if stemmed in verbs:
            if not stemmed == afterparticles or not len(stemmed.split("---")) < 2:
                stemmed = verbdic[stemmed]
        elif stemmed.endswith("#.i.#---d.a.#") and len(stemmed) > 16: # assuming not a verb in its own right, attached copula
            stemmed = stemmed[:-16]
        return stemmed


def hangulize(romword, hangul_only=False):
    if " " in romword:
        words = romword.split(" ")
        hangwords = []
        for word in words:
            hword = hangulize(word, hangul_only=hangul_only)
            hangwords.append(hword)
        return " ".join(hangwords)
    syllables = romword.split("---")
    if len(syllables) == 1:
        if syllables[0].count(".") != 2:
            if not hangul_only:
                return romword
            else:
                return ""
    vowels=["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
    initials=["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "#", "j", "jj", "ch", "k", "t", "p", "h"]
    finals=["#", "g", "kk", "ks", "n", "nj", "nh", "d", "l", "lk", "lm", "lb", "ls", "lt", "lp", "lh", "m", "b", "bs", "s", "ss", "ng", "j", "ch", "k", "t", "p", "h"]
    output = u""
    for s in syllables:
        pieces = s.split(".")
        first = pieces[0]
        vowel = pieces[1]
        last = pieces[2]
        number = 44032 + (588 * initials.index(first))
        number += 28 * vowels.index(vowel)
        number += finals.index(last)
        output += unichr(number)
    return output

    
def setup(reset=True):
### keep at end ###
    if reset or not verbage:
        try:
            verbfile = open(verbfilepath)
        except IOError:
            pass
        else:
            with verbfile:
                rawverbs = [unicode(x.split(":")[0], "utf-8", "ignore").strip() for x in verbfile if ":" in x]
            romverbs = set()
            for r in rawverbs:
                romverbs.add(romanize(r[:-1]))
            for v in rawverbs:
                romstem = romanize(v[:-1])
                romverb = romanize(v)
                process_verb(romstem, romverb, romverbs=romverbs) # adds to "verbage" global
        global verbdic
        global verbs
        verbdic = dict(verbage)
        verbs = set(verbdic.keys())
        print "Done with verbs."

        
def search(searchterm, directory="KR", suffix=".html", endat=10):
    if re.search("[a-zA-Z]", searchterm):
        searchterm = hangulize(searchterm)
    if type(searchterm) == unicode:
        searchterm = searchterm.encode("utf-8", "ignore")
    found = []
    filenames = os.listdir(directory)
    filenames = [x for x in filenames if x.endswith(suffix)]
    filenames = [os.path.join(directory, x) for x in filenames]
    for path in filenames:
        if not filenames.index(path) % 500:
            print filenames.index(path), len(filenames), len(found)
        text = open(path).read()
        if searchterm in text:
            found.append(path)
            if len(found) >= endat:
                break
    return found
    
