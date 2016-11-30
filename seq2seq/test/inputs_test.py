"""
Unit tests for input-related operations.
"""


import tensorflow as tf
import numpy as np

from seq2seq import inputs
from seq2seq.test import utils as test_utils

class ReadFromDataProviderTest(tf.test.TestCase):
  """
  Tests Data Provider operations.
  """

  def test_read_from_data_provider(self):
    file = test_utils.create_temp_tfrecords(source="Hello World .", target="Bye")
    data_provider = inputs.make_data_provider([file.name], num_epochs=5)
    features = inputs.read_from_data_provider(data_provider)

    with self.test_session() as sess:
      sess.run(tf.global_variables_initializer())
      sess.run(tf.local_variables_initializer())
      with tf.contrib.slim.queues.QueueRunners(sess):
        res = sess.run(features)

    self.assertEqual(res["source_len"], 3)
    self.assertEqual(res["target_len"], 1)
    np.testing.assert_array_equal(res["source_tokens"].astype("U"), ["Hello", "World", "."])
    np.testing.assert_array_equal(res["target_tokens"].astype("U"), ["Bye"])


class CreateVocabularyLookupTableTest(tf.test.TestCase):
  """
  Tests Vocabulary lookup table operations.
  """

  def setUp(self):
    super(CreateVocabularyLookupTableTest, self).setUp()
    self.vocab_list = ["Hello", ".", "Bye"]
    self.vocab_file = test_utils.create_temporary_vocab_file(self.vocab_list)

  def tearDown(self):
    super(CreateVocabularyLookupTableTest, self).tearDown()
    self.vocab_file.close()

  def test_lookup_table(self):

    vocab_to_id_table, id_to_vocab_table, vocab_size = \
      inputs.create_vocabulary_lookup_table(self.vocab_file.name)

    self.assertEqual(vocab_size, 3)

    with self.test_session() as sess:
      sess.run(tf.global_variables_initializer())
      sess.run(tf.local_variables_initializer())
      sess.run(tf.initialize_all_tables())

      ids = vocab_to_id_table.lookup(tf.convert_to_tensor(["Hello", ".", "Bye", "??", "xxx"]))
      ids = sess.run(ids)
      np.testing.assert_array_equal(ids, [0, 1, 2, 3, 3])

      words = id_to_vocab_table.lookup(tf.convert_to_tensor([0, 1, 2, 3], dtype=tf.int64))
      words = sess.run(words)
      np.testing.assert_array_equal(words.astype("U"), ["Hello", ".", "Bye", "UNK"])


if __name__ == "__main__":
  tf.test.main()
