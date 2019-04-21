#! /usr/bin/env python
# -*- coding: UTF-8 -*-


'''
###############################################################################################
\t Tersor-Flowun sağladığı word2Vec kodunun ucuncu versiyonu
 config.json dosyının icierindeki veriyi degistirdigşimizde kodun calısma paramtreleri degisecektir.

 * simple Usage *
 python3.6 word2_vec_basis_VER3.py               ->Runs for './Input_Text/*.txt' files and './config.json'

                                                                                          -uluc
###############################################################################################
'''

# Needed Libs

from __future__ import division
from __future__ import print_function

import collections
import math
import os
import sys
import argparse
import random
from tempfile import gettempdir
import zipfile

import numpy as np
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from tensorflow.contrib.tensorboard.plugins import projector
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import json
import glob

def Visualize(final_embeddings,reverse_dictionary,log_path):
	try:
		# pylint: disable=g-import-not-at-top
		tsne = TSNE(
		  perplexity=30, n_components=2, init='pca', n_iter=5000, method='exact')
		plot_only = 500
		low_dim_embs = tsne.fit_transform(final_embeddings[:plot_only, :])
		print (final_embeddings[:1, :10])
		labels = [reverse_dictionary[i] for i in xrange(plot_only)]
		plot_with_labels(low_dim_embs, labels, os.path.join(log_path,'tsne.png'))
		#plot_with_labels(low_dim_embs, labels, os.path.join(gettempdir(), 'tsne.png'))
	except ImportError as ex:
		print('Please install sklearn, matplotlib, and scipy to show embeddings.')
		print(ex)

def plot_with_labels(low_dim_embs, labels, filename):
  assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
  plt.figure(figsize=(18, 18))  # in inches
  for i, label in enumerate(labels):
    x, y = low_dim_embs[i, :]
    plt.scatter(x, y)
    plt.annotate(
        label,
        xy=(x, y),
        xytext=(5, 2),
        textcoords='offset points',
        ha='right',
        va='bottom')

  plt.savefig(filename)

def creation_of_log():
	#code path
	current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
	log_path = os.path.join(current_path, 'log')
	# Create the directory for TensorBoard variables if there is not.
	if not os.path.exists(log_path):
		os.makedirs(log_path)

	config = open('./config.json','r')
	config = config.readlines()
	config = json.loads(' '.join( config) )
	print ('okunan parametreler : \n',json.dumps(config,indent = 4))
	return log_path,config

def read_data_from(path):
	# path = './Input_Text/*.txt'
	## glob gives us the macher paths
	paths = glob.glob(path)
	data = []
	for one_path in paths:
		print ('Read file ,', one_path)
		with open(one_path,'r') as f:
			data = data + (' '.join(f.readlines())).split()
	return data

def build_dataset(words, n_words):
	''' Counter object stores pairs
		 		word1  : frequency ,
		 		word2  : frequency
		 most_common n_words will be stored
	'''
	## uniq words and counts
	count = [('UNK', -1)]
	count.extend(collections.Counter(words).most_common(n_words - 1))
	# ----------------------

	## Every word needs a numeric value!!
	## according to the frequency, every word convert a number
	dictionary = {}
	for i, (word, frequency) in enumerate(count):
		dictionary[word] = i
	# ----------------------
	## Also every numeric value can be reTransform to a word
	reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
	# ----------------------

	## our text input has words but our data set must be converted to numbers
	## according to dictionary every word has a numberic value and our text input
	## can be corverted to a numberic input --- next code do that
	data_as_numeric = []
	unk_count = 0 # means how meany miss word in the text according to first common n_words
	for one_word_in_input in words:
		numeric_value_of_the_word = dictionary.get(one_word_in_input, 0) # if word is not in the first n_words doesn't have a numberic value so default is '0'
		if numeric_value_of_the_word == 0:
			unk_count += 1
		data_as_numeric.append(numeric_value_of_the_word)
	count= [('UNK',unk_count)]
	# ----------------------

	'''
	data_as_numeric -> All transform data to  numeric rep.
	count -> first n_word frequency collection 
	dictionary -> word 2 numeric value map 
	reversed_dictionary -> numeric 2 word value map 
	'''
	return data_as_numeric, count, dictionary, reversed_dictionary

def generate_batch(batch_size, num_skips, skip_window):
	global data
	global count
	global dictionary
	global reverse_dictionary

	global data_index
	assert batch_size % num_skips == 0 ## to throw exception
	assert num_skips <= 2 * skip_window ## to throw exception

	batch = np.ndarray(shape=(batch_size), dtype=np.int32)
	labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
	span = 2 * skip_window + 1  # [ skip_window target skip_window ]
	buffer = collections.deque(maxlen=span)  # pylint: disable=redefined-builtin	

	if data_index + span > len(data):
		data_index = 0
	buffer.extend(data[data_index:data_index + span])
	data_index += span
	for i in range(batch_size // num_skips):
		context_words = [w for w in range(span) if w != skip_window]
		words_to_use = random.sample(context_words, num_skips)
		for j, context_word in enumerate(words_to_use):
			batch[i * num_skips + j] = buffer[skip_window]
			labels[i * num_skips + j, 0] = buffer[context_word]
		if data_index == len(data):
			buffer.extend(data[0:span])
			data_index = span
		else:
			buffer.append(data[data_index])
			data_index += 1
	# Backtrack a little bit to avoid skipping words in the end of a batch
	data_index = (data_index + len(data) - span) % len(data)
	return batch, labels	

def setup_():
	global batch_size
	global embedding_size
	global skip_window
	global num_skips
	global num_sampled
	global valid_size
	global valid_window
	global valid_examples	
	graph = tf.Graph()

	with graph.as_default():
		# Input data.
		with tf.name_scope('inputs'):
			train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
			train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
			valid_dataset = tf.constant(valid_examples, dtype=tf.int32)
		# Ops and variables pinned to the CPU because of missing GPU implementation
		with tf.device('/cpu:0'):
			# Look up embeddings for inputs.
			with tf.name_scope('embeddings'):
				embeddings = tf.Variable( tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0) )
				embed = tf.nn.embedding_lookup(embeddings, train_inputs)

			# Construct the variables for the NCE loss
			with tf.name_scope('weights'):
				nce_weights = tf.Variable( tf.truncated_normal( [vocabulary_size, embedding_size], stddev=1.0 / math.sqrt(embedding_size)))
			with tf.name_scope('biases'):
				nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

		# Compute the average NCE loss for the batch.
		# tf.nce_loss automatically draws a new sample of the negative labels each
		# time we evaluate the loss.
		# Explanation of the meaning of NCE loss:
		#   http://mccormickml.com/2016/04/19/word2vec-tutorial-the-skip-gram-model/
		with tf.name_scope('loss'):
			loss = tf.reduce_mean( tf.nn.nce_loss(
										weights=nce_weights,
										biases=nce_biases,
										labels=train_labels,
										inputs=embed,
										num_sampled=num_sampled,
										num_classes=vocabulary_size))

		# Add the loss value as a scalar to summary.
		tf.summary.scalar('loss', loss)

		# Construct the SGD optimizer using a learning rate of 1.0.
		with tf.name_scope('optimizer'):
			optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

		# Compute the cosine similarity between minibatch examples and all embeddings.
		norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keepdims=True))
		normalized_embeddings = embeddings / norm
		valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings,
		                                        valid_dataset)
		similarity = tf.matmul(
		  	valid_embeddings, normalized_embeddings, transpose_b=True)

		# Merge all summaries.
		merged = tf.summary.merge_all()

		# Add variable initializer.
		init = tf.global_variables_initializer()

		# Create a saver.
		saver = tf.train.Saver()

	return graph, loss,optimizer, normalized_embeddings, similarity, merged, init, saver, train_inputs, train_labels, valid_dataset, embeddings

def train_(num_steps,log_path, graph, loss, optimizer, normalized_embeddings, similarity, merged, init, saver, train_inputs, train_labels, valid_dataset, embeddings):
	global batch_size
	global embedding_size
	global skip_window
	global num_skips
	global num_sampled
	global valid_size
	global valid_window
	global valid_examples	
	with tf.Session(graph = graph) as session:
		# Open a writer to write summaries.
		writer = tf.summary.FileWriter(log_path, session.graph)

		# We must initialize all variables before we use them.
		init.run()
		print('Initialized')

		average_loss = 0
		for step in xrange(num_steps):
			batch_inputs, batch_labels = generate_batch(batch_size, num_skips, skip_window)
			feed_dict = { train_inputs: batch_inputs, train_labels: batch_labels }

			# Define metadata variable.
			run_metadata = tf.RunMetadata()

			# We perform one update step by evaluating the optimizer op (including it
			# in the list of returned values for session.run()
			# Also, evaluate the merged op to get all summaries from the returned "summary" variable.
			# Feed metadata variable to session for visualizing the graph in TensorBoard.
			_, summary, loss_val = session.run(
			    [optimizer, merged, loss],
			    feed_dict=feed_dict,
			    run_metadata=run_metadata)
			average_loss += loss_val

			# Add returned summaries to writer in each step.
			writer.add_summary(summary, step)

			# Add metadata to visualize the graph for the last run.
			if step == (num_steps - 1):
				writer.add_run_metadata(run_metadata, 'step%d' % step)

			if step % 2000 == 0:
				if step > 0:
					average_loss /= 2000
					# The average loss is an estimate of the loss over the last 2000 batches.
					print('Average loss at step ', step, ': ', average_loss)
					average_loss = 0

			# Note that this is expensive (~20% slowdown if computed every 500 steps)
			if step % 10000 == 0:
				sim = similarity.eval()
				for i in xrange(valid_size):
					valid_word = reverse_dictionary[valid_examples[i]]
					top_k = 8  # number of nearest neighbors
					nearest = (-sim[i, :]).argsort()[1:top_k + 1]
					log_str = 'Nearest to %s:' % valid_word
					for k in xrange(top_k):
						close_word = reverse_dictionary[nearest[k]]
						log_str = '%s %s,' % (log_str, close_word)
					print(log_str)
		final_embeddings = normalized_embeddings.eval()

			# Write corresponding labels for the embeddings.
		with open(log_path + '/metadata.tsv', 'w') as f:
			for i in xrange(vocabulary_size):
				f.write(reverse_dictionary[i] + '\n')

			# Save the model for checkpoints.
		saver.save(session, os.path.join(log_path, 'model.ckpt'))

		# Create a configuration for visualizing embeddings with the labels in TensorBoard.
		config = projector.ProjectorConfig()
		embedding_conf = config.embeddings.add()
		embedding_conf.tensor_name = embeddings.name
		embedding_conf.metadata_path = os.path.join(log_path,'metadata.tsv')
		projector.visualize_embeddings(writer, config)
	writer.close()
	return final_embeddings

def main():
	log_path, config = creation_of_log()

	#---reading
	filename = './Input_Text/*.txt'
	vocabulary = read_data_from(filename)
	print('Data size', len(vocabulary))

	#---counting and transform to numeric value
	global vocabulary_size
	vocabulary_size = config['vocabulary_size']
	global data
	global count
	global dictionary
	global reverse_dictionary
	data, count, dictionary, reverse_dictionary = build_dataset( vocabulary, vocabulary_size)
	del vocabulary  # Hint to reduce memory.
	print('Most common words (+UNK)', count[:5])
	print('Sample data', data[:10], [reverse_dictionary[i] for i in data[:10]])

	#---- generate a training batch for the skip-gram model
	
	global data_index
	data_index = 0	
	generating_batch_size = config['generating_batch_size']
	generating_num_skips = config['generating_num_skips']
	generating_skip_window = config['generating_skip_window']
	batch, labels = generate_batch(batch_size=generating_batch_size, num_skips=generating_num_skips, skip_window=generating_skip_window)
	for i in range(8):
		print(batch[i], reverse_dictionary[batch[i]], '->', labels[i, 0], reverse_dictionary[labels[i, 0]])
	
	##---
	global batch_size
	global embedding_size
	global skip_window
	global num_skips
	global num_sampled
	global valid_size
	global valid_window
	global valid_examples
	batch_size = config['batch_size']
	embedding_size = config['embedding_size']      # Dimension of the embedding vector.
	skip_window = config['skip_window']           # How many words to consider left and right.
	num_skips = config['num_skips']             # How many times to reuse an input to generate a label.
	num_sampled = config['num_sampled']          # Number of negative examples to sample.

	# We pick a random validation set to sample nearest neighbors. Here we limit the
	# validation samples to the words that have a low numeric ID, which by
	# construction are also the most frequent. These 3 variables are used only for
	# displaying model accuracy, they don't affect calculation.
	valid_size = config['valid_size']     # Random set of words to evaluate similarity on.
	valid_window = config['valid_window']  # Only pick dev samples in the head of the distribution.
	valid_examples = np.random.choice(valid_window, valid_size, replace=False)	

	#---Build a skip-gram model.
	graph, loss, optimizer, normalized_embeddings, similarity, merged, init, saver, train_inputs, train_labels, valid_dataset,embeddings = setup_()
	#---Begin training.
	num_steps = config['num_steps']
	final_embeddings = train_(num_steps,log_path, graph, loss, optimizer, normalized_embeddings, similarity, merged, init, saver, train_inputs, train_labels, valid_dataset,embeddings)

	# ---  Visualize the embeddings.
	Visualize(final_embeddings,reverse_dictionary,log_path)

if __name__ == "__main__":
	print (__doc__)
	main()



