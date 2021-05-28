import os

from ltp import LTP

from oer.bean.word_unit import WordUnit
from oer.bean.sentence_unit import SentenceUnit
from oer.core.entity_combine import EntityCombine


class NLP:
    """进行自然语言处理，包括分词，词性标注，命名实体识别，依存句法分析
    Attributes:
        default_user_dict_dir: str，用户自定义词典目录
    """
    RESOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resource"))
    def __init__(self, model_type='base', user_dict_dir=RESOURCE_DIR):
        self.default_user_dict_dir = user_dict_dir
        # 加载ltp模型
        self.ltp = LTP(model_type)
        # 添加用户词典(法律文书大辞典与清华大学法律词典)，这种方式是添加进内存中，速度更快
        files = os.listdir(user_dict_dir)
        for file in files:
            file_path = os.path.join(user_dict_dir, file)
            # 文件夹则跳过
            if os.path.isdir(file):
                continue
            self.ltp.init_dict(file_path)

        # # 词性标注模型
        # self.postagger = Postagger()
        # postag_flag = self.postagger.load(os.path.join(self.default_model_dir, 'pos.model'))
        # # 命名实体识别模型
        # self.recognizer = NamedEntityRecognizer()
        # ner_flag = self.recognizer.load(os.path.join(self.default_model_dir, 'ner.model'))
        # # 依存句法分析模型
        # self.parser = Parser()
        # parse_flag = self.parser.load(os.path.join(self.default_model_dir, 'parser.model'))

    def segment(self, sentence, entity_postag=dict()):
        """采用NLPIR进行分词处理
        Args:
            sentence: string，句子
            entity_postag: dict，实体词性词典，默认为空集合，分析每一个案例的结构化文本时产生
        Returns:
            lemmas: list，分词结果
        """
        # 添加实体词典
        if entity_postag:
            for entity in entity_postag:
                self.ltp.add_words([entity])
        segment, hidden = self.ltp.seg([sentence])
        return segment[0], hidden

    def postag(self, segment, hidden):
        """对分词后的结果进行词性标注
        Args:
            segment: list，分词后的结果
        Returns:
            words: WordUnit list，包含分词与词性标注结果
        """
        words = []  # 存储句子处理后的词单元
        # 词性标注
        postags = self.ltp.pos(hidden)
        for i in range(len(segment)):
            # 存储分词与词性标记后的词单元WordUnit，编号从1开始
            word = WordUnit(i+1, segment[i], postags[0][i])
            words.append(word)
        return words

    def get_postag(self, word):
        """获得单个词的词性标注
        Args:
            word: str，单词
        Returns:
            post_tag: str，该单词的词性标注
        """
        _, hidden = self.ltp.seg([word], is_preseged=True)
        post_tag = self.ltp.pos(hidden)
        return post_tag[0]

    def netag(self, words, hidden):
        """命名实体识别，并对分词与词性标注后的结果进行命名实体识别与合并
        Args:
            words: WordUnit list，包含分词与词性标注结果
        Returns:
            words_netag: WordUnit list，包含分词，词性标注与命名实体识别结果
        """
        lemmas = []  # 存储分词后的结果
        postags = []  # 存储词性标书结果
        for word in words:
            lemmas.append(word.lemma)
            postags.append(word.postag)
        # 命名实体识别
        netags = self.ltp.ner(hidden, as_entities=False)
        words_netag = EntityCombine.combine(words, netags[0])
        return words_netag

    def parse_seged(self, words):
        lemmas = []  # 分词结果
        postags = []  # 词性标注结果
        for word in words:
            lemmas.append(word.lemma)
            postags.append(word.postag)
        # 依存句法分析
        _, hidden = self.ltp.seg([lemmas], is_preseged=True)
        arcs = self.ltp.dep(hidden)[0]
        for i in range(len(arcs)):
            words[i].head = arcs[i][1]
            words[i].dependency = arcs[i][2]
        return SentenceUnit(words)

    def parse(self, words, hidden):
        """对分词，词性标注与命名实体识别后的结果进行依存句法分析(命名实体识别可选)
        Args:
            words_netag: WordUnit list，包含分词，词性标注与命名实体识别结果
        Returns:
            *: SentenceUnit，该句子单元
        """
        lemmas = []  # 分词结果
        postags = []  # 词性标注结果
        for word in words:
            lemmas.append(word.lemma)
            postags.append(word.postag)
        # 依存句法分析
        arcs = self.ltp.dep(hidden)[0]
        for i in range(len(arcs)):
            words[i].head = arcs[i][1]
            words[i].dependency = arcs[i][2]
        return SentenceUnit(words)

    def close(self):
        """关闭与释放nlp"""
        pass


if __name__ == '__main__':
    nlp = NLP()
    # 分词测试
    print('***' + '分词测试' + '***')
    # sentence = '国家主席习近平视察中国福建厦门。'
    sentence = '奥巴马毕业于哈弗大学'
    lemmas = nlp.segment(sentence)
    # 输出：['国家主席', '习近平', '视察', '中国', '福建', '厦门', '。']
    print(lemmas)
    
    # 词性标注测试
    print('***' + '词性标注测试' + '***')
    words = nlp.postag(lemmas)
    for word in words:
        print(word.to_string())

    print('"中国"的词性: ' + nlp.get_postag('中国'))

    # 命名实体识别与合并测试
    print('***' + '命名实体识别测试' + '***')
    # 合并后的分词结果变为：['国家主席', '习近平', '视察', '中国福建厦门', '。']
    words_netag = nlp.netag(words)
    for word in words_netag:
        print(word.to_string())

    # 依存句法分析测试
    print('***' + '依存句法分析测试' + '***')
    sentence = nlp.parse(words_netag)
    print(sentence.to_string())
    print('sentence head: ' + sentence.words[0].head_word.lemma)
    
