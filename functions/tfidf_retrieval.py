# -*- coding: utf-8 -*-
import jieba
import math
import time
import sys
import os

def generate_vocab_inverted_index(filename):
    vocab = set()
    vocab_idf = dict()
    id2title = dict()
    term2ids = dict()
    docNum = 0
    f = open(filename, 'r')
    for line in f.xreadlines():
        if line.strip() and len(line.strip().split('\t')) == 2:
            docNum += 1
            title = line.strip().split('\t')[0].decode('utf-8')
            #title = line.strip().decode('utf-8')
            id2title[docNum] = line.strip().decode('utf-8')
            term_split = set(jieba.lcut(title))
            for term in term_split:
                vocab.add(term)
                vocab_idf[term] = vocab_idf.get(term,0) + 1
                if term in term2ids:
                    term2ids[term].append(docNum)
                else:
                    term2ids[term] = [docNum]
    f.close()
    print "vocabulary size is:%d" % len(vocab)
    for term,n in vocab_idf.iteritems():
        if n > 0:
            vocab_idf[term] = 1.0 + math.log(float(docNum) / n)
        else:
            vocab_idf[term] = 1.0
    return vocab,vocab_idf,id2title,term2ids

def termFrequency(term, document):
    normalizeDocument = jieba.lcut(document)
    return normalizeDocument.count(term) / float(len(normalizeDocument))

def calculate_title_score(vocab_idf,filename):
    title2score = dict()
    num = 0
    f = open(filename,'r')
    for line in f.xreadlines():
        if line.strip() and len(line.strip().split('\t')) == 2:
            num += 1
            line = line.strip().split('\t')[0].decode('utf-8')
            title2score[num] = dict()
            term_split = set(jieba.lcut(line))
            for term in term_split:
                tf = termFrequency(term, line)
                if term in vocab_idf:
                    idf = vocab_idf[term]
                    title2score[num][term] = tf * idf
            
    f.close()
    print "%s----%d titles score are computed" % (time.strftime('%Y-%m-%d %H:%M:%S'),num)
    return title2score

def dump_vocab_idf(idf_dict,filename):
    sort_idf = sorted(idf_dict.items(), key=lambda x: x[1])
    f = open(filename,"w")
    for item in sort_idf:
        f.write("%s\t%.6f\n" %(item[0].encode("utf-8"),item[1]))
    f.close()
    print "IDF score of vocabulary is all dumped into %s" % filename

if __name__ == "__main__":
    print "%s----Process start......." % time.strftime('%Y-%m-%d %H:%M:%S')
    query_file = "query.txt"
    title_file = "doc.txt" # two columns, one is doc, anthoer is url, segmented by tab
    vocab,vocab_idf,id2title,term2ids = generate_vocab_inverted_index(title_file)
    idf_file = "qa_repo_idf.txt"
    dump_vocab_idf(vocab_idf,idf_file)
    
    title_term_tf_idf = calculate_title_score(vocab_idf,title_file) # key:title value:{word:tf,idf}+
    retrieval_result = "retrieval_result.txt"
    retrieval_no_result = "no_result_query.txt"
    topN = 5                                  # TopN results will be returned 
    f = open(query_file,'r')
    fo = open(retrieval_result,'w')
    fo_no = open(retrieval_no_result,'w')
    query_post_num = 0
    for line in f.xreadlines():
        if line.strip():
            query_post_num += 1
            match_score = dict()
            query = line.strip().decode('utf-8')
            query_norm = 0.0
            query_max_idf = 0.0
            max_term = ""
            query_split = set(jieba.lcut(query))
            for term in query_split:
                tf = termFrequency(term, query)
                if term in vocab_idf:
                    idf = vocab_idf[term]
                    query_norm += pow(tf*idf,2)
                    if idf > query_max_idf:
                        max_term = term
            query_norm = math.sqrt(query_norm)
            if not max_term in term2ids:
                continue 
            candidates = term2ids[max_term]
            
            for title_id in candidates:                
                inter_term = query_split & set(jieba.lcut(id2title[title_id].split('\t')[0]))
                if len(inter_term) < 1:
                    continue
                # consine similarity between query & title
                numerator = 0.0
                for term in inter_term:
                    # print "inter term:" + term
                    tf = termFrequency(term, query)
                    if term in vocab_idf:
                        idf = vocab_idf[term]
                        numerator += tf*idf * title_term_tf_idf[title_id][term]
                
                title_norm = 0.0
                for term,score in title_term_tf_idf[title_id].iteritems():
                    title_norm += pow(score,2)
                title_norm = math.sqrt(title_norm)

                if query_norm * title_norm > 0.0:
                    match_score[title_id] = numerator / (query_norm * title_norm)
            if len(match_score) < topN:
                # print "No enough result for query:%s" % query
                fo_no.write("%s\n" % query.encode('utf-8'))
                continue
            sorted_match = sorted(match_score.items(), key = lambda x:x[1], reverse=True)
            for i in range(topN):
                fo.write("%s\t%s\t%.6f\n" % (query.encode('utf-8'),id2title[sorted_match[i][0]].encode('utf-8'),sorted_match[i][1]))
            
            if query_post_num % 1000 == 0:
                print "%s---%d queries have been processed!" % (time.strftime('%Y-%m-%d %H:%M:%S'),query_post_num)
    f.close()
    fo.close()
    fo_no.close()
    print "All %d queries has been processed!" % query_post_num
