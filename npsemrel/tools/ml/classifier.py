import sys
from ltlearn.classification.makers.maker import Maker

import ltcore.io.matrix as mio
import ltcore.transformations.makers.selection.selectionmaker as sm

weka_jar="/home/pkedzia/work/projects/npsemrel/3rdparty/weka-3-6-9/weka.jar:"\
"/home/pkedzia/work/projects/npsemrel/3rdparty/libsvm-3.17/java/libsvm.jar"

classifiers = [
	'weka.rules.decisiontable',
	'weka.bayes.naivebayes',
	'weka.trees.j48',
	'weka.trees.randomforest',
	'weka.svm.libsvm',
	'weka.nn.multilayerperceptron',
	'weka.functions.rbfnetwork',
	None
]

examples = [
	'example_01.tar.bz2',
	'example_02.tar.bz2',
	'example_03.tar.bz2',
	'example_03_obmsc.tar.bz2',
	'example_04.tar.bz2',
	'example_05.tar.bz2',
	None
]

sel_config = "/home/pkedzia/work/projects/npsemrel/cfg/selection.ini"
classification_config = "/home/pkedzia/work/projects/npsemrel/cfg/classification.ini"

def load_matrix(matrix_path):
	matrix = mio.load_matrix(matrix_path)

	'''
	selmak = sm.SelectionMaker()
	w = selmak.make_selection_from_config(sel_config)
	print >> sys.stderr, '\t\tMaking selection...',
	w.make(matrix_path)
	print >> sys.stderr, 'done!: ', w._selected_features
	'''

	return matrix

def learn():
	maker = Maker()

	for classifier_string in classifiers:
		if classifier_string == None:
			continue
		print >> sys.stderr, '=' * 80
		print >> sys.stderr, '[*] Classifier:', classifier_string

		for example in examples:
			if example == None:
				continue
			print >> sys.stderr, '\t[*]E Example:', example

			input_matrix = 'features/%s' % (example)
			classifier_model = 'features/%s_classifiermodel_%s' % (example.replace('.tar.bz2', ''), classifier_string)
			matrix = load_matrix(input_matrix)
			classifier = maker.make_classifier_from_cfg_string(classifier_string)
			classifier._weka_jar = weka_jar
			classifier.learn(matrix)
			classifier.serialize(classifier_model)

def learn2():
	maker = Maker()
	classifiers = maker.make_classifiers_from_config(classification_config)
	for classifier in classifiers:
		print >> sys.stderr, '=' * 80
		for example in examples:
			input_matrix = 'features/%s' % (example)
			# classifier_model = 'features/%s_classifiermodel_%s' % (example.replace('.tar.bz2', ''), classifier_string)
			matrix = load_matrix(input_matrix)
			classifier.learn(matrix)
		# classifier.serialize(classifier_model)

def classify():
	maker = Maker()

	for classifier_string in classifiers:
		if classifier_string == None:
			break

		for example in examples:
			input_matrix = 'features/%s' % (example)
			classifier_model = 'features/%s_classifiermodel_%s' % (example.replace('.tar.bz2', ''), classifier_string)
			
			classifier = maker.make_classifier_from_cfg_string(classifier_string)
			classifier.deserialize(classifier_model)
			
			print classifier_string, example
			print classifier.classify(input_matrix)

def main():
	learn()
	# learn2()
	# print classify()

if __name__ == '__main__':
	main()
