# coding=utf-8
# 记录平时工作学习过程中比较常用有关文本处理的函数
# 函数传入参数是ustring的统一为Unicode编码，其余未做特殊说明为utf-8编码

import re
# 中文文本处理，过滤字母数字和特殊字符
def filter_digit_letter(ustring):
    r = '[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
    return (re.sub(r,"",ustring))

# 全角半角转换
def setB2Q(ustring):
    # 半角转全角
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 32:                                 # 半角空格直接转化
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:        # 半角字符（除空格）根据关系转化
            inside_code += 65248
        rstring += unichr(inside_code)
    return rstring


def setQ2B(ustring):
    # 全角转半角
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif inside_code >= 65280 and inside_code <= 65374:
            inside_code -= 65248
        rstring += unichr(inside_code)
    return rstring

# 识别一段文本中有无数字，如有中文数字则转阿拉伯数字
def recognize_age(speech_text):
    speech_text = speech_text.decode('utf-8')
    dig = re.search("\d+",speech_text)
    if dig:
        return int(dig.group())
    dig_char = re.search('[零一二两三四五六七八九十百]+'.decode('utf-8'),speech_text)
    if not dig_char:
        return -1   # 没有数字则返回-1
    dig_char = dig_char.group()
    common_used_numerals_tmp ={'零':0, '一':1, '二':2, '两':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, '百':100}
    common_used_numerals = dict()
    for key,value in common_used_numerals_tmp.iteritems():
        common_used_numerals[key.decode('utf-8')] = value
    total = 0
    r = 1              #表示单位：个十百千...
    for i in range(len(dig_char) - 1, -1, -1):
        val = common_used_numerals.get(dig_char[i])
        if val >= 10 and i == 0:  #应对 十三 十四 十*之类
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
            #total =total + r * x
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val
    return total

# 建立词典
def build_vocab(filename,threshold):
    vocab = dict()
    f = open(os.path.join(dirname,filename),'r')
    for line in f.xreadlines():
        if line.strip():
            line = line.decode('gbk','ignore').replace("\n"," <EOS>").replace("\t"," <EOS> ")
            for word in line.split():
                vocab[word] = vocab.get(word,0) + 1
    f.close()
    count_pairs = sorted(vocab.items(),key=lambda x: (-x[1],x[0]))
    count_pairs_filter = filter(lambda x:x[1] > threshold,count_pairs)
    words, _ = list(zip(*count_pairs_filter))
    # 单词到整数的映射
    word_to_id = dict(zip(words, range(2,len(words) + 2)))
    word_to_id["<PAD>"] = 0
    word_to_id["<UNK>"] = 1
    return word_to_id

# batch数据生成
def generate_batch(data,batch_size):
    batch_data = []
    for x in data:
        if len(batch_data) == batch_size:
            yield batch_data
            batch_data = []
        batch_data.append(x)
    if len(batch_data) != 0:
        yield batch_data
