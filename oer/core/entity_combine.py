from oer.bean.word_unit import WordUnit


class EntityCombine:
    """将分词词性标注后得到的words与netags进行合并"""
    @classmethod
    def combine(cls, words, netags):
        """根据命名实体的B-I-E进行词合并
        Args:
            words: WordUnit list，分词与词性标注后得到的words
            netags: list，命名实体识别结果
        Returns:
            words_combine: WordUnit list，连接后的结果
        """
        words_combine = []  # 存储连接后的结果
        length = len(netags)
        n = 1  # 实体计数，从1开始
        i = 0
        while i < length:
            if 'S-' in netags[i]:
                words[i].ID = n
                words[i].postag = cls.judge_postag(netags[i])
                words_combine.append(words[i])
                n += 1
                i += 1
            elif 'B-' in netags[i]:
                newword = words[i].lemma
                j = i + 1
                while j < length:
                    if 'I-' in netags[j]:
                        newword += words[j].lemma
                    elif 'E-' in netags[j]:
                        newword += words[j].lemma
                        j += 1
                        break
                    elif 'O' == netags[j] or (j + 1) == length:
                        break
                    j += 1
                words_combine.append(WordUnit(n, newword, cls.judge_postag(netags[j - 1])))
                n += 1
                i = j
            else:
                words[i].ID = n
                n += 1
                words_combine.append(words[i])
                i += 1
        return cls.combine_comm(words_combine)

    @classmethod
    def combine_comm(cls, words):
        """根据词性标注进行普通实体合并
        Args:
            words: WordUnit list，进行命名实体合并后的words
        Returns:
            words_combine: WordUnit list，进行普通实体连接后的words
        """
        newword = words[0].lemma  # 第一个词，作为新词
        words_combine = []  # 存储合并后的结果
        n = 1
        i = 1  # 当前词ID
        while i < len(words):
            word = words[i]
            # 词合并: (前后词都是实体) and (前后词的词性相同 or 前词 in ["nz", "j"] or 后词 in ["nz", "j"])
            if (cls.is_entity(word.postag) and cls.is_entity(words[i-1].postag) 
                and (word.postag in {'nz', 'j'} or words[i-1].postag in {'nz', 'j'})):
                newword += word.lemma
            else:
                words_combine.append(WordUnit(n, newword, words[i - 1].postag))  # 添加上一个词
                n += 1
                newword = word.lemma  # 当前词作为新词
            i += 1
        # 添加最后一个词
        words_combine.append(WordUnit(n, newword, words[len(words)-1].postag))
        return words_combine

    @classmethod
    def judge_postag(cls, netag):
        """根据命名实体识别结果判断该连接实体的词性标注
        Args:
            netag: string，该词的词性标注
        Returns:
            entity_postag: string，判别得到的该连接实体的词性
        """
        entity_postag = ''
        if '-Ns' in netag:
            entity_postag = 'ns'  # 地名
        elif '-Ni' in netag:
            entity_postag = 'ni'  # 机构名
        elif '-Nh' in netag:
            entity_postag = 'nh'  # 人名
        return entity_postag

    @classmethod
    def is_entity(cls, netag):
        """根据词性判断该词是否是候选实体
        Args:
            netag: string，该词的词性标注
        Returns:
            flag: bool, 实体标志，实体(True)，非实体(False)
        """
        flag = False  # 默认该词标志不为实体
        # 地名，机构名，人名，其他名词，缩略词
        if netag in {'ns', 'ni', 'nh', 'nz', 'j'}:
            flag = True
        return flag

