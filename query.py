import argparse
import os
import re
import time

query_attributes = ["user_text", "kr_include", "kr_include_type", 
    "us_include", "us_include_type", "kr_exclude", "kr_exclude_type",
    "us_exclude", "us_exclude_type"]


class DummyQuery: # class to allow non-CGI interfaces to interact with QueryHandler

    def __init__(self, query=None, **kwargs): # use "query" param for CGI FieldStorage instance
        if not query:
            self.query = kwargs
        else:
            self.query = query
        for att in query_attributes:
            if att in query.keys():
                value = query[att]
            else:
                value = None
            setattr(self, att, value)

class QueryHandler:

    def __init__(self, queryobj=None, **kwargs, mappings="mappings.tsv"): # queryobj may be a CGI FieldStorage instance, 
        # or any other object with the same attributes
        if queryobj is None:
            queryobj = DummyQuery(kwargs)
        self.query = queryobj
        self.compiled = {}
        for att in query_attributes:
            setattr(self, att, getattr(queryobj, att))
        self.pairs = [tuple(x.split("\t",2)[:2]) for x in open(mappings) if "\t" in x]
    
    def fetch_text(self, fileid, country="KR"):
        filepath = os.path.join(country, fileid + ".txt")
        if not os.path.exists(filepath):
            print "Alarm!  No file at " + filepath
            return ""
        text = open(filepath).read()
        return text

    def answer(self, limit=10):
        # Main pipeline for query results
        # First we evaluate the terminological constraints, to narrow down the files
        # For each potential query, we compile it as a regex
        for constraint in ["kr_include", "us_include", "kr_exclude", "us_exclude"]:
            constraint_value = getattr(self, constraint)
            if constraint_value is not None:
                typeattr = getattr(self, constraint + "_type")
                if getattr(self, typeattr) == "exact":
                    self.compiled[constraint] = re.compile(re.escape(constraint_value)), re.UNICODE)
                else:
                    self.compiled[constraint] = re.compile(constraint_value, re.UNICODE)
        newpairs = list()
        for usid, krid in self.pairs:
            keep = True
            texts = {}
            if "kr_" in str(self.compiled.keys()):
                krtext = self.fetch_text(krid, "KR")
                texts["KR"] = krtext
            elif "us_" in str(self.compiled.keys()):
                ustext = self.fetch_text(usid, "US")
                texts["US"] = ustext
            for constraint in self.compiled.keys():
                country = constraint[:2].upper()
                regex = self.compiled[constraint]
                inclusive = constraint.endswith("include")
                is_present = re.search(regex, texts[country])
                if inclusive and not is_present:
                    keep = False
                elif is_present and not inclusive:
                    keep = False
                if keep is False:
                    break
            if keep is True:
                newpairs.append((usid, krid))
        self.pairs = newpairs
        # Now that the field has been narrowed, we run the similarity ranking
        if self.user_text:
            doc = self.user_text
        else:
            doc = self.us_include + " " + self.kr_include
        if self.user_text_language != "EN":
            self.user_text_language = "KO"
            country = "KR"
        else:
            country = "US"
        temppath = "temp%s.txt" % str(time.time())
        open(temppath,"w").write(doc)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process patent query.')
    parser.add_argument('--kr_include', help="Regex or phrase that any Korean document must contain")
    parser.add_argument('--us_include', help="Regex or phrase that any US document must contain")
    parser.add_argument('--kr_exclude', help="Regex or phrase that any Korean document must NOT contain")
    parser.add_argument('--us_exclude', help="Regex or phrase that any US document must NOT contain")
    parser.add_argument('--us_exclude_type', help="Either 'regex' or 'phrase'")
    parser.parse_args()
