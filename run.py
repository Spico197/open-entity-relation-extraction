import os
import re

from oer.core.nlp import NLP
from oer.core.extractor import Extractor
from oer.core.pipeline import Pipeline


def predict_file(input_path, output_path):
    if os.path.isfile(output_path):
        os.remove(output_path)

    print('Start extracting...')

    # 实例化NLP(分词，词性标注，命名实体识别，依存句法分析)
    nlp = NLP()
    num = 1  # 知识三元组

    with open(input_path, 'r', encoding='utf-8') as f_in:
        # 分句，获得句子列表
        origin_sentences = re.split('[。？！；]|\n', f_in.read())
        # 遍历每一篇文档中的句子
        for origin_sentence in origin_sentences:
            # 原始句子长度小于6，跳过
            if (len(origin_sentence) < 6):
                continue
            print('*****')
            # print(origin_sentence)
            # 分词处理
            lemmas, hidden = nlp.segment(origin_sentence)
            # 词性标注
            words_postag = nlp.postag(lemmas, hidden)
            # sentence = nlp.parse(words_postag, hidden)
            # 命名实体识别
            words_netag = nlp.netag(words_postag, hidden)
            # 依存句法分析
            sentence = nlp.parse_seged(words_netag)
            print(sentence.to_string())

            Extractor.extract(origin_sentence, sentence, file_path=output_path, verbose=True)


if __name__ == '__main__':
    # input_path = 'data/input_text.txt'  # 输入的文本文件
    # output_path = 'data/knowledge_triple.json'  # 输出的处理结果Json文件
    # predict_file(input_path, output_path)

    pipeline = Pipeline()
    results = pipeline.predict("高克访问中国，并在同济大学发表演讲。", more_common=False, verbose=False)
    print(results)
    results = pipeline.predict("奥巴马毕业于哈佛大学。", more_common=False, verbose=False)
    print(results)
