import collections
import numpy as np


class SentencePair:
    """
    Contains lists of tokens (strings) for source and target sentence
    """

    ru: list[str]
    zh: list[str]

    def __init__(self, ru, zh):
        self.ru = ru
        self.zh = zh


class IdxSentencePair:
    """
    Contains arrays of token vocabulary indices (preferably np.int32) for source and target sentence
    """
    ru: np.ndarray
    zh: np.ndarray

    def __init__(self, ru, zh):
        self.ru = ru
        self.zh = zh


def process_sentences(filenames: list[str]) -> list[SentencePair]:
    all_sentences = []
    for filename in filenames:
        with open(filename, "r") as f:
            for line in f:
                ru, zh = line.split("|||")
                ru = ru.split()
                zh = zh.split()
                if len(ru) == 0 or len(zh) == 0:
                    continue
                all_sentences.append(SentencePair(ru, zh))
    return all_sentences


def get_token_to_index(sentence_pairs: list[SentencePair], freq_cutoff=None) -> tuple[dict[str, int], dict[str, int]]:
    """
    Given a parallel corpus, create two dictionaries token->index for source and target language.
    """
    ru_cnt = collections.Counter()
    zh_cnt = collections.Counter()

    for sentence_pair in sentence_pairs:
        ru_cnt.update(sentence_pair.ru)
        zh_cnt.update(sentence_pair.zh)

    if freq_cutoff is None:
        freq_cutoff = max(len(ru_cnt), len(zh_cnt))

    source_list = [k[0] for k in ru_cnt.most_common(freq_cutoff)]
    target_list = [k[0] for k in zh_cnt.most_common(freq_cutoff)]

    return ({token: index for index, token in enumerate(source_list)},
            {token: index for index, token in enumerate(target_list)})


def sents_to_idx(sentence_pairs: list[SentencePair], source_dict, target_dict) -> list[IdxSentencePair]:
    """
    Given a parallel corpus and token_to_index for each language, transform each pair of sentences from lists
    of strings to arrays of integers. If either source or target sentence has no tokens that occur in corresponding
    token_to_index, do not include this pair in the result.
    """
    tokenized_sentence_pairs = []

    for sentence_pair in sentence_pairs:
        ru_idx = np.array(list(map(lambda x: source_dict.get(x, -1), sentence_pair.ru)))
        if np.any(ru_idx[ru_idx < 0]):
            continue

        zh_idx = np.array(list(map(lambda x: target_dict.get(x, -1), sentence_pair.zh)))
        if np.any(zh_idx[zh_idx < 0]):
            continue

        tokenized_sentence_pairs.append(IdxSentencePair(ru_idx, zh_idx))

    return tokenized_sentence_pairs



