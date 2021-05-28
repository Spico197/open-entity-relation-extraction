from oer.bean.entity_pair import EntityPair
from oer.core.extract_by_dsnf import ExtractByDSNF


class Extractor:
    """抽取生成知识三元组
    Attributes:
        entities: WordUnit list，句子的实体列表
        entity_pairs: EntityPair WordUnit list，句子实体对列表
    """
    @classmethod
    def extract(cls, origin_sentence, sentence, more_common=True, file_path=None, verbose=False):
        """
        Args:
            origin_sentence: string，原始句子
            sentence: SentenceUnit，句子单元
        """
        entities = cls.get_entities(sentence, more_common=more_common)
        entity_pairs = cls.get_entity_pairs(entities, sentence)
        results = []
        for entity_pair in entity_pairs:
            entity1 = entity_pair.entity1
            entity2 = entity_pair.entity2

            extract_dsnf = ExtractByDSNF(origin_sentence, sentence, entity1, entity2, file_path, verbose)
            # [DSNF2|DSNF7]，部分覆盖[DSNF5|DSNF6]
            obj = extract_dsnf.SBV_VOB(entity1, entity2)
            if obj:
                results.append(obj)
            # [DSNF4]
            obj = extract_dsnf.SBV_CMP_POB(entity1, entity2)
            if obj:
                results.append(obj)
            obj = extract_dsnf.SBVorFOB_POB_VOB(entity1, entity2)
            if obj:
                results.append(obj)
            # [DSNF1]
            # if not extract_dsnf.E_NN_E(entity1, entity2):
            #     pass
            # [DSNF3|DSNF5|DSNF6]，并列实体中的主谓宾可能会包含DSNF3
            obj = extract_dsnf.coordinate(entity1, entity2)
            if obj:
                results.append(obj)
            # ["的"短语]
            obj = extract_dsnf.entity_de_entity_NNT(entity1, entity2)
            if obj:
                results.append(obj)
        return {
            "sentence": origin_sentence,
            "knowledge": results
        }

    @classmethod
    def get_entities(cls, sentence, more_common=True):
        """获取句子中的所有可能实体
        Args:
            sentence: SentenceUnit，句子单元
        Returns:
            None
        """
        entities = []
        for word in sentence.words:
            if cls.is_entity(word, more_common=more_common):
                entities.append(word)
        return entities

    @classmethod
    def get_entity_pairs(cls, entities, sentence):
        """组成实体对，限制实体对之间的实体数量不能超过4
        Args:
            sentence: SentenceUnit，句子单元
        """
        entity_pairs = []
        length = len(entities)
        i = 0
        while i < length:
            j = i + 1
            while j < length:
                if (entities[i].lemma != entities[j].lemma and 
                    cls.get_entity_num_between(entities[i], entities[j], sentence) <= 4):
                    entity_pairs.append(EntityPair(entities[i], entities[j]))
                j += 1
            i += 1
        return entity_pairs

    @classmethod
    def is_entity(cls, entry, more_common=True):
        """判断词单元是否实体
        Args:
            entry: WordUnit，词单元
            more_common：是否包含一般名词
        Returns:
            *: bool，实体(True)，非实体(False)
        References:
            nh：人名
            ni：机构名
            ns：地名
            nz：奖项名
            j：缩写名，如：公检法
            n：一般名词
            nl：一般地名，如“城郊”、“国内”
        """
        entity_postags = {'nh', 'ni', 'ns', 'nz', 'j'}
        if more_common:
            entity_postags.update({'n', 'nl'})
        if entry.postag in entity_postags:
            return True
        else:
            return False

    @classmethod
    def get_entity_num_between(cls, entity1, entity2, sentence):
        """获得两个实体之间的实体数量
        Args:
            entity1: WordUnit，实体1
            entity2: WordUnit，实体2
        Returns:
            num: int，两实体间的实体数量
        """
        num = 0
        i = entity1.ID + 1
        while i < entity2.ID:
            if cls.is_entity(sentence.words[i]):
                num += 1
            i += 1
        return num
