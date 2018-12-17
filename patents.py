from collections import Counter, defaultdict
import re

# Library for rapidly cleaning the extracted text of Korean patents and published applications

def clean_patent_text(text, pattern="\[\d\d\d\d\]", mustend=True):
    if pattern:
        text = fix_line_numbers(text, pattern, mustend)
    print len(text)
    text = remove_rep_header(text)
    print len(text)
    text = unbreak_paras(text)
    print len(text)
    text = tab_biblio(text)
    print len(text)
    text = unbreak_more_paras(text)
    print len(text)
    text = insert_page_breaks(text)
    print len(text)
    text = repair_pages(text)
    print len(text)
    text = fix_superscripts(text)
    print len(text)
    return text


def fix_superscripts(text):
    lines=[x.strip() for x in text.split("\n")]
    print len(lines)
    indices=range(len(lines))
    index=indices[0]
    while index < len(lines):
        line=lines[index]
        if len(line) > 3:
            index+=1
            continue
        else:
            try:
                value=int(line)
            except ValueError:
                index+=1
                continue
            else:
                print value
                lines[index-1]=lines[index-1]+"^"+str(value)+" "+lines[index+1]
                del(lines[index+1])
                del(lines[index])
                index-=1
    outtext="\n".join(lines)
    print len(lines)
    return outtext

    
def fix_line_numbers(text,pattern="\[\d\d\d\d\]",mustend=True):
    lines=[x.strip() for x in text.split("\n")]
    print len(re.findall(pattern,text))
    for line in lines:
#        if not line.endswith("]"):
#            continue
        if not re.search(pattern,line):
            continue
        match=re.search(pattern,line).group(0)
        if match: print str(match)
        else: continue
        if mustend and not line.endswith(match):
            continue
        lines[lines.index(line)]=match+"\t"+(line.replace(match,""))
    outtext="\n".join(lines)
    return outtext


def remove_rep_header(text, catcher="10-"):
    lines=text.split("\n")
    kept_once=False
    lines.reverse()
    for line in lines:
        if line.strip().count(" ") == 1:
            if line.split(" ")[1].startswith(catcher):
                if not kept_once:
                    kept_once=True
                    continue
                else:
                    lines[lines.index(line)]=""
                    continue
    lines.reverse() #it's really weird that these statements are necessary, but otherwise the "first" occurrence ends up being at the end of the file.
    outtext="\n".join(lines)
    return outtext
    
    
def unbreak_paras(text): #after fix_line_numbers; works only for docs with standard [xxxx] paragraph numbering
    if not "[0001]" in text: # this approach only works in doc with numbered paras; if not present, bounce
        return text
    lines=[x.strip() for x in text.split("\n")]
    newlines=[]
    current_line=""
    for line in lines:
        match=re.match("\[\d\d\d\d\]",line)
        if not match and not current_line:
            newlines.append(line)
        elif current_line and not match:
            current_line+=line
            if current_line.strip().endswith("."):
                newlines.append(current_line)
                current_line=""
        elif current_line and match: # did previous para end without period?
            newlines.append(current_line)
            current_line=line
        elif match and not current_line:
            current_line=line
    outtext="\n".join(newlines)
    return outtext


def tab_biblio(text,matcher="\n(\(\d\d\)\s*.*?)\s\s+"):
    outtext=re.sub(matcher,"\n\\1\t",text)
    return outtext


def unbreak_more_paras(text): # after unbreak_paras, fix_line_numbers, biblio
    lines=[x.strip() for x in text.split("\n")]
    newlines=[]
    current_line=""
    for line in lines:
        if is_probably_text(line):
            if current_line:
                current_line+=line
                if line.strip().endswith("."):
                    newlines.append(current_line)
                    current_line=""
                continue
            if not current_line:
                current_line=line
                if line.strip().endswith("."):
                    newlines.append(current_line)
                    current_line=""
        if not is_probably_text(line):
            if current_line:
                newlines.append(current_line)
                current_line=""
            if not current_line:
                pass
            newlines.append(line)
    outtext="\n".join(newlines)
    return outtext
    
    
def insert_page_breaks(text, breaker="(\-\s+\d{1,2}\s+\-)"): 
    print len(re.findall(breaker,text))
    outtext=re.sub(breaker,"\n\\1\n\f\n",text)
    return outtext
    
    
def repair_pages(text): # after paragraph restoration and pagebreak insertion
    pages=text.split("\f")
    for p in pages:
        pagedex=pages.index(p)
        lines=p.strip().split("\n")
        theselines=[x for x in lines[:-1] if x.strip()]
        if not theselines:
            continue
        lastline=theselines[-1]
        linedex=lines.index(lastline)
        if is_probably_text(lastline,[]) and not lastline.strip().endswith("."):
            if pagedex+1 < len(pages):
                nextpage=pages[pagedex+1]
                try: 
                    nextline=[x for x in nextpage.split("\n") if x.strip()][0]
                except IndexError:
                    nextline=""
                newlastline=lastline + nextline
                newnextpage=nextpage.replace(nextline,"\r\n",1)
                lines[linedex]=newlastline
                newthispage="\n".join(lines)
                pages[pagedex]=newthispage
                pages[pagedex+1]=newnextpage
                continue
    outtext="\f".join(pages)
    return outtext


def split_biblio(text):
    title_marker = "(54)" # indicates title of invention, which typically occurs at or near the end of the bibliographic data 
    return text.split(title_marker, 1) 


def repair_words(text):
    if type(text) == str:
        text = unicode(text, "utf-8", "ignore")
    whitespace_splitter = "(\s+)"
    word_scrubber = re.compile("\W+", re.UNICODE)
    textpieces = split_biblio(text)
    if len(textpieces) > 1:
        biblio = textpieces[0]
        text = textpieces[1]
    else:
        biblio = ""
    newtext = ""
    words = re.split(re.compile(whitespace_splitter, re.UNICODE), text)
    uniques = set(words)
    index = 0
    word_count = len(words)
    combined = set()
    not_combined = set()
    to_separate = []
    while index < word_count - 1:
        combine_them = False
        next_word_index = index + 2
        next_space_index = index + 3
        space_after_this = words[index + 1]
        try:
            space_after_next = words[next_space_index]
        except IndexError:
            space_after_next = ""
            next_space_index = None
        thisword = words[index]
        nextword = words[index + 2]
        combined_word = thisword + nextword
        separated_phrase = thisword + " " + nextword
        if combined_word not in not_combined:
            if combined_word in combined:
                combine_them = True
            else:
                if combined_word in uniques:
                    separated_regex = re.compile(re.escape(thisword) + whitespace_splitter + re.escape(nextword))
                    separated_count = len(re.findall(separated_regex, text))
                    combined_count = len(re.findall(re.escape(combined_word), text))
                    if combined_count > separated_count:
                        combine_them = True
                        print "Combining", separated_phrase, combined_word, separated_count, combined_count
                    elif separated_count > combined_count:
                        print "Separating", separated_phrase, combined_word, separated_count, combined_count
                        to_separate.append((combined_word, separated_phrase))
        if combine_them is False:
            not_combined.add(combined_word)
        else:
            thisword += nextword
            space_after_this += space_after_next
            if next_space_index is not None:
                del(words[next_space_index])
            del(words[next_word_index])
            word_count = len(words)
            combined.add(combined_word)
        newtext += thisword
        newtext += space_after_this
        index += 2
    if index < word_count - 1:
        remainder = words[index:]
        to_add = "".join(remainder)
        newtext += to_add
    for combined_word, separated_phrase in to_separate:
        newtext.replace(combined_word, separated_phrase)
    newtext = biblio + newtext 
    return newtext


def is_probably_text(line,bouncers=["\t"],unbouncers=["\<\d+\d\>\t","\[\d+\]\t"]): #utility function: if it has at least 4 words or ends with punctuation, presume part of running text
    if not line.strip():
        return False
    if re.match("\(\d",line): # for biblio info
        return False
    for b in bouncers:
        if b in line:
            unbounced=False
            for u in unbouncers:
                if re.search(u,line): 
                    unbounced=True
            if not unbounced:
                return False
    value=False
    if line.strip()[-1] in [".",",","?","!",";",":"]:
        value=True
    elif line.count(" ") > 3:
        value=True
    return value

        
if __name__ == "__main__":
    open("newpatent.txt","w").write(clean_patent_text(open("patent.txt").read(),"\[\d\d\d\d\]"))

