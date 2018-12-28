# -*- coding: utf-8 -*-
from urllib import request # Python 3.6支持
import sys
import xml.sax
import time

class TitleHandler(xml.sax.ContentHandler):
    def __init__(self,fout,has_headline,encodingType='utf-8'):  # encodingType为了Linux系统而加，在MAC OS上，写文件无需进行encode(encodingType操作)
        xml.sax.ContentHandler.__init__(self)
        self.CurrentData = ""
        self.Content = ""
        self.fout = fout
        self.has_headline = has_headline
        self.url = ""
        self.encodingType = encodingType

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        # if tag == "title":
        #     print("Element start: %s" % tag)

    def endElement(self, tag):
        # if tag == "title":
        #     print("Element end: %s" % tag)
        self.CurrentData = ""

    def characters(self, content):
        if has_headline and self.CurrentData == "headline":
            self.Content = content + "\t" + self.url
            self.fout.write("%s\n" % self.Content.encode(self.encodingType))
        if not has_headline and self.CurrentData == "title":
            self.Content = content
        if self.CurrentData == "url":
            if has_headline:
                self.url = content
            else:
                self.Content = self.Content + "\t" + content
                self.fout.write("%s\n" % self.Content.encode(self.encodingType))
        # if self.CurrentData == "title":
        #     # print ("Characters: %s" % content)
        #     self.Content = content
        #     self.fout.write("%s" % content)
        # if self.CurrentData == "url":
        #     self.fout.write("\t%s\n" % content)

if __name__ == "__main__":
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    fo = open("dump_xml_data.txt", 'w')
    authority_pool = []

    cnt = 0
    for i in authority_pool:
        if "specific url" in i and "wenda" in i:
            has_headline = True
        else:
            has_headline = False
        Handler = TitleHandler(fo,has_headline)
        parser.setContentHandler(Handler)
        cnt += 1
        # 中文网页存在两种编码，sax默认是utf-8解码
        try:
            parser.parse(request.urlopen(i))
            print("%s: parse is done %d / %d" % (time.strftime('%Y-%m-%d %H:%M:%S'), cnt, len(authority_pool)))       # make_parser().parse(strem or file)
        except Exception as e:
            try :
                Handler = TitleHandler(fo,has_headline,'gbk')
                xml.sax.parseString(request.urlopen(i).read().decode('gbk'),Handler)
                print("%s: parse is done %d / %d" % (time.strftime('%Y-%m-%d %H:%M:%S'), cnt, len(authority_pool)))    # parseString
            except Exception as err:
                print(repr(err))
                print("parse url--%s fail" % i)
    fo.close()
