# coding=utf-8

import math
import os
import random


def get_most_informative_words(stemfilepath, indexpath=None, cutoff=50, save=True, load=True):
    # key words for a specific document based on TF-IDF
    if indexpath is None:
        indexpath = "KR.index"
    savepath = stemfilepath.replace(".stems","") + ".best"
    if os.path.exists(savepath) and load is True:
        result = []
        bestfile = open(savepath)
        for line in bestfile:
            if not "\t" in line:
                continue
            word, count = line.split("\t")
            count = int(count)
            result.append((word, count))
        return result
    stemdic = stems2dict(stemfilepath)
    stems = set(stemdic.keys())
    tfidf_ranking = []
    indexfile = open(indexpath)
    # by using existing index, we can benefit from any filtering already done;
    # e.g. removal of very high- and low-frequency words
    for line in indexfile:
        stem, docs = line.split("\t", 1)
        if stem not in stems:
            continue
        docfreq = docs.count(",")
        termfreq = stemdic[stem]
        tfidf = float(termfreq) / docfreq
        tfidf_ranking.append((tfidf, stem))
    best_words = sorted(tfidf_ranking)[:cutoff]
    result = [(x[1], stemdic[x[1]]) for x in best_words]
    if save:
        savepath = stemfilepath.replace(".stems","") + ".best"
        to_save = "\n".join(["\t".join([x[0], str(x[1])]) for x in result])
        open(savepath, "w").write(to_save)
    return result


def stems2dict(stemfilepath):
    stemdic = {}
    stemfile = open(stemfilepath)
    for line in stemfile:
        stem, count = line.split("\t", 1)
        count = int(count.strip())
        stemdic[stem] = count
    return stemdic


def vectorize(termcounts, vocab):
    total = sum(termcounts.values())
#    vec = [float(termcounts[x])/total for x in vocab]
    vec = [float(termcounts[x]) for x in vocab]
    return vec


def dot_product(terms1, terms2):
    total1 = sum(terms1.values())
    total2 = sum(terms2.values())
    vecterms = list(set(terms1.keys()).intersection(terms2.keys()))
    vec1 = vectorize(terms1, vecterms)
    vec2 = vectorize(terms2, vecterms)
    dot = sum([vec1[i] * vec2[i] for i in range(len(vecterms))])
    return dot


def magnitude(terms):
    values = terms.values()
    summed_squares = sum([x ** 2 for x in values])
    mag = math.sqrt(summed_squares)
    return mag


def cosine_sim(terms1, terms2):
    dot = dot_product(terms1, terms2)
    mag = magnitude(terms1) * magnitude(terms2)
    sim = float(dot) / mag
    return sim


def test_best(bests, cutoff=5):
    random.shuffle(bests)
    subject = bests[0]
    bests = bests[1:]
    print "Seeking best matches for ", subject[0]
    ranked = []
    subject_terms = dict(subject[1])
    keywords = set(subject_terms.keys())
    for filepath, termlist in bests:
        termdic = dict(termlist)
        thesekeys = set(termdic.keys())
        if len(thesekeys.intersection(keywords)) < 3: # clearly not a match
            continue
        sim = cosine_sim(termdic, subject_terms)
        ranked.append((sim, filepath))
    ranked.sort()
    ranked.reverse()
    ranked = ranked[:cutoff]
    print str(ranked)
    precision = evaluate_ranking(subject, ranked)
    return precision
    

def evaluate_ranking(comparator, ranked, datapath="mappings.tsv"):
# Precision metric:
# Evaluates a specific similarity ranking based on whether the ranked items each have at least one perfect IPC match with the comparator.
# This is a pretty crude way of handling precision (and will create a significant number of false negatives) but gives a ballpark notion.
# Since the IPC hierarchy provides a good basis for graded relevance, ideally this would be replaced with NDCG.
    def id_from_filepath(filepath):
        filepath = filepath.split("/")[-1]
        filepath = filepath.split(".")[0]
        return filepath
    def extract_ipcs(line):
        ipcs = [x.split("(")[0].strip() for x in line.split("\t")[-1].split("; ")]
        return set(ipcs)
    comparator_id = id_from_filepath(comparator[0])
    data = open(datapath).read().split("\n")
    datadic = dict([(x.split("\t")[1], x) for x in data])
    ipcdic = dict([(x[0], extract_ipcs(x[1])) for x in datadic.items()])
    krids = set(datadic.keys())
    if comparator_id not in krids: # no data to work with
        return
    thisline = datadic[comparator_id]
    these_ipcs = extract_ipcs(thisline)
    precision = 0
    denominator = len(ranked)
    for r in ranked:
        r_id = id_from_filepath(r[1])
        if r_id not in krids: # file excluded e.g. due to divisional US application
            denominator -= 1
            continue
        thatline = datadic[r_id]
        if thisline == thatline:
            raise ValueError
        those_ipcs = extract_ipcs(thatline)
        matches = these_ipcs.intersection(those_ipcs)
        print r_id, str(matches)
        relevant = bool(matches)
        if relevant:
            precision += 1
    if denominator == 0:
        return
    average_precision = float(precision) / denominator
    return average_precision


def test_similarity(filepath=None, metric=cosine_sim, directory="KR", indexpath="KR.index", runs=100, cutoff=5):
# Runs basic sanity checks and then does test runs comparing in-corpus files to each other to obtain MAP,
# using IPC matches as a proxy for relevance.
    this = {"a":1, "b":1, "c":0}
    that = {"a":1, "b":0, "c":1}
    result = metric(this, this)
    if int(math.degrees(math.acos(result))) == 0:
        print "Test 1 passed"
    else:
        print "Test 1 failed", result
    result = metric(this, that)
    if int(math.degrees(math.acos(result))) == 60:
        print "Test 2 passed"
    else:
        print "Test 2 failed", result
    if metric(this, that) == metric(that, this):
        print "Test 3 passed"
    else:
        print "Test 3 failed"
    stemfiles = [os.path.join(directory, x) for x in os.listdir(directory) if x.endswith(".stems")]
    print "Loading best words for each of %d files" % len(stemfiles)
    bests = [(x, get_most_informative_words(x, indexpath, save=True, load=True)) for x in stemfiles]
    runcount = 0
    cumulative_score = 0
    mean_average_precision = 0
    while runcount < runs:
        runcount += 1
        print "Run # %d/%d" % (runcount, runs)
        score = test_best(bests, cutoff=cutoff)
        if score is None:
            runcount -= 1 # let it be as if it had never been
            continue
        cumulative_score += score
        mean_average_precision = float(cumulative_score) / runcount
        print score, mean_average_precision
    return mean_average_precision
