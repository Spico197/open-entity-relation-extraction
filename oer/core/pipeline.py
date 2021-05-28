from .nlp import NLP
from .extractor import Extractor


class Pipeline:
    def __init__(self) -> None:
        self.nlp = NLP()

    def predict(self, string, more_common=True, verbose=True):
        # 分词处理
        lemmas, hidden = self.nlp.segment(string)
        # 词性标注
        words_postag = self.nlp.postag(lemmas, hidden)
        # sentence = nlp.parse(words_postag, hidden)
        # 命名实体识别
        words_netag = self.nlp.netag(words_postag, hidden)
        # 依存句法分析
        sentence = self.nlp.parse_seged(words_netag)
        if verbose:
            print(sentence.to_string())
        return Extractor.extract(string, sentence, more_common=more_common, verbose=verbose)
