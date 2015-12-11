##
# File: kmeans.py
# ---------------
#
##

import collections, copy
import numpy, scipy, math, random
import os, importlib
import json, unicodedata
import pdb

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction import DictVectorizer
# import matplotlib.pyplot as plt
from lib import util
from lib import constants as c

COMMAND_LINE = ""
MEATY_IMPLEMENTATION = 2

# NOTE
# K-Means
#     1a. Cluster recipes together based on
#         - flavors
#         - course/meal
#         - common ingredients
#         - subsets of common ingredients like spices, meats, sweets
#         - cooking time
#         - total calories
#         - % calories from fat
#         - # ingredients
#         - average ingredient line length
#     1b. Cluster ingredients together based on
#         - common ingredient/alias buddies 
#           (implemented like synonyms from 107)
#     2.  After clustering
#         - Manually label clusters as mexican/meats/breakfast/etc.

# Nut recipes, meat recipes (checkout json file)
# Try to cluster on fewer features, very few at a time
# Name clusters (automatic labeling)
# Output stuff to JSON file , dump json dict

##
# Function: testDatapoints
# -------------
# Example code to show necessary collection manipulation
# and to test KMeans algorithm. Not used in production code.
##
def testDatapoints():
	# sparse matrix, shape = (n_samples, n_features)
	allPoints = [
		{'0':0, '1':0},
		{'0':2, '1':0},
		{'0':10, '1':0},
		{'0':12, '1':0},
		]

	vec = DictVectorizer()
	dataMatrix = vec.fit_transform(allPoints)

	return dataMatrix

def cuisinePoint(point, cuisine):
	if cuisine is not None and len(cuisine) > 0:
		for cui in cuisine:
			point['cuisine-' + cui] = 1

def meatyPoint(point, ingredients, recipeName):
	if MEATY_IMPLEMENTATION in [1, 2, 3]:
		meatyCount = 0
		for alias in ingredients:
			if util.meatStringQ(alias):
				meatyCount += 1

		# Implementation 1: % of ingredients that are meaty
		if MEATY_IMPLEMENTATION == 1:
			point['meaty'] = float(meatyCount)/len(ingredients) * 100

		# Implementation 2: num of ingredients that are meaty
		if MEATY_IMPLEMENTATION == 2:
			point['meaty'] = float(meatyCount)*20

		# Implementation 3: num of ingredients + recipe name that are meaty
		if MEATY_IMPLEMENTATION == 3:
			for word in recipeName.split():
				if util.meatStringQ(word.lower()):
					meatyCount += 1
			point['meaty'] = float(meatyCount)*20

def flavorPoint(point, flavors, flavorsList):
	# Implementation 0: Flavor Feature with Yummly
	for flavorFeature in flavorsList:
		if flavors is not None and len(flavors) > 0:
			point[flavorFeature] = flavors[flavorFeature] * 100
		else:
			point[flavorFeature] = -100

def getListIntersections(list1, list2):
	result = set(list1).intersection(list2)
	return list(result)

##
# Function: createPoint
# -------------
# Given a recipe, it scrapes the important features used
# in the kmean clustering, and creates a "point", which is 
# a dictionary of featureName -> featureValue. The point
# is then returned.
##
def createPoint(recipe, featureList):
	point = {}

	recipeName = recipe['recipeName']
	cuisine = recipe.get('cuisine')
	flavors = recipe.get('flavors')
	ingredients = recipe['ingredients']

	if c.KMEANS_FEATURE_CUISINE in featureList:
		cuisinePoint(point, cuisine)

	if c.KMEANS_FEATURE_MEATY in featureList:
		meatyPoint(point, ingredients, recipeName)

	flavorsList = getListIntersections(featureList, c.KMEANS_FLAVOR_FEATURES)
	if len(flavorsList) > 0:
		flavorPoint(point, flavors, flavorsList)

	# point['totalTimeInSeconds'] = recipe['totalTimeInSeconds']
	# point['numIngredients'] = len(ingredients)

	# for ingredient in ingredients:
	# 	point['ingredient-'+ingredient] = 1

	return point

##
# Function: createRecipeDatapoints
# -------------
# Opens the specified jsonDataFilePath, and does collection 
# manipulation to create sparse matrixes, which is the form
# used by the KMeans class. Returns such matrix together with
# a dict that maps the orderNumber -> recipeName.
#
# Collection manipulations:
# 1) Get dict of dict from the JSON file with loadJSONDict()
# 2) Transform in list of dict, which contains all
#    relevant features (which need to be in string or
#	 number form)
# 3) Creates sparse matrix using DictVectorizer()
##
def createRecipeDatapoints(jsonDataFilePath, featureList):
	# sparse matrix, shape = (n_samples, n_features)
	allPoints = []
	countToRecipeName = {}

	allRecipes = util.loadJSONDict(jsonDataFilePath)

	count = 0
	for recipeName, recipe in allRecipes.items():
		point = createPoint(recipe, featureList)
		allPoints.append(point)
		countToRecipeName[count] = recipeName
		count += 1

	vec = DictVectorizer()
	dataMatrix = vec.fit_transform(allPoints)

	return dataMatrix, countToRecipeName, allPoints

##
# Function: createAliasDatapoints
# -------------
##
def createAliasDatapoints(jsonDataFilePath, featureList):
	raise Exception("createAliasDatapoints Not implemented yet")

##
# Function: clusterAssignment
# -------------
# Maps each recipe to its cluster and stores that in
# a cluster -> recipeNameList dict, which is returned.
##
def clusterAssignment(est, countToRecipeName, allPoints, featureList):
	clusterToRecipes = {}
	clusterStats = {}
	labels = est.labels_
	numtypeFeatures = getListIntersections(featureList, c.KMEANS_NUM_FEATURES)

	for count, recipeName in countToRecipeName.iteritems():
		cluster = "Cluster " + str(labels[count])
		
		clusterRecipeList = clusterToRecipes.get(cluster)
		if clusterRecipeList is None:
			clusterRecipeList = []
		clusterRecipeList.append(recipeName)
		clusterToRecipes[cluster] = clusterRecipeList

		for numtypeFeature in numtypeFeatures:
			clusterData = clusterStats.get(cluster)
			if clusterData is None:
				clusterData = {}
			fv = clusterData.get(numtypeFeature)
			if fv is None:
				clusterData[numtypeFeature] = 0
			
			point = allPoints[count]
			pointNum = point.get(numtypeFeature) # WATCH OUT for this here! What about ones with variable names?
			if pointNum is None:
				pointNum = -1
			clusterData[numtypeFeature] = clusterData[numtypeFeature] + pointNum
			clusterStats[cluster] = clusterData

	if len(numtypeFeatures) > 0:
		for cluster, clusterData in clusterStats.iteritems():
			for numtypeFeature, sumPoints in clusterData.iteritems():
				numPoints = len(clusterToRecipes[cluster])
				clusterData[numtypeFeature] = sumPoints/float(numPoints)

	return clusterToRecipes, clusterStats

##
# Function: printClusters
# -------------
# Prints which recipes where in which clusters.
##
def printClusters(clusterToRecipes, clusterStats, est, dataType, featureList):
	dict2dump = copy.deepcopy(clusterToRecipes)

	for cluster, recipeList in clusterToRecipes.iteritems():
		print 10 * '-' + cluster + ' '+ 10 * '-'
		clusterData = clusterStats[cluster]
		for numtypeFeature, sumPoints in clusterData.iteritems():
			dict2dump[cluster + ' ' + numtypeFeature + ' score'] = sumPoints
			print "The cluster's %s score was: %f" % (numtypeFeature, sumPoints)
		
		print
		for recipe in recipeList:
			print recipe
		print

	dict2dump['command-line'] = COMMAND_LINE

	tempFilename = dataType + '-cluster-'
	for f in featureList:
		tempFilename = tempFilename + f + '&'
	if tempFilename[-1] == '&':
		tempFilename = tempFilename[:-1]
	toFilename = util.string_appendDateAndTime(tempFilename)
	
	if dataType == c.KMEANS_RECIPE_DATATYPE:
		jsonToFilePath = os.path.join(c.PATH_TO_ROOT, "res/kmeans-results/recipe", toFilename)
	if dataType == c.KMEANS_ALIAS_DATATYPE:
		jsonToFilePath = os.path.join(c.PATH_TO_ROOT, "res/kmeans-results/alias", toFilename)

	util.dumpJSONDict(jsonToFilePath, dict2dump)
	print 'Clustering dumped into: ' + jsonToFilePath
	
# NOT WORKING YET
def drawClusters(dataMatrix, pred):
	plt.figure(figsize=(12, 12))
	plt.title("Recipe Clusters")
	plt.scatter(dataMatrix[:, 0], dataMatrix[:, 1], c=pred)
	plt.show()

##
# Function: cluster
# -------------
# Cluster the recipes in the jsonDataFilePath into K clusters and
# prints which recipes where in what clusters afterwards.
##
def cluster(jsonDataFilePath, K, dataType, featureList):
	'''
	datapoints: list of datapoints, each datapoint is a string-to-double dict representing a sparse vector.
	K: number of desired clusters. Assume that 0 < K <= |datapoints|.
	maxIters: maximum number of iterations to run for (you should terminate early if the algorithm converges).
	Return: (length K list of cluster centroids,
	        list of assignments, (i.e. if datapoints[i] belongs to centers[j], then assignments[i] = j)
	        final reconstruction loss)
	Use dataMatrix = testDatapoints() instead to test.
	'''
	if dataType == c.KMEANS_RECIPE_DATATYPE:
		dataMatrix, countToData, allPoints = createRecipeDatapoints(jsonDataFilePath, featureList)
	elif dataType == c.KMEANS_ALIAS_DATATYPE:
		dataMatrix, countToData, allPoints = createAliasDatapoints(jsonDataFilePath, featureList)
	
	est = KMeans(n_clusters = K)
	pred = est.fit_predict(dataMatrix)
	clusterToRecipes, clusterStats = clusterAssignment(est, countToData, allPoints, featureList)
	
	printClusters(clusterToRecipes, clusterStats, est, dataType, featureList)
	# drawClusters(dataMatrix, pred)
	
##
# Function: run
# -------------
# kmeans.py's version of main(). This function is called by write_recipes.py
# with arguments given to it.
##
def run(verbose=False, K='5', dataFilename='testRecipeTh', dataType=c.KMEANS_RECIPE_DATATYPE, features=c.KMEANS_FEATURE_PIQUANT):
	global COMMAND_LINE

	COMMAND_LINE = "python __main__.py write_recipes module=kmeans " + "verbose=" + str(verbose) + " " + K + " " + dataFilename + " " + dataType + " " + features
	fullFilename = dataFilename + '.json'

	featureList = features.split(',')

	print '***** Starting Kmeans on ' + fullFilename + '! *****'
	print

	if dataType != c.KMEANS_RECIPE_DATATYPE and dataType != c.KMEANS_ALIAS_DATATYPE:
		exceptionMessage = "We don't have kmeans implemented for datatype " + dataType + ". Try 'recipe' or 'alias' instead."
		raise Exception(exceptionMessage)
	for feature in featureList:
		if feature not in c.KMEANS_ALL_FEATURES:
			exceptionMessage = "We don't have kmeans implemented for feature " + feature + ". Try 'piquant', or 'meaty' instead."
			raise Exception(exceptionMessage)

	numClusters = int(K)
	jsonDataFilePath = os.path.join(c.PATH_TO_ROOT, "res", fullFilename)
	cluster(jsonDataFilePath, numClusters, dataType, featureList)

	print
	# print COMMAND_LINE
	return '***** Kmeans completed on ' + fullFilename + '! *****'


