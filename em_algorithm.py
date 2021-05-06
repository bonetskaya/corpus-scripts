#!/usr/bin/env python3

import argparse
import numpy as np
from scipy.special import xlogy
import itertools
from utils import (process_sentences, get_token_to_index,
                   sents_to_idx)


class SentencePair:
    """
    Contains lists of tokens (strings) for source and target sentence
    """
    ru: list[str]
    zh: list[str]


class IdxSentencePair:
    """
    Contains arrays of token vocabulary indices (preferably np.int32) for source and target sentence
    """
    ru: np.ndarray
    zh: np.ndarray


class WordAligner:
    def __init__(self, num_source_words, num_target_words, num_iters):
        self.num_source_words = num_source_words
        self.num_target_words = num_target_words
        self.translation_probs = np.full((num_source_words, num_target_words), 1 / num_target_words, dtype=np.float32)
        self.num_iters = num_iters

    def _e_step(self, parallel_corpus: list[IdxSentencePair]) -> list[np.array]:
        """
        Given a parallel corpus and current model parameters, get a posterior distribution over alignments for each
        sentence pair.

        Args:
            parallel_corpus: list of sentences with translations, given as numpy arrays of vocabulary indices

        Returns:
            posteriors: list of np.arrays with shape (ru_len, zh_len). posteriors[i][j][k] gives a posterior
            probability of zh token k to be aligned to ru token j in a sentence i.
        """
        posteriors = []
        for sentence_pair in parallel_corpus:
            # print(sentence_pair.source_tokens, sentence_pair.target_tokens)
            # print([np.ix_(sentence_pair.source_tokens, sentence_pair.target_tokens)])
            q = self.translation_probs[np.ix_(sentence_pair.ru, sentence_pair.zh)]
            q /= q.sum(0)
            posteriors.append(q)
        return posteriors

    def _compute_elbo(self, parallel_corpus: list[IdxSentencePair], posteriors: list[np.array]) -> float:
        """
        Compute evidence (incomplete likelihood) lower bound for a model given data and the posterior distribution
        over latent variables.

        Args:
            parallel_corpus: list of sentences with translations, given as numpy arrays of vocabulary indices
            posteriors: posterior alignment probabilities for parallel sentence pairs (see WordAligner._e_step).

        Returns:
            elbo: the value of evidence lower bound
        """
        elbo = 0

        for i in range(len(parallel_corpus)):
            sentence_pair = parallel_corpus[i]
            q = posteriors[i]

            theta = self.translation_probs[np.ix_(sentence_pair.ru, sentence_pair.zh)]
            elbo += (xlogy(q, theta) - xlogy(q, q)).sum()
            elbo -= xlogy(q.shape[1], q.shape[0])

        return elbo

    def _m_step(self, parallel_corpus: list[IdxSentencePair], posteriors: list[np.array]):
        """
        Update model parameters from a parallel corpus and posterior alignment distribution. Also, compute and return
        evidence lower bound after updating the parameters for logging purposes.

        Args:
            parallel_corpus: list of sentences with translations, given as numpy arrays of vocabulary indices
            posteriors: posterior alignment probabilities for parallel sentence pairs (see WordAligner._e_step).

        Returns:
            elbo:  the value of evidence lower bound after applying parameter updates
        """
        self.translation_probs = np.zeros((self.num_source_words, self.num_target_words))
        for i in range(len(parallel_corpus)):
            sentence_pair = parallel_corpus[i]
            q = posteriors[i]
            np.add.at(self.translation_probs,
                      np.ix_(sentence_pair.ru, sentence_pair.zh),
                      q)

        self.translation_probs /= self.translation_probs.sum(1).reshape(self.num_source_words, 1)
        return self._compute_elbo(parallel_corpus, posteriors)

    def fit(self, parallel_corpus):
        """
        Same as in the base class, but keep track of ELBO values to make sure that they are non-decreasing.
        Sorry for not sticking to my own interface ;)

        Args:
            parallel_corpus: list of sentences with translations, given as numpy arrays of vocabulary indices

        Returns:
            history: values of ELBO after each EM-step
        """
        history = []
        for i in range(self.num_iters):
            posteriors = self._e_step(parallel_corpus)
            elbo = self._m_step(parallel_corpus, posteriors)
            history.append(elbo)
        return history

    def align(self, sentences):
        alignments = []
        for sentence_pair in sentences:
            result = []
            for zh_word in sentence_pair.zh:
                max_val = 0
                i = 1
                for ru_word in sentence_pair.ru:
                    if self.translation_probs[ru_word][zh_word] > max_val:
                        max_val = self.translation_probs[ru_word][zh_word]
                        best_target = i
                    i += 1
                result.append(best_target)
            alignments.append(list(zip(result, itertools.count(1))))

        return alignments


parser = argparse.ArgumentParser(description="Get pharaoh alignment with EM-algorithm")
parser.add_argument("fit_filenames", nargs="+", type=str, help="русский ||| 中文 like filenames to fit")
parser.add_argument("-p", "--predict_filename", nargs=1, type=str, help="filename for prediction, fit_filenames if empty", default=[])


parser_args = parser.parse_args()
filenames = parser_args.fit_filenames
predict_filename = parser_args.predict_filename

all_sentences = process_sentences(predict_filename + filenames)

t_idx_src, t_idx_tgt = get_token_to_index(all_sentences)
tokenized_sentences = sents_to_idx(all_sentences, t_idx_src, t_idx_tgt)

word_aligner = WordAligner(len(t_idx_src), len(t_idx_tgt), 20)

word_aligner.fit(tokenized_sentences)
len_predict = len(tokenized_sentences) if len(predict_filename) == 0 else sum(1 for line in open(predict_filename[0]))
result = word_aligner.align(tokenized_sentences[:len_predict])
for sent in result:
    for pair in sent:
        print(f"{pair[0]}-{pair[1]}", end=" ")
    print()
