#  Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Example of Estimator for DNN-based text classification with DBpedia data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import re
import json
import argparse
import sys

from random import shuffle

import numpy as np
import pandas
from sklearn import metrics
import tensorflow as tf

FLAGS = None

MAX_DOCUMENT_LENGTH = 400
EMBEDDING_SIZE = 50
n_words = 0
MAX_LABEL = 1000
WORDS_FEATURE = 'words'  # Name of the input words feature.


def estimator_spec_for_softmax_classification(
    logits, labels, mode):
  """Returns EstimatorSpec instance for softmax classification."""
  predicted_classes = tf.argmax(logits, 1)
  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(
        mode=mode,
        predictions={
            'class': predicted_classes,
            'prob': tf.nn.softmax(logits)
        })

  onehot_labels = tf.one_hot(labels, MAX_LABEL, 1, 0)
  loss = tf.losses.softmax_cross_entropy(
      onehot_labels=onehot_labels, logits=logits)
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.AdamOptimizer(learning_rate=0.01)
    train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

  eval_metric_ops = {
      'accuracy': tf.metrics.accuracy(
          labels=labels, predictions=predicted_classes)
  }
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def bag_of_words_model(features, labels, mode):
  """A bag-of-words model. Note it disregards the word order in the text."""
  bow_column = tf.feature_column.categorical_column_with_identity(
      WORDS_FEATURE, num_buckets=n_words)
  bow_embedding_column = tf.feature_column.embedding_column(
      bow_column, dimension=EMBEDDING_SIZE, combiner="sum")
  bow = tf.feature_column.input_layer(
      features,
      feature_columns=[bow_embedding_column])
  logits = tf.layers.dense(bow, MAX_LABEL, activation=None)

  return estimator_spec_for_softmax_classification(
      logits=logits, labels=labels, mode=mode)


def rnn_model(features, labels, mode):
  """RNN model to predict from sequence of words to a class."""
  # Convert indexes of words into embeddings.
  # This creates embeddings matrix of [n_words, EMBEDDING_SIZE] and then
  # maps word indexes of the sequence into [batch_size, sequence_length,
  # EMBEDDING_SIZE].
  word_vectors = tf.contrib.layers.embed_sequence(
      features[WORDS_FEATURE], vocab_size=n_words, embed_dim=EMBEDDING_SIZE)

  # Split into list of embedding per word, while removing doc length dim.
  # word_list results to be a list of tensors [batch_size, EMBEDDING_SIZE].
  word_list = tf.unstack(word_vectors, axis=1)

  # Create a Gated Recurrent Unit cell with hidden size of EMBEDDING_SIZE.
  cell = tf.nn.rnn_cell.GRUCell(EMBEDDING_SIZE)

  # Create an unrolled Recurrent Neural Networks to length of
  # MAX_DOCUMENT_LENGTH and passes word_list as inputs for each unit.
  _, encoding = tf.nn.static_rnn(cell, word_list, dtype=tf.float32)

  # Given encoding of RNN, take encoding of last step (e.g hidden size of the
  # neural network of last step) and pass it as features for softmax
  # classification over output classes.
  logits = tf.layers.dense(encoding, MAX_LABEL, activation=None)
  return estimator_spec_for_softmax_classification(
      logits=logits, labels=labels, mode=mode)

import nltk
import os
stopwords = set(nltk.corpus.stopwords.words('french'))
stopwords.update([w[0:-1] for w in open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'french-stopwords.txt'))][1:])
stopwords.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '\'', '\'\'', '``', '`', '»', '«', '...'])
def preprocess(text):
  stemmer = nltk.SnowballStemmer('french')

  data = nltk.word_tokenize(text.replace('\n', ' '))
  data = [t.lower() for t in data if t.lower() not in stopwords]
  #data = [re.sub(r"^(d|l|qu|c|s)'", '', w) for w in data if not re.match(r"^(\d+|\.)$", w)]
  #data = [re.sub(r"^(d|l|qu|c|s)'", '', w) for w in data]
  #data = [w for w in data if not re.match(r"^(\d+|\.)$", w)]
  data = [stemmer.stem(t) for t in data]

  return ' '.join(data)

def read_book(filename):
  with open(filename) as f:
    return [{'is_confirmed': False, 'text': p} for p in f.read().split('***', 2)[2].split('\n\n')]

def main(unused_argv):
  global n_words
  tf.logging.set_verbosity(tf.logging.INFO)

  with open('./2017-11-29-all-classified.json') as f:
    data = json.load(f)

    #split = int(len(data) * 0.8)
    #train = data[split:]
    #test = data[:split]
    train = data
    for book in glob.glob('data/books/*.txt'):
      train = train + read_book(book)

    #related = [a for a in data if a['is_confirmed']]
    #unrelated = [a for a in data if not a['is_confirmed']]
    #even = min(len(related), len(unrelated))
    #train = related[0:even] + unrelated[0:even]
    #shuffle(train)

    with open('./2017-11-29-test.json') as f2: test = [a for a in json.load(f2) if a['is_confirmed'] is not None]

    print("Related: " + str(len([1 for a in train if a['is_confirmed']])))
    print("Unrelated: " + str(len([1 for a in train if not a['is_confirmed']])))

    train_data = np.array([preprocess(a['text']) for a in train], np.str)
    train_target = np.array([int(a['is_confirmed']) for a in train], np.int32)
    test_data = np.array([preprocess(a['text']) for a in test], np.str)
    test_target = np.array([int(a['is_confirmed']) for a in test], np.int32)

  #for d in zip(test_target, test_data):
  #  print("---> %s : %s" % (d[0], d[1]))

  x_train = pandas.Series(train_data)
  y_train = pandas.Series(train_target)
  x_test = pandas.Series(test_data)
  y_test = pandas.Series(test_target)

  # Process vocabulary
  vocab_processor = tf.contrib.learn.preprocessing.VocabularyProcessor(
      MAX_DOCUMENT_LENGTH)

  x_transform_train = vocab_processor.fit_transform(x_train)
  x_transform_test = vocab_processor.transform(x_test)

  x_train = np.array(list(x_transform_train))
  x_test = np.array(list(x_transform_test))

  n_words = len(vocab_processor.vocabulary_)
  print('Total words: %d' % n_words)

  # define inputs
  train_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={WORDS_FEATURE: x_train},
      y=y_train,
      batch_size=len(x_train),
      num_epochs=None,
      shuffle=True)
  test_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={WORDS_FEATURE: x_test},
      y=y_test,
      num_epochs=1,
      shuffle=False)

  # Build model
  # Switch between rnn_model and bag_of_words_model to test different models.
  model_fn = rnn_model
  if FLAGS.bow_model:
    # Subtract 1 because VocabularyProcessor outputs a word-id matrix where word
    # ids start from 1 and 0 means 'no word'. But
    # categorical_column_with_identity assumes 0-based count and uses -1 for
    # missing word.
    x_train -= 1
    x_test -= 1
    model_fn = bag_of_words_model
  classifier = tf.estimator.Estimator(model_fn=model_fn)

  # Train.
  classifier.train(input_fn=train_input_fn, steps=100)

  # Predict.
  predictions = classifier.predict(input_fn=test_input_fn)

  # Print some
  y_predicted = np.array(list(p['class'] for p in predictions))
  y_predicted = y_predicted.reshape(np.array(y_test).shape)
  print('Y TEST:')
  print(y_test)
  print('Y PREDICT:')
  print(y_predicted)

  # Score
  scores = classifier.evaluate(input_fn=test_input_fn)
  print('Accuracy (tensorflow): {0:f}'.format(scores['accuracy']))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--bow_model',
      default=True,
      help='Run with BOW model instead of RNN.',
      action='store_true')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
