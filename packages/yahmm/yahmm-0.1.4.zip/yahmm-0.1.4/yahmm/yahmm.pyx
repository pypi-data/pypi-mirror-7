#!/usr/bin/env python2.7
# yahmm.py: Yet Another Hidden Markov Model library
# Contact: Jacob Schreiber ( jmschreiber91@gmail.com )
#          Adam Novak ( anovak1@ucsc.edu )

"""
For detailed documentation and examples, see the README.
"""

cimport cython
from cython.view cimport array as cvarray
from libc.math cimport log as clog, sqrt as csqrt, exp as cexp
import math, random, collections, itertools as it, sys, bisect, time
import networkx
import scipy.stats, scipy.sparse, scipy.special, scipy.misc

import numpy
cimport numpy
from matplotlib import pyplot

# Define some useful constants
DEF NEGINF = float("-inf")
DEF INF = float("inf")
DEF SQRT_2_PI = 2.50662827463

# Define a mapping of strings to distibution options
REGISTRY = { 'NormalDistribution' : NormalDistribution,
			 'UniformDistribution' : UniformDistribution,
			 'ExponentialDistribution': ExponentialDistribution,
			 'GammaDistribution' : GammaDistribution,
			 'InverseGammaDistribution' : InverseGammaDistribution,
			 'DiscreteDistribution' : DiscreteDistribution,
			 'LambdaDistribution' : LambdaDistribution,
			 'GaussianKernelDensity' : GaussianKernelDensity,
			 'UniformKernelDensity' : UniformKernelDensity,
			 'TriangleKernelDensity' : TriangleKernelDensity,
			 'MixtureDistribution' : MixtureDistribution }

# Useful speed optimized functions
cdef inline double _log ( double x ):
	return clog( x ) if x > 0 else NEGINF

cdef inline double pair_lse( double x, double y ):
	if x == INF or y == INF:
		return INF
	if x == NEGINF:
		return y
	if y == NEGINF:
		return x
	if x > y:
		return x + clog( cexp( y-x ) + 1 )
	return y + clog( cexp( x-y ) + 1 )

# Useful python-based array-intended operations
def log(value):
	"""
	Return the natural log of the given value, or - infinity if the value is 0.
	Can handle both scalar floats and numpy arrays.
	"""

	if isinstance( value, numpy.ndarray ):
		to_return = numpy.zeros(( value.shape ))
		to_return[ value > 0 ] = numpy.log( value[ value > 0 ] )
		to_return[ value == 0 ] = NEGINF
		return to_return
	return _log( value )
		
def exp(value):
	"""
	Return e^value, or 0 if the value is - infinity.
	"""
	
	return numpy.exp(value)

cdef class Distribution(object):
	"""
	Represents a probability distribution over whatever the HMM you're making is
	supposed to emit. Ought to be subclassed and have log_probability(), 
	sample(), and from_sample() overridden. Distribution.name should be 
	overridden and replaced with a unique name for the distribution type. The 
	distribution should be registered by calling register() on the derived 
	class, so that Distribution.read() can read it. Any distribution parameters 
	need to be floats stored in self.parameters, so they will be properly 
	written by write().
	"""
	
	# Instance stuff
	
	"""
	This is the name that should be used for serializing this distribution. May
	not contain newlines or spaces.
	"""

	cdef public str name
	cdef public list parameters
	cdef public numpy.ndarray points
	cdef public double [:] weights

	def __init__(self):
		"""
		Make a new Distribution with the given parameters. All parameters must 
		be floats.
		
		Storing parameters in self.parameters instead of e.g. self.mean on the 
		one hand makes distribution code ugly, because we don't get to call them
		self.mean. On the other hand, it means we don't have to override the 
		serialization code for every derived class.
		"""

		self.name = "Distribution"
		self.parameters = []
		self.distributions = {}
		
	def copy( self ):
		"""
		Return a copy of this distribution, untied. 
		"""

		return self.__class__( *self.parameters ) 

	def log_probability(self, symbol):
		"""
		Return the log probability of the given symbol under this distribution.
		"""
		
		raise NotImplementedError

	def sample(self):
		"""
		Return a random item sampled from this distribution.
		"""
		
		raise NotImplementedError
		
	def from_sample(self, items, weights=None):
		"""
		Set the parameters of this Distribution to maximize the likelihood of 
		the given sample. Items holds some sort of sequence. If weights is 
		specified, it holds a sequence of value to weight each item by.
		"""
		
		raise NotImplementedError
		
	def __str__(self):
		"""
		Represent this distribution in a human-readable form.
		"""
		
		return "{}({})".format(self.name, ", ".join(map(str, self.parameters)))
		
	def write(self, stream):
		"""
		Write a line to the stream that can be used to reconstruct this 
		distribution.
		"""
		
		# Format is name of distribution in distribution lookup table, and then
		# all the parameters
		stream.write("{} {}\n".format(self.name, 
			" ".join(map(repr, self.parameters))))
			
	@staticmethod
	def read(stream):
		"""
		Read a Distribution from the given stream. Instantiate it as the 
		appropriate Distribution subclass. Implemented as a staticmethod instead
		of a classmethod since it figures out the appropriate distribution type
		on its own.
		"""
		
		# Get a line from the stream
		line = stream.readline()
		if line == "":
			# EoF
			raise EOFError("EoF encountered wile reading distribution.")
			
		# Break it into parts. The first part is the name of the distribution 
		# and the other parts are parameters.    
		parts = line.strip().split()
		if not REGISTRY.has_key(parts[0]):
			raise Exception("Unknown distribution: {}".format(parts[0]))
		
		# Get the class to use
		distribution_class = REGISTRY[parts[0]]
		
		# Make a list of float parameters
		parameters = [float(s) for s in parts[1:]]
		
		# Instantiate and return the distribution, by passing all the parameters
		# in order to the appropriate constructor.
		return distribution_class(*parameters)

cdef class UniformDistribution(Distribution):
	"""
	A uniform distribution between two values.
	"""
	
	"""
	This is the name that should be used for serializing this distribution.
	"""

	def __init__(self, start, end):
		"""
		Make a new Uniform distribution over floats between start and end, 
		inclusive. Start and end must not be equal.
		"""
		
		# Store the parameters
		self.parameters = [start, end]
		self.name = "UniformDistribution"
		
	def log_probability(self, symbol):
		"""
		What's the probability of the given float under this distribution?
		"""
		
		return self._log_probability( self.parameters[0], self.parameters[1], symbol )

	cdef double _log_probability( self, double a, double b, double symbol ):
		if symbol == a and symbol == b:
			return 0
		if symbol >= a and symbol <= b:
			return _log( 1.0 / ( b - a ) )
		return NEGINF
			
	def sample(self):
		"""
		Sample from this uniform distribution and return the value sampled.
		"""
		
		return random.uniform(self.parameters[0], self.parameters[1])
		
	def from_sample(self, items, weights=None):
		"""
		Set the parameters of this Distribution to maximize the likelihood of 
		the given sample. Items holds some sort of sequence. If weights is 
		specified, it holds a sequence of value to weight each item by.
		"""
		
		if weights is not None:
			# Throw out items with weight 0
			items = [item for (item, weight) in it.izip(items, weights) 
				if weight > 0]
		
		if len(items) == 0:
			# No sample, so just ignore it and keep our old parameters.
			return
		
		# The ML uniform distribution is just min to max.
		# Weights don't matter for this
		self.parameters[0] = numpy.min(items)
		self.parameters[1] = numpy.max(items)

cdef class NormalDistribution(Distribution):
	"""
	A normal distribution based on a mean and standard deviation.
	"""
	
	"""
	This is the name that should be used for serializing this distribution.
	"""

	def __init__(self, mean, std):
		"""
		Make a new Normal distribution with the given mean mean and standard 
		deviation std.
		"""
		
		# Store the parameters
		self.parameters = [mean, std]
		self.name = "NormalDistribution"

	def log_probability(self, symbol, epsilon=1E-4):
		"""
		What's the probability of the given float under this distribution?
		
		For distributions with 0 std, epsilon is the distance within which to 
		consider things equal to the mean.
		"""

		return self._log_probability( symbol, epsilon )

	cdef double _log_probability( self, double symbol, double epsilon ):
		"""
		Do the actual math here.
		"""

		cdef double mu = self.parameters[0], theta = self.parameters[1]
		if theta == 0.0:
			if abs( symbol - mu ) < epsilon:
				return 0
			else:
				return NEGINF
  
		return _log( 1.0 / ( theta * SQRT_2_PI ) ) - ((symbol - mu) ** 2) /\
			(2 * theta ** 2)
			
	def sample(self):
		"""
		Sample from this normal distribution and return the value sampled.
		"""
		
		# This uses the same parameterization
		return random.normalvariate(*self.parameters)
		
	def from_sample(self, items, weights=None, min_std=0.01):
		"""
		Set the parameters of this Distribution to maximize the likelihood of 
		the given sample. Items holds some sort of sequence. If weights is 
		specified, it holds a sequence of value to weight each item by.
		
		min_std specifieds a lower limit on the learned standard deviation.
		"""
		
		if len(items) == 0:
			# No sample, so just ignore it and keep our old parameters.
			return
		
		# Make it be a numpy array
		items = numpy.asarray(items)
		
		if weights is None:
			# Weight everything 1 if no weights specified
			weights = numpy.ones_like(items)
		else:
			# Force whatever we have to be a Numpy array
			weights = numpy.asarray(weights)
		
		if weights.sum() == 0:
			# Since negative weights are banned, we must have no data.
			# Don't change the parameters at all.
			return
		
		# The ML uniform distribution is just sample mean and sample std.
		# But we have to weight them. average does weighted mean for us, but 
		# weighted std requires a trick from Stack Overflow and Prof. Karplus.
		# http://stackoverflow.com/a/2415343/402891
		# Take the mean
		mean = numpy.average(items, weights=weights)
		
		if len(weights[weights != 0]) > 1:
			# We want to do the std too, but only if more than one thing has a 
			# nonzero weight
			# First find the variance
			variance = (numpy.dot(items ** 2 - mean ** 2, weights) / 
				weights.sum())
				
			if variance >= 0:
				std = math.sqrt(variance)
			else:
				# May have a small negative variance on accident. Ignore and set
				# to 0.
				std = 0
		else:
			# Only one data point, can't update std
			std = self.parameters[1]    
		
		# Enforce min std
		std = max( numpy.array([std, min_std]) )
			
		# Set the parameters
		self.parameters = [mean, std]

cdef class ExponentialDistribution(Distribution):
	"""
	Represents an exponential distribution on non-negative floats.
	"""
	
	def __init__(self, rate):
		"""
		Make a new inverse gamma distribution. The parameter is called "rate" 
		because lambda is taken.
		"""

		self.parameters = [rate]
		self.name = "ExponentialDistribution"
		
	def log_probability(self, symbol):
		"""
		What's the probability of the given float under this distribution?
		"""
		
		return log(self.parameters[0]) - self.parameters[0] * symbol
		
	def sample(self):
		"""
		Sample from this exponential distribution and return the value
		sampled.
		"""
		
		return random.expovariate(*self.parameters)
		
	def from_sample(self, items, weights=None):
		"""
		Set the parameters of this Distribution to maximize the likelihood of 
		the given sample. Items holds some sort of sequence. If weights is 
		specified, it holds a sequence of value to weight each item by.
		"""
		
		if len(items) == 0:
			# No sample, so just ignore it and keep our old parameters.
			return
		
		# Make it be a numpy array
		items = numpy.asarray(items)
		
		if weights is None:
			# Weight everything 1 if no weights specified
			weights = numpy.ones_like(items)
		else:
			# Force whatever we have to be a Numpy array
			weights = numpy.asarray(weights)
		
		if weights.sum() == 0:
			# Since negative weights are banned, we must have no data.
			# Don't change the parameters at all.
			return
		
		# Parameter MLE = 1/sample mean, easy to weight
		# Compute the weighted mean
		weighted_mean = numpy.average(items, weights=weights)
		
		# Update parameters
		self.parameters[0] = 1.0 / weighted_mean

cdef class GammaDistribution(Distribution):
	"""
	This distribution represents a gamma distribution, parameterized in the 
	alpha/beta (shape/rate) parameterization. ML estimation for a gamma 
	distribution, taking into account weights on the data, is nontrivial, and I 
	was unable to find a good theoretical source for how to do it, so I have 
	cobbled together a solution here from less-reputable sources.
	"""
	
	def __init__(self, alpha, beta):
		"""
		Make a new gamma distribution. Alpha is the shape parameter and beta is 
		the rate parameter.
		"""
		
		self.parameters = [alpha, beta]
		self.name = "GammaDistribution"
		
	def log_probability(self, symbol):
		"""
		What's the probability of the given float under this distribution?
		"""
		
		# Gamma pdf from Wikipedia (and stats class)
		return (log(self.parameters[1]) * self.parameters[0] - 
			math.lgamma(self.parameters[0]) + 
			log(symbol) * (self.parameters[0] - 1) - 
			self.parameters[1] * symbol)
		
	def sample(self):
		"""
		Sample from this gamma distribution and return the value sampled.
		"""
		
		# We have a handy sample from gamma function. Unfortunately, while we 
		# use the alpha, beta parameterization, and this function uses the 
		# alpha, beta parameterization, our alpha/beta are shape/rate, while its
		# alpha/beta are shape/scale. So we have to mess with the parameters.
		return random.gammavariate(self.parameters[0], 1.0 / self.parameters[1])
		
	def from_sample(self, items, weights=None, epsilon=1E-9, 
		iteration_limit = 1000):
		"""
		Set the parameters of this Distribution to maximize the likelihood of 
		the given sample. Items holds some sort of sequence. If weights is 
		specified, it holds a sequence of value to weight each item by.
		
		In the Gamma case, likelihood maximization is necesarily numerical, and 
		the extension to weighted values is not trivially obvious. The algorithm
		used here includes a Newton-Raphson step for shape parameter estimation,
		and analytical calculation of the rate parameter. The extension to 
		weights is constructed using vital information found way down at the 
		bottom of an Experts Exchange page.
		
		Newton-Raphson continues until the change in the parameter is less than 
		epsilon, or until iteration_limit is reached
		
		See:
		http://en.wikipedia.org/wiki/Gamma_distribution
		http://www.experts-exchange.com/Other/Math_Science/Q_23943764.html
		"""
		
		if len(items) == 0:
			# No sample, so just ignore it and keep our old parameters.
			return
		
		# Make it be a numpy array
		items = numpy.asarray(items)
		
		if weights is None:
			# Weight everything 1 if no weights specified
			weights = numpy.ones_like(items)
		else:
			# Force whatever we have to be a Numpy array
			weights = numpy.asarray(weights)
		
		if weights.sum() == 0:
			# Since negative weights are banned, we must have no data.
			# Don't change the parameters at all.
			return
		
		# First, do Newton-Raphson for shape parameter.
		
		# Calculate the sufficient statistic s, which is the log of the average 
		# minus the average log. When computing the average log, we weight 
		# outside the log function. (In retrospect, this is actually pretty 
		# obvious.)
		statistic = (log(numpy.average(items, weights=weights)) - 
			numpy.average(log(items), weights=weights))
			
		# Start our Newton-Raphson at what Wikipedia claims a 1969 paper claims 
		# is a good approximation.
		# Really, start with new_shape set, and shape set to be far away from it
		shape = float("inf")
		
		if statistic != 0:
			# Not going to have a divide by 0 problem here, so use the good
			# estimate
			new_shape =  (3 - statistic + math.sqrt((statistic - 3) ** 2 + 24 * 
				statistic)) / (12 * statistic)
		if statistic == 0 or new_shape <= 0:
			# Try the current shape parameter
			new_shape = self.parameters[0]
		
		# Count the iterations we take
		iteration = 0
			
		# Now do the update loop.
		# We need the digamma (gamma derivative over gamma) and trigamma 
		# (digamma derivative) functions. Luckily, scipy.special.polygamma(0, x)
		# is the digamma function (0th derivative of the digamma), and 
		# scipy.special.polygamma(1, x) is the trigamma function.
		while abs(shape - new_shape) > epsilon and iteration < iteration_limit:
			shape = new_shape
			
			new_shape = shape - (log(shape) - 
				scipy.special.polygamma(0, shape) -
				statistic) / (1.0 / shape - scipy.special.polygamma(1, shape))
			
			# Don't let shape escape from valid values
			if abs(new_shape) == float("inf") or new_shape == 0:
				# Hack the shape parameter so we don't stop the loop if we land
				# near it.
				shape = new_shape
				
				# Re-start at some random place.
				new_shape = random.random()
				
			iteration += 1
			
		# Might as well grab the new value
		shape = new_shape
				
		# Now our iterative estimation of the shape parameter has converged.
		# Calculate the rate parameter
		rate = 1.0 / (1.0 / (shape * weights.sum()) * items.dot(weights).sum())

		# Set the estimated parameters
		self.parameters = [shape, rate]    

cdef class InverseGammaDistribution(GammaDistribution):
	"""
	This distribution represents an inverse gamma distribution (1/the RV ~ gamma
	with the same parameters). A distribution over non-negative floats.
	
	We cheat and don't have to do much work by inheriting from the 
	GammaDistribution.
	
	Tests:
	
	>>> random.seed(0)
	
	>>> distribution = InverseGammaDistribution(10, 0.5)
	>>> weights = numpy.array([random.random() for i in xrange(10000)])
	>>> distribution.write(sys.stdout)
	InverseGammaDistribution 10 0.5
	
	>>> sample = numpy.array([distribution.sample() for i in xrange(10000)])
	>>> distribution.from_sample(sample)
	>>> distribution.write(sys.stdout)
	InverseGammaDistribution 9.9756999562413196 0.4958491351206667
	
	"""
	
	def __init__(self, alpha, beta):
		"""
		Make a new inverse gamma distribution. Alpha is the shape parameter and 
		beta is the scale parameter.
		"""
		
		self.parameters = [alpha, beta]
		self.name = "InverseGammaDistribution"
		
	def log_probability(self, symbol):
		"""
		What's the probability of the given float under this distribution?
		"""
		
		return super(InverseGammaDistribution, self).log_probability(
			1.0 / symbol)
			
	def sample(self):
		"""
		Sample from this inverse gamma distribution and return the value
		sampled.
		"""
		
		# Invert the sample from the gamma distribution.
		return 1.0 / super(InverseGammaDistribution, self).sample()
		
	def from_sample(self, items, weights=None):
		"""
		Set the parameters of this Distribution to maximize the likelihood of 
		the given sample. Items holds some sort of sequence. If weights is 
		specified, it holds a sequence of value to weight each item by.
		"""
		
		# Fit the gamma distribution on the inverted items.
		super(InverseGammaDistribution, self).from_sample(1.0 / 
			numpy.asarray(items), weights=weights)

cdef class DiscreteDistribution(Distribution):
	"""
	A discrete distribution, made up of characters and their probabilities,
	assuming that these probabilities will sum to 1.0. 
	"""
	
	def __init__(self, characters ):
		"""
		Make a new discrete distribution with a dictionary of discrete
		characters and their probabilities, checking to see that these
		sum to 1.0. Each discrete character can be modelled as a
		Bernoulli distribution.
		"""
		
		# Store the parameters
		self.parameters = [ characters ]
		self.name = "DiscreteDistribution"


	def log_probability(self, symbol, pseudocounts=None ):
		"""
		What's the probability of the given symbol under this distribution?
		Simply the log probability value given at initiation. If the symbol
		is not part of the discrete distribution, return 0 or a pseudocount
		of .001. 
		"""

		if symbol in self.parameters[0]:
			return log( self.parameters[0][symbol] )
		else:
			if pseudocounts:
				return pseudocounts
			return NEGINF    
			
	def sample(self):
		"""
		Sample randomly from the discrete distribution, returning the character
		which was randomly generated.
		"""
		
		rand = random.random()
		for key, value in self.parameters[0].items():
			if value >= rand:
				return key
			rand -= value
	
	def from_sample( self, items, weights=None ):
		"""
		Takes in an iterable representing samples from a distribution and
		turn it into a discrete distribution. If no weights are provided,
		each sample is weighted equally. If weights are provided, they are
		normalized to sum to 1 and used.
		"""

		n = len(items)
		if weights:
			weights = numpy.array(weights) / numpy.sum(weights)
		else:
			weights = numpy.ones(n) / n

		characters = {}
		for character, weight in it.izip( items, weights ):
			try:
				characters[character] += 1. * weight
			except KeyError:
				characters[character] = 1. * weight

		self.parameters = [ characters ]

cdef class LambdaDistribution(Distribution):
	"""
	A distribution which takes in an arbitrary lambda function, and returns
	probabilities associated with whatever that function gives. For example...

	func = lambda x: log(1) if 2 > x > 1 else log(0)
	distribution = LambdaDistribution( func )
	print distribution.log_probability( 1 ) # 1
	print distribution.log_probability( -100 ) # 0

	This assumes the lambda function returns the log probability, not the
	untransformed probability.
	"""
	
	def __init__(self, lambda_funct ):
		"""
		Takes in a lambda function and stores it. This function should return
		the log probability of seeing a certain input.
		"""

		# Store the parameters
		self.parameters = [lambda_funct]
		self.name = "LambdaDistribution"
		
	def log_probability(self, symbol):
		"""
		What's the probability of the given float under this distribution?
		"""

		return self.parameters[0](symbol)

cdef class GaussianKernelDensity( Distribution ):
	"""
	A quick way of storing points to represent a Gaussian kernel density in one
	dimension. Takes in the points at initialization, and calculates the log of
	the sum of the Gaussian distance of the new point from every other point.
	"""

	def __init__( self, points, bandwidth=1, weights=None ):
		"""
		Take in points, bandwidth, and appropriate weights. If no weights
		are provided, a uniform weight of 1/n is provided to each point.
		Weights are scaled so that they sum to 1. 
		"""

		n = len(points)
		if weights:
			self.weights = numpy.array(weights) / numpy.sum(weights)
		else:
			self.weights = numpy.ones( n ) / n 

		self.points = numpy.array( points )
		self.parameters = [ self.points, bandwidth, self.weights ]
		self.name = "GaussianKernelDensity"

	def log_probability( self, symbol ):
		"""
		What's the probability of a given float under this distribution? It's
		the sum of the distances of the symbol from every point stored in the
		density. Bandwidth is defined at the beginning. A wrapper for the
		cython function which does math.
		"""

		return self._log_probability( symbol )

	cdef double _log_probability( self, double symbol ):
		"""
		Actually calculate it here.
		"""
		cdef double bandwidth = self.parameters[1]
		cdef double mu, scalar = 1.0 / SQRT_2_PI
		cdef int i = 0, n = len(self.parameters[0])
		cdef double distribution_prob = 0, point_prob

		for i in xrange( n ):
			# Go through each point sequentially
			mu = self.parameters[0][i]

			# Calculate the probability under that point
			point_prob = scalar * \
				cexp( -0.5 * (( mu-symbol ) / bandwidth) ** 2 )

			# Scale that point according to the weight 
			distribution_prob += point_prob * self.parameters[2][i]

		# Return the log of the sum of the probabilities
		return _log( distribution_prob )

	def sample( self ):
		"""
		Generate a random sample from this distribution. This is done by first
		selecting a random point, weighted by weights if the points are weighted
		or uniformly if not, and then randomly sampling from that point's PDF.
		"""

		mu = numpy.random.choice( self.parameters[0], p=self.parameters[2] )
		return random.gauss( mu, self.parameters[1] )

	def from_sample( self, points, weights=None ):
		"""
		Replace the points, training without inertia.
		"""

		self.points = points

		n = len(points)
		if weights:
			self.weights = numpy.array(weights) / numpy.sum(weights)
		else:
			self.weights = numpy.ones( n ) / n 

cdef class UniformKernelDensity( Distribution ):
	"""
	A quick way of storing points to represent an Exponential kernel density in
	one dimension. Takes in points at initialization, and calculates the log of
	the sum of the Gaussian distances of the new point from every other point.
	"""

	def __init__( self, points, bandwidth=1, weights=None ):
		"""
		Take in points, bandwidth, and appropriate weights. If no weights
		are provided, a uniform weight of 1/n is provided to each point.
		Weights are scaled so that they sum to 1. 
		"""

		n = len(points)
		if weights:
			self.weights = numpy.array(weights) / numpy.sum(weights)
		else:
			self.weights = numpy.ones( n ) / n 

		self.points = numpy.array( points )
		self.parameters = [ self.points, bandwidth, self.weights ]
		self.name = "UniformKernelDensity"

	def log_probability( self, symbol ):
		"""
		What's the probability ofa given float under this distribution? It's
		the sum of the distances from the symbol calculated under individual
		exponential distributions. A wrapper for the cython function.
		"""

		return self._log_probability( symbol )

	cdef _log_probability( self, double symbol ):
		"""
		Actually do math here.
		"""

		cdef double mu
		cdef double distribution_prob=0, point_prob
		cdef int i = 0, n = len(self.parameters[0])

		for i in xrange( n ):
			# Go through each point sequentially
			mu = self.parameters[0][i]

			# The good thing about uniform distributions if that
			# you just need to check to make sure the point is within
			# a bandwidth.
			if abs( mu - symbol ) <= self.parameters[1]:
				point_prob = 1

			# Properly weight the point before adding it to the sum
			distribution_prob += point_prob * self.parameters[2][i]

		# Return the log of the sum of probabilities
		return _log( distribution_prob )
	
	def sample( self ):
		"""
		Generate a random sample from this distribution. This is done by first
		selecting a random point, weighted by weights if the points are weighted
		or uniformly if not, and then randomly sampling from that point's PDF.
		"""

		mu = numpy.random.choice( self.points, p=self.weights )
		bandwidth = self.parameters[1]
		return random.uniform( mu-bandwidth, mu+bandwidth )

	def from_sample( self, points, weights=None ):
		"""
		Replace the points, training without inertia.
		"""

		self.points = points

		n = len(points)
		if weights:
			self.weights = numpy.array(weights) / numpy.sum(weights)
		else:
			self.weights = numpy.ones( n ) / n 

cdef class TriangleKernelDensity( Distribution ):
	"""
	A quick way of storing points to represent an Exponential kernel density in
	one dimension. Takes in points at initialization, and calculates the log of
	the sum of the Gaussian distances of the new point from every other point.
	"""

	def __init__( self, points, bandwidth=1, weights=None ):
		"""
		Take in points, bandwidth, and appropriate weights. If no weights
		are provided, a uniform weight of 1/n is provided to each point.
		Weights are scaled so that they sum to 1. 
		"""

		n = len(points)
		if weights:
			self.weights = numpy.array(weights) / numpy.sum(weights)
		else:
			self.weights = numpy.ones( n ) / n 

		self.points = numpy.array( points )
		self.parameters = [ self.points, bandwidth, self.weights ]
		self.name = "TriangleKernelDensity"

	def log_probability( self, symbol ):
		"""
		What's the probability of a given float under this distribution? It's
		the sum of the distances from the symbol calculated under individual
		exponential distributions. A wrapper for the cython function.
		""" 

		return self._log_probability( symbol )

	cdef double _log_probability( self, double symbol ):
		"""
		Actually do math here.
		"""

		cdef double bandwidth = self.parameters[1]
		cdef double mu
		cdef double distribution_prob=0, point_prob
		cdef int i = 0, n = len(self.parameters[0])

		for i in xrange( n ):
			# Go through each point sequentially
			mu = self.parameters[0][i]

			# Calculate the probability for each point
			point_prob = bandwidth - abs( mu - symbol ) 
			if point_prob < 0:
				point_prob = 0 

			# Properly weight the point before adding to the sum
			distribution_prob += point_prob * self.parameters[2][i]

		# Return the log of the sum of probabilities
		return _log( distribution_prob )

	def sample( self ):
		"""
		Generate a random sample from this distribution. This is done by first
		selecting a random point, weighted by weights if the points are weighted
		or uniformly if not, and then randomly sampling from that point's PDF.
		"""

		mu = numpy.random.choice( self.points, p=self.weights )
		bandwidth = self.parameters[1]
		return random.triangular( mu-bandwidth, mu+bandwidth, mu )

	def from_sample( self, points, weights=None ):
		"""
		Replace the points, training without inertia.
		"""

		self.points = points

		n = len(points)
		if weights:
			self.weights = numpy.array(weights) / numpy.sum(weights)
		else:
			self.weights = numpy.ones( n ) / n 

cdef class MixtureDistribution( Distribution ):
	"""
	Allows you to create an arbitrary mixture of distributions. There can be
	any number of distributions, include any permutation of types of
	distributions. Can also specify weights for the distributions.
	"""

	def __init__( self, distributions, weights=None ):
		"""
		Take in the distributions and appropriate weights. If no weights
		are provided, a uniform weight of 1/n is provided to each point.
		Weights are scaled so that they sum to 1. 
		"""
		n = len(distributions)
		if weights:
			self.weights = numpy.array( weights ) / numpy.sum( weights )
		else:
			self.weights = numpy.ones(n) / n

		self.parameters = [ distributions, self.weights ]
		self.name = "MixtureDistribution"

	def log_probability( self, symbol ):
		"""
		What's the probability of a given float under this mixture? It's
		the log-sum-exp of the distances from the symbol calculated under all
		distributions. Currently in python, not cython, to allow for dovetyping
		of both numeric and not-necessarily-numeric distributions. 
		"""

		(d, w), n = self.parameters, len(self.parameters) 
		return _log(numpy.sum(cexp( d[i](symbol) ) * w[i] for i in xrange(n)))

	def sample( self ):
		"""
		Sample from the mixture. First, choose a distribution to sample from
		according to the weights, then sample from that distribution. 
		"""

		i = random.random()
		for d, w in zip( self.parameters ):
			if w > i:
				return d.sample()
			i -= w 

	def from_sample( self, items, weights=None ):
		"""
		Currently not implemented, but should be some form of GMM estimation
		on the data. The issue would be that the MixtureModel can be more
		expressive than a GMM estimation, since GMM estimation is one type
		of distribution.
		"""

		raise NotImplementedError

cdef class State(object):
	"""
	Represents a state in an HMM. Holds emission distribution, but not
	transition distribution, because that's stored in the graph edges.
	"""
	
	cdef public Distribution distribution
	cdef public str name

	def __init__(self, distribution, name=None ):
		"""
		Make a new State emitting from the given distribution. If distribution 
		is None, this state does not emit anything. A name, if specified, will 
		be the state's name when presented in output. Name may not contain 
		spaces or newlines, and must be unique within an HMM.
		"""
		
		# Save the distribution
		self.distribution = distribution
		
		if name is not None:
			# Name specified by the user. Use that instead.
			self.name = name
		else:
			# No name specified, use the memory address
			self.name = str(id(self))

	def is_silent(self):
		"""
		Return True if this state is silent (distribution is None) and False 
		otherwise.
		"""
		
		return self.distribution is None

	def tied_copy( self ):
		"""
		Return a copy of this state where the distribution is tied to the
		distribution of this state.
		"""

		return State( distribution=self.distribution, name=self.name )
		
	def copy( self ):
		"""
		Return a hard copy of this state.
		"""

		return State( **self.__dict__ )
			
	def __str__(self):
		"""
		Represent this state with it's name.
		"""
		
		if self.is_silent():
			return "{} (silent)".format(self.name)
		else:
			return "{}: {}".format(self.name, str(self.distribution))
		
	def __repr__(self):
		"""
		Represent this state uniquely.
		"""
		
		return "State({}, {})".format(self.name, str(self.distribution))
		
	def write(self, stream):
		"""
		Write this State (and its Distribution) to the given stream.
		
		Format: name, followed by "*" if the state is silent.
		If not followed by "*", the next line contains the emission
		distribution.
		"""
		
		
		if self.is_silent():
			stream.write("{} *\n".format(self.name))
		else:
			stream.write("{}\n".format(self.name))
			self.distribution.write(stream)
			
	@classmethod
	def read(cls, stream):
		"""
		Read a State from the given stream, in the format output by write().
		"""
		
		# Read a line
		line = stream.readline()
		
		if line == "":
			raise EOFError("End of file while reading state.")
			
		# Spilt the line up
		parts = line.strip().split()
		
		# parts[0] holds the state's name, and parts[1], if it exists, holds "*"
		# if the state is silent.
		
		if len(parts) > 1 and parts[1] == "*":
			# This is a silent state
			return cls(None, name=parts[0])
		else:
			# This state has a distribution on the next line.
			# Read in the distribution
			distribution = Distribution.read(stream)
			
			# Make and return the state
			return cls(distribution, name=parts[0])

cdef class Model(object):
	"""
	Represents a Hidden Markov Model.
	
	Tests:
	Re-seed the RNG
	>>> random.seed(0)

	>>> s1 = State(UniformDistribution(0.0, 1.0), name="S1")
	>>> s2 = State(UniformDistribution(0.5, 1.5), name="S2")
	>>> s3 = State(UniformDistribution(-1.0, 1.0), name="S3")
	
	Make a simple 2-state model
	>>> model_a = Model(name="A")
	>>> model_a.add_state(s1)
	>>> model_a.add_state(s2)
	>>> model_a.add_transition(s1, s1, 0.70)
	>>> model_a.add_transition(s1, s2, 0.25)
	>>> model_a.add_transition(s1, model_a.end, 0.05)
	>>> model_a.add_transition(s2, s2, 0.70)
	>>> model_a.add_transition(s2, s1, 0.25)
	>>> model_a.add_transition(s2, model_a.end, 0.05)
	>>> model_a.add_transition(model_a.start, s1, 0.5)
	>>> model_a.add_transition(model_a.start, s2, 0.5)
	
	Make another model with that model as a component
	>>> model_b = Model(name="B")
	>>> model_b.add_state(s3)
	>>> model_b.add_transition(model_b.start, s3, 1.0)
	>>> model_b.add_model(model_a)
	>>> model_b.add_transition(s3, model_a.start, 1.0)
	>>> model_b.add_transition(model_a.end, model_b.end, 1.0) 
	
	>>> model_b.bake()
	
	>>> model_b.write(sys.stdout)
	B 7
	A-end *
	A-start *
	B-end *
	B-start *
	S1
	UniformDistribution 0.0 1.0
	S2
	UniformDistribution 0.5 1.5
	S3
	UniformDistribution -1.0 1.0
	A-end B-end 1.0
	A-start S1 0.5
	A-start S2 0.5
	B-start S3 1.0
	S1 A-end 0.05
	S1 S1 0.7
	S1 S2 0.25
	S2 A-end 0.05
	S2 S1 0.25
	S2 S2 0.7
	S3 A-start 1.0

	
	>>> model_b.sample()
	[0.515908805880605, 1.0112747213686086, 1.2837985890347725, \
0.9765969541523558, 1.4081128851953353, 0.7818378443997038, \
0.6183689966753316, 0.9097462559682401]


	
	>>> model_b.forward([])
	-inf
	>>> model_b.forward([-0.5, 0.2, 0.2])
	-4.7387015786126137
	>>> model_b.forward([-0.5, 0.2, 0.2 -0.5])
	-inf
	>>> model_b.forward([-0.5, 0.2, 1.2, 0.8])
	-5.8196142901813221

	
	>>> model_b.backward([])
	-inf
	>>> model_b.backward([-0.5, 0.2, 0.2])
	-4.7387015786126137
	>>> model_b.backward([-0.5, 0.2, 0.2 -0.5])
	-inf
	>>> model_b.backward([-0.5, 0.2, 1.2, 0.8])
	-5.819614290181323

	
	>>> model_b.viterbi([])
	(-inf, None)
	>>> model_b.viterbi([-0.5, 0.2, 0.2])
	(-4.7387015786126137, \
[(0, State(B-start, None)), \
(1, State(S3, UniformDistribution(-1.0, 1.0))), \
(1, State(A-start, None)), \
(2, State(S1, UniformDistribution(0.0, 1.0))), \
(3, State(S1, UniformDistribution(0.0, 1.0))), \
(3, State(A-end, None)), \
(3, State(B-end, None))])
	>>> model_b.viterbi([-0.5, 0.2, 0.2 -0.5])
	(-inf, None)
	>>> model_b.viterbi([-0.5, 0.2, 1.2, 0.8])
	(-6.1249959397325044, \
[(0, State(B-start, None)), \
(1, State(S3, UniformDistribution(-1.0, 1.0))), \
(1, State(A-start, None)), \
(2, State(S1, UniformDistribution(0.0, 1.0))), \
(3, State(S2, UniformDistribution(0.5, 1.5))), \
(4, State(S2, UniformDistribution(0.5, 1.5))), \
(4, State(A-end, None)), \
(4, State(B-end, None))])
	>>> model_b.train([[-0.5, 0.2, 0.2], [-0.5, 0.2, 1.2, 0.8]], \
	transition_pseudocount=1)
	Training improvement: 4.47502955715
	Training improvement: 0.0392148069767
	Training improvement: 0.0366728072271
	Training improvement: 0.0268032628936
	Training improvement: 0.0159736872496
	Training improvement: 0.00828859233119
	Training improvement: 0.00397283392515
	Training improvement: 0.00182886240049
	Training improvement: 0.000825903775144
	Training improvement: 0.000369706973896
	Training improvement: 0.000164840436767
	Training improvement: 7.33668075608e-05
	Training improvement: 3.26281298075e-05
	Training improvement: 1.45054754273e-05
	Training improvement: 6.44768506741e-06
	Training improvement: 2.86579726017e-06
	Training improvement: 1.2737191708e-06
	Training improvement: 5.66103632638e-07
	Training improvement: 2.5160284256e-07
	Training improvement: 1.11823730498e-07
	Training improvement: 4.96994811972e-08
	Training improvement: 2.20886680058e-08
	Training improvement: 9.81718994986e-09
	Training improvement: 4.36319358421e-09
	Training improvement: 1.93919769131e-09
	Training improvement: 8.61867466284e-10
	0.16271181143980118
	>>> model_b.write(sys.stdout)
	B 7
	A-end *
	A-start *
	B-end *
	B-start *
	S1
	UniformDistribution 0.2 0.8
	S2
	UniformDistribution 0.8 1.2
	S3
	UniformDistribution -0.5 -0.5
	A-end B-end 1.0
	A-start S1 1.0
	B-start S3 1.0
	S1 A-end 0.333333333453
	S1 S1 0.333333333273
	S1 S2 0.333333333273
	S2 A-end 0.499999999865
	S2 S1 2.69609280849e-10
	S2 S2 0.499999999865
	S3 A-start 1.0
	
	>>> model_b.forward([])
	-inf
	>>> model_b.forward([-0.5, 0.2, 0.2])
	-1.1755733296244983
	>>> model_b.forward([-0.5, 0.2, 0.2 -0.5])
	-inf
	>>> model_b.forward([-0.5, 0.2, 1.2, 0.8])
	-0.14149956275300468
	"""
	cdef public str name
	cdef public object start, end, graph
	cdef public list states
	cdef public int start_index, end_index, silent_start
	cdef double [:,:] f, b, v, transition_log_probabilities
	cdef int [:] in_edge_count, in_transitions, out_edge_count, out_transitions
	cdef int [:,:] tied
	cdef int finite

	def __init__(self, name=None, start=None, end=None):
		"""
		Make a new Hidden Markov Model. Name is an optional string used to name
		the model when output. Name may not contain spaces or newlines.
		
		If start and end are specified, they are used as start and end states 
		and new start and end states are not generated.
		"""
		
		if name is not None:
			# We have a name
			self.name = name
		else:
			# Make up a name
			self.name = str(id(self))
		
		# This holds a directed graph between states. Nodes in that graph are
		# State objects, so they're guaranteed never to conflict when composing
		# two distinct models
		self.graph = networkx.DiGraph()
		
		if start is not None:
			# Use the specified start state
			self.start = start
		else:
			# Make start state with no emissions
			self.start = State(None, name=self.name + "-start")
			
		if end is not None:
			# Use the specified end state
			self.end = end
		else:
			# Make end state with no emissions
			self.end = State(None, name=self.name + "-end")
		
		# Put start and end in the graph
		self.graph.add_node(self.start)
		self.graph.add_node(self.end)
		
		'''
		# Later, in self.bake(), we will fill these in.
		# List of all states in a defined order
		self.states = None
		# Numpy array of log probabilities for [from, to] transitions
		self.transition_log_probabilities = None
		# Index of start state
		self.start_index = None
		# Index of end state
		self.end_index = None
		# Index of first silent state
		self.silent_start = None
		
		# This holds the forward algorithm DP table. Each entry i, k holds the
		# log probability of emitting i symbols and ending in state k. This is
		# initialized by self.forward
		self.f = None
		
		# This holds the backward algorithm DP table. Each entry i, k holds the
		# log probability of emitting the remaining len(sequence) - i symbols
		# and ending in the end state, given that we are in state k. This is
		# initialized by self.backward.
		self.b = None
		'''
	
	def __str__(self):
		"""
		Represent this HMM with it's name and states.
		"""
		
		return "{}:\n\t{}".format(self.name, "\n\t".join(map(str, self.states)))

	def is_infinite( self ):
		"""
		Returns whether or not the HMM is infinite, or finite. This is
		determined in the bake method, based on if there are any edges to the
		end state or not. Can only be used after a model is baked.
		"""

		return self.finite == 0

	def add_state(self, state):
		"""
		Adds the given State to the model. It must not already be in the model,
		nor may it be part of any other model that will eventually be combined
		with this one.
		"""
		
		# Put it in the graph
		self.graph.add_node(state)
		
	def add_transition(self, a, b, probability):
		"""
		Add a transition from state a to state b with the given (non-log)
		probability. Both states must be in the HMM already. self.start and
		self.end are valid arguments here. Probabilities will be normalized
		such that every node has edges summing to 1. leaving that node, but
		only when the model is baked.
		"""
		
		# Add the transition
		self.graph.add_edge(a, b, weight=log(probability))
		
	def add_model(self, other):
		"""
		Given another Model, add that model's contents to us. Its start and end
		states become silent states in our model.
		"""
		
		# Unify the graphs (requiring disjoint states)
		self.graph = networkx.union(self.graph, other.graph)
		
		# Since the nodes in the graph are references to Python objects,
		# other.start and other.end and self.start and self.end still mean the
		# same State objects in the new combined graph.

	def concatenate_model( self, other ):
		"""
		Given another model, concatenate it in such a manner that you simply
		add a transition of probability 1 from self.end to other.start, and
		end at other.end. One of these silent states will be removed when
		the model is baked, due to the graph simplification routine.
		"""

		# Unify the graphs (requiring disjoint states)
		self.graph = networkx.union( self.graph, other.graph )
		
		# Connect the two graphs
		self.add_transition( self.end, other.start, 1.00 )

		# Move the end to other.end
		self.end = other.end

	def draw(self, **kwargs):
		"""
		Draw this model's graph using NetworkX and matplotlib. Blocks until the
		window displaying the graph is closed.
		
		Note that this relies on networkx's built-in graphing capabilities (and 
		not Graphviz) and thus can't draw self-loops.

		See networkx.draw_networkx() for the keywords you can pass in.
		"""
		
		networkx.draw(self.graph, **kwargs)
		pyplot.show()
		   
	def bake( self, verbose=False, merge="all" ): 
		"""
		Finalize the topology of the model, and assign a numerical index to
		every state. This method must be called before any of the probability-
		calculating methods.
		
		This fills in self.states (a list of all states in order) and 
		self.transition_log_probabilities (log probabilities for transitions), 
		as well as self.start_index and self.end_index, and self.silent_start 
		(the index of the first silent state).

		The option verbose will return a log of the changes made to the model
		due to normalization or merging. Merging has three options, "all",
		"partial", and None. None will keep the underlying graph structure
		completely in tact. "Partial" will merge silent states where one
		has a probability 1.0 transition to the other, to simplify the model
		without changing the underlying meaning. "All" will merge any silent
		state which has a probability 1.0 transition to any other state,
		silent or character-generating either. This may not be desirable as
		some silent states are useful for bookkeeping purposes.
		"""

		# Go through the model and delete any nodes which have no edges leading
		# to it, or edges leading out of it. This gets rid of any states with
		# no edges in or out, as well as recursively removing any chains which
		# are impossible for the viterbi path to touch.
		self.in_edge_count = numpy.zeros( len( self.graph.nodes() ), 
			dtype=numpy.int32 ) 
		self.out_edge_count = numpy.zeros( len( self.graph.nodes() ), 
			dtype=numpy.int32 )
		
		merge = merge.lower()
		while merge == 'all':
			merge_count = 0

			# Reindex the states based on ones which are still there
			prestates = self.graph.nodes()
			indices = { prestates[i]: i for i in xrange( len( prestates ) ) }

			# Go through all the edges, summing in and out edges
			for a, b in self.graph.edges():
				self.out_edge_count[ indices[a] ] += 1
				self.in_edge_count[ indices[b] ] += 1
				
			# Go through each state, and if either in or out edges are 0,
			# remove the edge.
			for i in xrange( len( prestates ) ):
				if prestates[i] is self.start or prestates[i] is self.end:
					continue

				if self.in_edge_count[i] == 0:
					merge_count += 1
					self.graph.remove_node( prestates[i] )

					if verbose:
						print "Orphan state {} removed due to no edges \
							leading to it".format(prestates[i].name )

				elif self.out_edge_count[i] == 0:
					merge_count += 1
					self.graph.remove_node( prestates[i] )

					if verbose:
						print "Orphan state {} removed due to no edges \
							leaving it".format(prestates[i].name )

			if merge_count == 0:
				break

		# Go through the model checking to make sure out edges sum to 1.
		# Normalize them to 1 if this is not the case.
		for state in self.graph.nodes():

			# Perform log sum exp on the edges to see if they properly sum to 1
			out_edges = round( numpy.sum( map( lambda x: numpy.e**x['weight'], 
				self.graph.edge[state].values() ) ), 8 )

			# The end state has no out edges, so will be 0
			if out_edges < 1. and state != self.end:
				# Issue a notice if verbose is activated
				if verbose:
					print "{} : {} summed to {}, normalized to 1.0"\
						.format( self.name, state.name, out_edges )

				# Reweight the edges so that the probability (not logp) sums
				# to 1.
				for edge in self.graph.edge[state].values():
					edge['weight'] = edge['weight'] - log( out_edges )

		# Automatically merge adjacent silent states attached by a single edge
		# of 1.0 probability, as that adds nothing to the model. Traverse the
		# edges looking for 1.0 probability edges between silent states.
		while merge in ['all', 'partial']:
			# Repeatedly go through the model until no merges take place.
			merge_count = 0

			for a, b, e in self.graph.edges( data=True ):
				# Since we may have removed a or b in a previous iteration,
				# a simple fix is to just check to see if it's still there
				if a not in self.graph.nodes() or b not in self.graph.nodes():
					continue

				if a == self.start or b == self.end:
					continue

				# If a silent state has a probability 1 transition out
				if e['weight'] == 0.0 and a.is_silent():

					# Make sure the transition is an appropriate merger
					if merge=='all' or ( merge=='partial' and b.is_silent() ):

						# Go through every transition to that state 
						for x, y, d in self.graph.edges( data=True ):

							# Make sure that the edge points to the current node
							if y is a:
								# Increment the edge counter
								merge_count += 1

								# Remove the edge going to that node
								self.graph.remove_edge( x, y )

								# Add a new edge going to the new node
								self.graph.add_edge( x, b, weight=d['weight'] )

								# Log the event
								if verbose:
									print "{} : {} - {} merged".format(
										self.name, a, b)

						# Remove the state now that all edges are removed
						self.graph.remove_node( a )

			if merge_count == 0:
				break

		# Detect whether or not there are loops of silent states by going
		# through every pair of edges, and ensure that there is not a cycle
		# of silent states.		
		for a, b, e in self.graph.edges( data=True ):
			for x, y, d in self.graph.edges( data=True ):
				if a is y and b is x and a.is_silent() and b.is_silent():
					print "Loop: {} - {}".format( a.name, b.name )
					#raise SyntaxError( "Cannot have loops between silent \
					#	states. Loop detected between state {} - {}".format(
					#		a.name, b.name ) )

		states = self.graph.nodes()
		n, m = len(states), len(self.graph.edges())
		silent_states, normal_states = [], []

		for state in states:
			if state.is_silent():
				silent_states.append(state)
			else:
				normal_states.append(state)

		# We need the silent states to be in topological sort order: any
		# transition between silent states must be from a lower-numbered state
		# to a higher-numbered state. Since we ban loops of silent states, we
		# can get away with this.
		
		# Get the subgraph of all silent states
		silent_subgraph = self.graph.subgraph(silent_states)
		
		# Get the sorted silent states. Isn't it convenient how NetworkX has
		# exactly the algorithm we need?
		silent_states_sorted = networkx.topological_sort(silent_subgraph)
		
		# What's the index of the first silent state?
		self.silent_start = len(normal_states)

		# Save the master state ordering. Silent states are last and in
		# topological order, so when calculationg forward algorithm
		# probabilities we can just go down the list of states.
		self.states = normal_states + silent_states_sorted 
		
		# We need a good way to get transition probabilities by state index that
		# isn't N^2 to build or store. So we will need a reverse of the above
		# mapping. It's awkward but asymptotically fine.

		indices = { self.states[i]: i for i in xrange(n) }

		# Create a matrix of ties, in order to allow tied-state training to
		# take place.

		self.tied = numpy.zeros(( self.silent_start, self.silent_start ),
			dtype=numpy.int32 )

		# Go through and see if the underlying distribution objects are the
		# same object.

		for i in xrange( self.silent_start ):
			for j in xrange( self.silent_start ):
				self.tied[i, j] = self.states[i].distribution is \
					self.states[j].distribution

		# This holds numpy array indexed [a, b] to transition log probabilities 
		# from a to b, where a and b are state indices. It starts out saying all
		# transitions are impossible.
		self.transition_log_probabilities = numpy.zeros((len(self.states), 
			len(self.states))) + float("-inf")
		self.in_transitions = numpy.zeros( len(self.graph.edges()), 
			dtype=numpy.int32 ) - 1
		self.in_edge_count = numpy.zeros( len(self.states)+1, 
			dtype=numpy.int32 ) 
		self.out_transitions = numpy.zeros( len(self.graph.edges()), 
			dtype=numpy.int32 ) - 1
		self.out_edge_count = numpy.zeros( len(self.states)+1, 
			dtype=numpy.int32 ) 

		# Now we need to find a way of storing in-edges for a state in a manner
		# that can be called in the cythonized methods below. This is basically
		# an inversion of the graph. We will do this by having two lists, one
		# list size number of nodes + 1, and one list size number of edges.
		# The node size list will store the beginning and end values in the
		# edge list that point to that node. The edge list will be ordered in
		# such a manner that all edges pointing to the same node are grouped
		# together. This will allow us to run the algorithms in time
		# nodes*edges instead of nodes*nodes.

		for a, b in self.graph.edges_iter():
			# Increment the total number of edges going to node b.
			self.in_edge_count[ indices[b]+1 ] += 1
			# Increment the total number of edges leaving node a.
			self.out_edge_count[ indices[a]+1 ] += 1

		# Determine if the model is infinite or not based on the number of edges
		# to the end state

		if self.in_edge_count[ indices[ self.end ]+1 ] == 0:
			self.finite = 0
		else:
			self.finite = 1

		# Take the cumulative sum so that we can associat
		self.in_edge_count = numpy.cumsum(self.in_edge_count, 
            dtype=numpy.int32)
		self.out_edge_count = numpy.cumsum(self.out_edge_count, 
            dtype=numpy.int32 )

		# Now we go through the edges again in order to both fill in the
		# transition probability matrix, and also to store the indices sorted
		# by the end-node.
		for a, b, data in self.graph.edges_iter(data=True):
			# Put the edge in the dict. Its weight is log-probability
			self.transition_log_probabilities[indices[a], indices[b]] = \
				data["weight"] 
			start = self.in_edge_count[ indices[b] ]

			# Start at the beginning of the section marked off for node b.
			# If another node is already there, keep walking down the list
			# until you find a -1 meaning a node hasn't been put there yet.
			while self.in_transitions[ start ] != -1:
				if start == self.in_edge_count[ indices[b]+1 ]:
					break
				start += 1

			# Store transition info in an array where the in_edge_count shows
			# the mapping stuff.
			self.in_transitions[ start ] = indices[a]

			# Now do the same for out edges
			start = self.out_edge_count[ indices[a] ]

			while self.out_transitions[ start ] != -1:
				if start == self.out_edge_count[ indices[a]+1 ]:
					break
				start += 1

			self.out_transitions[ start ] = indices[b]  

		# This holds the index of the start state
		try:
			self.start_index = indices[self.start]
		except KeyError:
			raise SyntaxError( "Model.start has been deleted, leaving the \
				model with no start. Please ensure it has a start." )
		# And the end state
		try:
			self.end_index = indices[self.end]
		except KeyError:
			raise SyntaxError( "Model.end has been deleted, leaving the \
				model with no end. Please ensure it has an end." )

	def sample( self, length=None, path=False ):
		"""
		Generate a sequence from the model. Returns the sequence generated, as a
		list of emitted items. The model must have been baked first in order to 
		run this method.

		If a length is specified and the HMM is infinite (no edges to the
		end state), then that number of samples will be randomly generated.
		If the length is specified and the HMM is finite, the method will
		attempt to generate a prefix of that length. Currently it will force
		itself to not take an end transition unless that is the only path,
		making it not a true random sample on a finite model.

		WARNING: If the HMM is infinite, must specify a length to use.

		If path is True, will return a tuple of ( sample, path ), where path is
		the path of hidden states that the sample took. Otherwise, the method
		will just return the path. Note that the path length may not be the same
		length as the samples, as it will return silent states it visited, but
		they will not generate an emission.
		"""
		
		# First prepare a table of cumulative transition probabilities.
		# Get the probabilities of all the transitions
		transition_probabilities = exp(self.transition_log_probabilities)
		
		# Calculate cumulative transition probabilities
		cum_probabilities = numpy.cumsum(transition_probabilities, 
			axis=1)
		
		# This holds the numerical index of the state we are currently in.
		# Start in the start state
		state = self.start_index
		
		# Record the number of samples
		n = 0
		# This holds the emissions
		emissions = []
		sequence_path = []

		while state != self.end_index:
			# Get the object associated with this state
			state_object = self.states[state]

			# Add the state to the growing path
			sequence_path.append( state_object )
			
			if state_object.distribution is not None:
				# There's an emission distribution, so sample from it
				emissions.append(state_object.distribution.sample())
				n += 1

			# If we've reached the specified length, return the appropriate
			# values
			if length and n >= length:
				return (emissions, sequence_path) if path else emissions

			# What should we pick as our next state?
			# Generate a random number between 0 and the total probability of 
			# this state (ought to be 1):
			sample = random.uniform(0, cum_probabilities[state, -1])
			
			# Save the last state id we were in
			last_state = state

			# Find out what state we're supposed to go into using bisect, and go
			# there
			state = bisect.bisect(cum_probabilities[state, :], sample)

			# If the user specified a length, and we're not at that length, and
			# we're in an infinite HMM, we want to avoid going to the end state
			# if possible. If there is only a single probability 1 end to the
			# end state we can't avoid it, otherwise go somewhere else.
			if length and self.finite == 1 and state == self.end_index:
				# If it's the only transition (log probability of 0), end
				if self.transition_log_probabilities[last_state, state] == 0:
					break

				# Else, sample until we find a new one. 
				while state == self.end_index:
					sample = random.uniform(0,cum_probabilities[last_state,-1])
					state = bisect.bisect(cum_probabilities[last_state, :], 
						sample)
			
		# We made it to the end state. Return our emission sequence.
		return (emissions, sequence_path) if path else emissions

	def forward( self, sequence ):
		'''
		Python wrapper for the forward algorithm, calculating probability by
		going forward through a sequence. Returns the full forward DP matrix.
		Each index i, j corresponds to the sum-of-all-paths log probability
		of starting at the beginning of the sequence, and aligning observations
		to hidden states in such a manner that observation i was aligned to
		hidden state j. Uses row normalization to dynamically scale each row
		to prevent underflow errors.

		If the sequence is impossible, will return a matrix of nans.

		input
			sequence: a list (or numpy array) of observations

		output
			A n-by-m matrix of floats, where n = len( sequence ) and
			m = len( self.states ). This is the DP matrix for the
			forward algorithm.

		See also: 
			- Silent state handling taken from p. 71 of "Biological
		Sequence Analysis" by Durbin et al., and works for anything which
		does not have loops of silent states.
			- Row normalization technique explained by 
		http://www.cs.sjsu.edu/~stamp/RUA/HMM.pdf on p. 14.
		'''

		return numpy.array( self._forward( numpy.array( sequence ) ) )

	cdef double [:,:] _forward( self, numpy.ndarray sequence ):
		"""
		Run the forward algorithm, and return the matrix of log probabilities
		of each segment being in each hidden state. 
		
		Initializes self.f, the forward algorithm DP table.
		"""

		cdef unsigned int D_SIZE = sizeof( double )
		cdef int i = 0, k, l, n = len( sequence ), m = len( self.states ), j = 0
		cdef double [:,:] f, e
		cdef double log_probability
		cdef State s
		cdef Distribution d
		cdef int [:] in_edges = self.in_edge_count
		cdef double [:] c

		# Initialize the DP table. Each entry i, k holds the log probability of
		# emitting i symbols and ending in state k, starting from the start
		# state.
		f = cvarray( shape=(n+1, m), itemsize=D_SIZE, format='d' )
		c = numpy.zeros( (n+1) )

		# Initialize the emission table, which contains the probability of
		# each entry i, k holds the probability of symbol i being emitted
		# by state k 
		e = cvarray( shape=(n,self.silent_start), itemsize=D_SIZE, format='d') 
		for k in xrange( n ):
			for i in xrange( self.silent_start ):
				s = <State>self.states[i]
				d = <Distribution>(s.distribution)
				log_probability = d.log_probability( sequence[k] )
				e[k, i] = log_probability

		# We must start in the start state, having emitted 0 symbols        
		for i in xrange(m):
			f[0, i] = NEGINF
		f[0, self.start_index] = 0.

		for l in xrange( self.silent_start, m ):
			# Handle transitions between silent states before the first symbol
			# is emitted. No non-silent states have non-zero probability yet, so
			# we can ignore them.
			if l == self.start_index:
				# Start state log-probability is already right. Don't touch it.
				continue

			# This holds the log total transition probability in from 
			# all current-step silent states that can have transitions into 
			# this state.  
			log_probability = NEGINF
			for k in xrange( in_edges[l], in_edges[l+1] ):
				k = self.in_transitions[k]
				if k < self.silent_start:
					continue
				if k >= l:
					continue

				# For each current-step preceeding silent state k
				log_probability = pair_lse( log_probability, 
					f[0, k] + self.transition_log_probabilities[k, l] )

			# Update the table entry
			f[0, l] = log_probability

		for i in xrange( n ):
			for l in xrange( self.silent_start ):
				# Do the recurrence for non-silent states l
				# This holds the log total transition probability in from 
				# all previous states

				log_probability = NEGINF
				for k in xrange( in_edges[l], in_edges[l+1] ):
					k = self.in_transitions[k]

					# For each previous state k
					log_probability = pair_lse( log_probability,
						f[i, k] + self.transition_log_probabilities[k, l] )

				# Now set the table entry for log probability of emitting 
				# index+1 characters and ending in state l
				f[i+1, l] = log_probability + e[i, l]

			for l in xrange( self.silent_start, m ):
				# Now do the first pass over the silent states
				# This holds the log total transition probability in from 
				# all current-step non-silent states
				log_probability = NEGINF
				for k in xrange( in_edges[l], in_edges[l+1] ):
					k = self.in_transitions[k]
					if k >= self.silent_start:
						continue

					# For each current-step non-silent state k
					log_probability = pair_lse( log_probability,
						f[i+1, k] + self.transition_log_probabilities[k, l] )

				# Set the table entry to the partial result.
				f[i+1, l] = log_probability

			for l in xrange( self.silent_start, m ):
				# Now the second pass through silent states, where we account
				# for transitions between silent states.

				# This holds the log total transition probability in from 
				# all current-step silent states that can have transitions into 
				# this state.
				log_probability = NEGINF
				for k in xrange( in_edges[l], in_edges[l+1] ):
					k = self.in_transitions[k]
					if k < self.silent_start:
						continue
					if k >= l:
						continue

					# For each current-step preceeding silent state k
					log_probability = pair_lse( log_probability,
						f[i+1, k] + self.transition_log_probabilities[k, l] )

				# Add the previous partial result and update the table entry
				f[i+1, l] = pair_lse( f[i+1, l], log_probability )

			# Now calculate the normalizing weight for this row, as described
			# here: http://www.cs.sjsu.edu/~stamp/RUA/HMM.pdf
			for l in xrange( m ):
				c[i+1] += cexp( f[i+1, l] )

			# Convert to log space, and subtract, instead of invert and multiply
			c[i+1] = clog( c[i+1] )
			for l in xrange( m ):
				f[i+1, l] -= c[i+1]

		# Go through and recalculate every observation based on the sum of the
		# normalizing weights.
		for i in xrange( n+1 ):
			for l in xrange( m ):
				for k in xrange( i+1 ):
					f[i, l] += c[k]

		# Save the table for future use
		self.f = f
		# Now the DP table is filled in
		# Return the entire table
		return f

	def backward( self, sequence ):
		'''
		Python wrapper for the backward algorithm, calculating probability by
		going backward through a sequence. Returns the full forward DP matrix.
		Each index i, j corresponds to the sum-of-all-paths log probability
		of starting with observation i aligned to hidden state j, and aligning
		observations to reach the end. Uses row normalization to dynamically 
		scale each row to prevent underflow errors.

		If the sequence is impossible, will return a matrix of nans.

		input
			sequence: a list (or numpy array) of observations

		output
			A n-by-m matrix of floats, where n = len( sequence ) and
			m = len( self.states ). This is the DP matrix for the
			backward algorithm.

		See also: 
			- Silent state handling is "essentially the same" according to
		Durbin et al., so they don't bother to explain *how to actually do it*.
		Algorithm worked out from first principles.
			- Row normalization technique explained by 
		http://www.cs.sjsu.edu/~stamp/RUA/HMM.pdf on p. 14.
		'''

		return numpy.array( self._backward( numpy.array( sequence ) ) )

	cdef double [:,:] _backward( self, numpy.ndarray sequence ):
		"""
		Run the backward algorithm, and return the log probability of the given 
		sequence. Sequence is a container of symbols.
		
		Initializes self.b, the backward algorithm DP table.
		"""

		cdef unsigned int D_SIZE = sizeof( double )
		cdef int i = 0, ir, k, kr, l, n = len( sequence ), m = len( self.states )
		cdef double [:,:] b, e
		cdef double log_probability
		cdef State s
		cdef Distribution d
		cdef int [:] out_edges = self.out_edge_count
		cdef double [:] c

		# Initialize the DP table. Each entry i, k holds the log probability of
		# emitting the remaining len(sequence) - i symbols and ending in the end
		# state, given that we are in state k.
		b = cvarray( shape=(n+1, m), itemsize=D_SIZE, format='d' )
		c = numpy.zeros( (n+1) )

		# Initialize the emission table, which contains the probability of
		# each entry i, k holds the probability of symbol i being emitted
		# by state k 
		e = cvarray( shape=(n,self.silent_start), itemsize=D_SIZE, format='d' )

		# Calculate the emission table
		for k in xrange( n ):
			for i in xrange( self.silent_start ):
				s = <State>self.states[i]
				d = <Distribution>(s.distribution)
				log_probability = d.log_probability( sequence[k] )
				e[k, i] = log_probability

		# We must end in the end state, having emitted len(sequence) symbols
		if self.finite == 1:
			for i in xrange(m):
				b[n, i] = NEGINF
			b[n, self.end_index] = 0
		else:
			for i in xrange(self.silent_start):
				b[n, i] = e[n-1, i]
			for i in xrange(self.silent_start, m):
				b[n, i] = NEGINF

		for kr in xrange( m-self.silent_start ):
			if self.finite == 0:
				break
			# Cython arrays cannot go backwards, so modify the loop to account
			# for this.
			k = m - kr - 1

			# Do the silent states' dependencies on each other.
			# Doing it in reverse order ensures that anything we can 
			# possibly transition to is already done.
			
			if k == self.end_index:
				# We already set the log-probability for this, so skip it
				continue

			# This holds the log total probability that we go to
			# current-step silent states and then continue from there to
			# finish the sequence.
			log_probability = NEGINF
			for l in xrange( out_edges[k], out_edges[k+1] ):
				l = self.out_transitions[l]
				if l < k+1:
					continue 
				# For each possible current-step silent state we can go to,
				# take into account just transition probability
				log_probability = pair_lse( log_probability,
					b[n,l] + self.transition_log_probabilities[k, l] )

			# Now this is the probability of reaching the end state given we are
			# in this silent state.
			b[n, k] = log_probability

		for k in xrange( self.silent_start ):
			if self.finite == 0:
				break
			# Do the non-silent states in the last step, which depend on
			# current-step silent states.
			
			# This holds the total accumulated log probability of going
			# to such states and continuing from there to the end.
			log_probability = NEGINF
			for l in xrange( out_edges[k], out_edges[k+1] ):
				l = self.out_transitions[l]
				if l < self.silent_start:
					continue

				# For each current-step silent state, add in the probability
				# of going from here to there and then continuing on to the
				# end of the sequence.
				log_probability = pair_lse( log_probability,
					b[n, l] + self.transition_log_probabilities[k, l] )

			# Now we have summed the probabilities of all the ways we can
			# get from here to the end, so we can fill in the table entry.
			b[n, k] = log_probability

		# Now that we're done with the base case, move on to the recurrence
		for ir in xrange( n ):
			#if self.finite == 0 and ir == 0:
			#	continue
			# Cython xranges cannot go backwards properly, redo to handle
			# it properly
			i = n - ir - 1
			for kr in xrange( m-self.silent_start ):
				k = m - kr - 1

				# Do the silent states' dependency on subsequent non-silent
				# states, iterating backwards to match the order we use later.
				
				# This holds the log total probability that we go to some
				# subsequent state that emits the right thing, and then continue
				# from there to finish the sequence.
				log_probability = NEGINF
				for l in xrange( out_edges[k], out_edges[k+1] ):
					l = self.out_transitions[l]
					if l >= self.silent_start:
						continue

					# For each subsequent non-silent state l, take into account
					# transition and emission emission probability.
					log_probability = pair_lse( log_probability,
						b[i+1, l] + self.transition_log_probabilities[k, l] +
						e[i, l] )

				# We can't go from a silent state here to a silent state on the
				# next symbol, so we're done finding the probability assuming we
				# transition straight to a non-silent state.
				b[i, k] = log_probability

			for kr in xrange( m-self.silent_start ):
				k = m - kr - 1

				# Do the silent states' dependencies on each other.
				# Doing it in reverse order ensures that anything we can 
				# possibly transition to is already done.
				
				# This holds the log total probability that we go to
				# current-step silent states and then continue from there to
				# finish the sequence.
				log_probability = NEGINF
				for l in xrange( out_edges[k], out_edges[k+1] ):
					l = self.out_transitions[l]
					if l < k+1:
						continue

					# For each possible current-step silent state we can go to,
					# take into account just transition probability
					log_probability = pair_lse( log_probability,
						b[i, l] + self.transition_log_probabilities[k, l] )

				# Now add this probability in with the probability accumulated
				# from transitions to subsequent non-silent states.
				b[i, k] = pair_lse( log_probability, b[i, k] )

			for k in xrange( self.silent_start ):
				# Do the non-silent states in the current step, which depend on
				# subsequent non-silent states and current-step silent states.
				
				# This holds the total accumulated log probability of going
				# to such states and continuing from there to the end.
				log_probability = NEGINF
				for l in xrange( out_edges[k], out_edges[k+1] ):
					l = self.out_transitions[l]
					if l >= self.silent_start:
						continue

					# For each subsequent non-silent state l, take into account
					# transition and emission emission probability.
					log_probability = pair_lse( log_probability,
						b[i+1, l] + self.transition_log_probabilities[k, l] +
						e[i, l] )

				for l in xrange( out_edges[k], out_edges[k+1] ):
					l = self.out_transitions[l]
					if l < self.silent_start:
						continue

					# For each current-step silent state, add in the probability
					# of going from here to there and then continuing on to the
					# end of the sequence.
					log_probability = pair_lse( log_probability,
						b[i, l] + self.transition_log_probabilities[k, l] )

				# Now we have summed the probabilities of all the ways we can
				# get from here to the end, so we can fill in the table entry.
				b[i, k] = log_probability

			# Now calculate the normalizing weight for this row, as described
			# here: http://www.cs.sjsu.edu/~stamp/RUA/HMM.pdf
			for l in xrange( m ):
				c[i] += cexp( b[i, l] )

			# Convert to log space, and subtract, instead of invert and multiply
			c[i] = clog( c[i] )
			for l in xrange( m ):
				b[i, l] -= c[i]

		# Go through and recalculate every observation based on the sum of the
		# normalizing weights.
		for ir in xrange( n+1 ):
			i = n - ir
			for l in xrange( m ):
				for k in xrange( i, n+1 ):
					b[i, l] += c[k]
				
		# Save the DP table for future use
		self.b = b

		# Now the DP table is filled in. 
		# Return the entire table.
		return b

	def forward_backward( self, sequence ):
		"""
		Implements the forward-backward algorithm. This is the sum-of-all-paths
		log probability that you start at the beginning of the sequence, align
		observation i to silent state j, and then continue on to the end.
		Simply, it is the probability of emitting the observation given the
		state and then transitioning one step.

		If the sequence is impossible, will return (None, None)

		input
			sequence: a list (or numpy array) of observations

		output
			A tuple of the estimated log transition probabilities, and
			the DP matrix for the FB algorithm. The DP matrix has
			n rows and m columns where n is the number of observations,
			and m is the number of non-silent states.

			* The estimated log transition probabilities are a m-by-m 
			matrix where index i, j indicates the log probability of 
			transitioning from state i to state j.

			* The DP matrix for the FB algorithm contains the sum-of-all-paths
			probability as described above.

		See also: 
			- Forward and backward algorithm implementations. A comprehensive
			description of the forward, backward, and forward-background
			algorithm is here: 
			http://en.wikipedia.org/wiki/Forward%E2%80%93backward_algorithm
		"""

		return self._forward_backward( numpy.array( sequence ) )

	cdef tuple _forward_backward( self, numpy.ndarray sequence ):
		"""
		Actually perform the math here.
		"""

		cdef int i, k, l
		cdef int m = len( self.states ), n = len( sequence )
		cdef double [:,:] transition_log_probabilities = \
			numpy.array( self.transition_log_probabilities ) 
		# Find the expected number of transitions between each pair of states, 
		# given our data and our current parameters, but allowing the paths 
		# taken to vary. (Indexed: from, to)
		cdef double [:,:] expected_transitions = numpy.zeros((m, m))
		cdef double [:,:] emission_weights = numpy.zeros((n, self.silent_start))

		cdef double log_sequence_probability, sequence_probability_sum
		cdef double log_transition_emission_probability_sum

		# Get the overall log probability of the sequence, and fill in self.f
		f = self.forward( sequence )
		if self.finite == 1:
			log_sequence_probability = f[ n, self.end_index ]
		else:
			log_sequence_probability = NEGINF
			for i in xrange( self.silent_start ):
				log_sequence_probability = pair_lse( log_sequence_probability, 
					f[n, i] )
		
		# Is the sequence impossible? If so, don't bother calculating any more.
		if log_sequence_probability == NEGINF:
			print( "Warning: Sequence is impossible." )
			return ( None, None )
			
		# Fill in self.b too
		b = self.backward( sequence )
			
		for k in xrange( m ):
			# For each state we could have come from
			for l in xrange( self.silent_start ):
				# For each state we could go to (and emit a character)
			
				# Sum up probabilities that we later normalize by 
				# probability of sequence.
				log_transition_emission_probability_sum = NEGINF
				for i in xrange( n ):
					# For each character in the sequence
					# Add probability that we start and get up to state k, 
					# and go k->l, and emit the symbol from l, and go from l
					# to the end.
					log_transition_emission_probability_sum = pair_lse( 
						log_transition_emission_probability_sum, 
						f[i, k] + transition_log_probabilities[k, l] +
						self.states[l].distribution.log_probability( 
							sequence[i] ) + b[ i+1, l ] )

				# Now divide by probability of the sequence to make it given
				# this sequence, and add as this sequence's contribution to 
				# the expected transitions matrix's k, l entry.
				expected_transitions[k, l] += cexp(
					log_transition_emission_probability_sum - 
					log_sequence_probability )
						
			for l in xrange( self.silent_start, m ):
				# For each silent state we can go to on the same character
					
				# Sum up probabilities that we later normalize by 
				# probability of sequence.
				log_transition_emission_probability_sum = NEGINF
				for i in xrange( n+1 ):
					# For each row in the forward DP table (where we can
					# have transitions to silent states) of which we have 1 
					# more than we have symbols...
						
					# Add probability that we start and get up to state k, 
					# and go k->l, and go from l to the end. In this case, 
					# we use forward and backward entries from the same DP 
					# table row, since no character is being emitted.
					log_transition_emission_probability_sum = pair_lse( 
						log_transition_emission_probability_sum, 
						f[i, k] + transition_log_probabilities[k, l] 
						+ b[i, l] )
					
				# Now divide by probability of the sequence to make it given
				# this sequence, and add as this sequence's contribution to 
				# the expected transitions matrix's k, l entry.
				expected_transitions[k, l] += cexp(
					log_transition_emission_probability_sum -
					log_sequence_probability )
				
			if k < self.silent_start:
				# Now think about emission probabilities from this state
						  
				for i in xrange( n ):
					# For each symbol that came out
		   
					# What's the weight of this symbol for that state?
					# Probability that we emit index characters and then 
					# transition to state l, and that from state l we  
					# continue on to emit len(sequence) - (index + 1) 
					# characters, divided by the probability of the 
					# sequence under the model.
					# According to http://www1.icsi.berkeley.edu/Speech/
					# docs/HTKBook/node7_mn.html, we really should divide by
					# sequence probability.

					emission_weights[i,k] = f[i+1, k] + b[i+1, k] - \
						log_sequence_probability

		# Connect the data of tied states, to ensure enough information comes
		# in to train them.
		cdef double tied_state_probability_sum
		for i in xrange( n ):
			for j in xrange( self.silent_start ):
				tied_state_probability_sum = 0
				for k in xrange( j, self.silent_start ): 
					if self.tied[j, k] == 1:
						tied_state_probability_sum += emission_weights[i, k]
				for k in xrange( j, self.silent_start ):
					if self.tied[j, k] == 1:
						emission_weights[i, k] = tied_state_probability_sum

		# Normalize transition expectations per row (so it becomes transition 
		# probabilities)
		# See http://stackoverflow.com/a/8904762/402891
		cdef double norm
		for i in xrange( m ):
			norm = 0
			for l in xrange( m ):
				norm += expected_transitions[i, l]
			if norm == 0:
				continue
			for l in xrange( m ):
				transition_log_probabilities[i, l] = \
					_log( expected_transitions[i, l] ) - _log( norm )

		return numpy.array( transition_log_probabilities ), \
			numpy.array( emission_weights )

	def viterbi(self, sequence):
		'''
		Run the Viterbi algorithm on the sequence given the model. This finds
		the ML path of hidden states given the sequence. Returns a tuple of the
		log probability of the ML path, or (-inf, None) if the sequence is
		impossible under the model. If a path is returned, it is a list of
		tuples of the form (sequence index, state object).

		This is fundamentally the same as the forward algorithm using max
		instead of sum, except the traceback is more complicated, because
		silent states in the current step can trace back to other silent states
		in the current step as well as states in the previous step.

		input
			sequence: a list (or numpy array) of observations

		output
			A tuple of the log probabiliy of the ML path, and the sequence of
			hidden states that comprise the ML path.

		See also: 
			- Viterbi implementation described well in the wikipedia article
			http://en.wikipedia.org/wiki/Viterbi_algorithm
		'''

		return self._viterbi( numpy.array( sequence ) )

	cdef tuple _viterbi(self, numpy.ndarray sequence):
		"""		
		This fills in self.v, the Viterbi algorithm DP table.
		
		This is fundamentally the same as the forward algorithm using max
		instead of sum, except the traceback is more complicated, because silent
		states in the current step can trace back to other silent states in the
		current step as well as states in the previous step.
		"""
		cdef unsigned int I_SIZE = sizeof( int ), D_SIZE = sizeof( double )

		cdef unsigned int n = sequence.shape[0], m = len(self.states)
		cdef double p
		cdef int i, l, k
		cdef int [:,:] tracebackx, tracebacky
		cdef double [:,:] v, e
		cdef double state_log_probability
		cdef Distribution d
		cdef State s
		cdef int[:] in_edges = self.in_edge_count

		# Initialize the DP table. Each entry i, k holds the log probability of
		# emitting i symbols and ending in state k, starting from the start
		# state, along the most likely path.
		v = cvarray( shape=(n+1,m), itemsize=D_SIZE, format='d' )

		# Initialize the emission table, which contains the probability of
		# each entry i, k holds the probability of symbol i being emitted
		# by state k 
		e = cvarray( shape=(n,self.silent_start), itemsize=D_SIZE, format='d' )

		# Initialize two traceback matricies. Each entry in tracebackx points
		# to the x index on the v matrix of the next entry. Same for the
		# tracebacky matrix.
		tracebackx = cvarray( shape=(n+1,m), itemsize=I_SIZE, format='i' )
		tracebacky = cvarray( shape=(n+1,m), itemsize=I_SIZE, format='i' )

		for k in xrange( n ):
			for i in xrange( self.silent_start ):
				s = <State>self.states[i]
				d = <Distribution>(s.distribution)
				p = d.log_probability( sequence[k] )
				e[k, i] = p

		# We catch when we trace back to (0, self.start_index), so we don't need
		# a traceback there.
		for i in xrange( m ):
			v[0, i] = NEGINF
		v[0, self.start_index] = 0
		# We must start in the start state, having emitted 0 symbols

		for l in xrange( self.silent_start, m ):
			# Handle transitions between silent states before the first symbol
			# is emitted. No non-silent states have non-zero probability yet, so
			# we can ignore them.
			if l == self.start_index:
				# Start state log-probability is already right. Don't touch it.
				continue

			for k in xrange( in_edges[l], in_edges[l+1] ):
				k = self.in_transitions[k]
				if k < self.silent_start:
					continue
				if k >= l:
					continue

				# For each current-step preceeding silent state k
				# This holds the log-probability coming that way
				state_log_probability = v[0, k] + \
					self.transition_log_probabilities[k, l]

				if state_log_probability > v[0, l]:
					# New winner!
					v[0, l] = state_log_probability
					tracebackx[0, l] = 0
					tracebacky[0, l] = k

		for i in xrange( n ):
			for l in xrange( self.silent_start ):
				# Do the recurrence for non-silent states l
				# Start out saying the best likelihood we have is -inf
				v[i+1, l] = NEGINF
				
				for k in xrange( in_edges[l], in_edges[l+1] ):
					k = self.in_transitions[k]

					# For each previous state k
					# This holds the log-probability coming that way
					state_log_probability = v[i, k] + \
						self.transition_log_probabilities[k, l] + e[i, l]

					if state_log_probability > v[i+1, l]:
						# Best to come from there to here
						v[i+1, l] = state_log_probability
						tracebackx[i+1, l] = i
						tracebacky[i+1, l] = k

			for l in xrange( self.silent_start, m ):
				# Now do the first pass over the silent states, finding the best
				# current-step non-silent state they could come from.
				# Start out saying the best likelihood we have is -inf
				v[i+1, l] = NEGINF

				for k in xrange( in_edges[l], in_edges[l+1] ):
					k = self.in_transitions[k]
					if k >= self.silent_start:
						continue

					# For each current-step non-silent state k
					# This holds the log-probability coming that way
					state_log_probability = v[i+1, k] + \
						self.transition_log_probabilities[k, l]

					if state_log_probability > v[i+1, l]:
						# Best to come from there to here
						v[i+1, l] = state_log_probability
						tracebackx[i+1, l] = i+1
						tracebacky[i+1, l] = k

			for l in xrange( self.silent_start, m ):
				# Now the second pass through silent states, where we check the
				# silent states that could potentially reach here and see if
				# they're better than the non-silent states we found.

				for k in xrange( in_edges[l], in_edges[l+1] ):
					k = self.in_transitions[k]
					if k < self.silent_start:
						continue
					if k >= l:
						continue

					# For each current-step preceeding silent state k
					# This holds the log-probability coming that way
					state_log_probability = v[i+1, k] + \
						self.transition_log_probabilities[k, l]

					if state_log_probability > v[i+1, l]:
						# Best to come from there to here
						v[i+1, l] = state_log_probability
						tracebackx[i+1, l] = i+1
						tracebacky[i+1, l] = k

		# Now the DP table is filled in. If this is a finite model, get the
		# log likelihood of ending up in the end state after following the
		# ML path through the model. If an infinite sequence, find the state
		# which the ML path ends in, and begin there.
		cdef int end_index
		cdef double log_likelihood
		if self.finite == 1:
			log_likelihood = v[n, self.end_index]
			end_index = self.end_index
		else:
			end_index = numpy.argmax( v[n] )
			log_likelihood = v[n, end_index ]

		# Save the viterbi matrix for future use
		self.v = v

		if log_likelihood == NEGINF:
			# The path is impossible, so don't even try a traceback. 
			return ( log_likelihood, None )

		# Otherwise, do the traceback
		# This holds the path, which we construct in reverse order
		cdef list path = []
		cdef int px = n, py = end_index, npx

		# This holds our current position (character, state) AKA (i, k).
		# We start at the end state
		while px != 0 or py != self.start_index:
			# Until we've traced back to the start...
			# Put the position in the path, making sure to look up the state
			# object to use instead of the state index.
			path.append( ( px, self.states[py] ) )

			# Go backwards
			npx = tracebackx[px, py]
			py = tracebacky[px, py]
			px = npx

		# We've now reached the start (if we didn't raise an exception because
		# we messed up the traceback)
		# Record that we start at the start
		path.append( (px, self.states[py] ) )

		# Flip the path the right way around
		path.reverse()

		# Return the log-likelihood and the right-way-arounded path
		return ( log_likelihood, path )

	def maximum_a_posteriori( self, sequence ):
		"""
		MAP decoding is an alternative to viterbi decoding, which returns the
		most likely state for each observation, based on the forward-backward
		algorithm. This is also called posterior decoding. This method is
		described on p. 14 of http://ai.stanford.edu/~serafim/CS262_2007/
		notes/lecture5.pdf

		WARNING: This may produce impossible sequences.
		"""

		transition_log_probabilities, emission_weights = self.forward_backward(
			sequence )

		# Calculate the index of the sum-of-all-paths log likelihood for all
		# observations, providing the maximum a posteriori path. 
		arg_max = numpy.argmax( emission_weights[:,:self.silent_start], axis=1 )

		# The log likelihood of the decoding is the joint of the log likelihood
		# of all states along the path. 
		log_likelihood = numpy.sum( numpy.max( emission_weights, axis=1 ) )
		
		# Convert to the index, state tuple 
		path = [ ( i, self.states[idx] ) for i, idx in enumerate( arg_max ) ]

		if self.finite == 1:
			# If the path is finite, add the end state to the path
			path.append( ( self.end_index, self.end ) )

		return log_likelihood, path

	def write(self, stream):
		"""
		Write out the HMM to the given stream in a format more sane than pickle.
		
		HMM must have been baked.
		
		HMM is written as its name and state count, a list of states, and then 
		a list of transitions of the form "<state> <state> <probability>" until 
		EoF.
		
		The start state is the one named "<hmm name>-start" and the end state is
		the one named "<hmm name>-end". Start and end states are always silent.
		
		Having the number of states on the first line makes the format harder 
		for humans to write, but saves us from having to write a real 
		backtracking parser.
		"""
		
		# Write our name.
		stream.write("{} {}\n".format(self.name, len(self.states)))
		
		for state in sorted(self.states, key=lambda s: s.name):
			# Write each state in order by name
			state.write(stream)
			
			
		# Get transitions.
		# Each is a tuple (from index, to index, log probability)
		transitions = []
		
		# We use Numpy iterators to accomplish this.
		# See http://docs.scipy.org/doc/numpy/reference/arrays.nditer.html
		# We also throw out transitions that don't exist.
		iterator = numpy.nditer(self.transition_log_probabilities, 
			flags=["multi_index"])
		while not iterator.finished:
			if iterator[0] != float("-inf"):
				# The transition is possible
				transitions.append((iterator.multi_index[0], 
					iterator.multi_index[1], iterator[0]))
			iterator.iternext()

		# Put transitions in a human-readable order. (alphabetical by from, then
		# by to)
		transitions.sort(key=lambda t: (self.states[t[0]].name, 
			self.states[t[1]].name))
			
		for (from_index, to_index, log_probability) in transitions:
			
			# Write each transition, using state names instead of indices.
			# This requires lookups and makes state names need to be unique, but
			# it's more human-readable and human-writeable.
			
			# Get the name of the state we're leaving
			from_name = self.states[from_index].name
			
			# And the one we're going to
			to_name = self.states[to_index].name
			
			# And the probability
			probability = exp(log_probability)
			
			# Write it out
			stream.write("{} {} {}\n".format(from_name, to_name, probability))
			
	@classmethod
	def read(cls, stream):
		"""
		Read a HMM from the given stream, in the format used by write(). The 
		stream must end at the end of the data defining the HMM.
		"""
		
		# Read the name and state count (first line)
		header = stream.readline()
		
		if header == "":
			raise EOFError("EOF reading HMM header")
		
		# Spilt out the parts of the headr
		parts = header.strip().split()
		
		# Get the HMM name
		name = parts[0]
		
		# Get the number of states to read
		num_states = int(parts[1])
		
		# Read and make the states.
		# Keep a dict of states by name
		states = {}
		
		for i in xrange(num_states):
			# Read in a state
			state = State.read(stream)
			
			# Store it in the state dict
			states[state.name] = state
			
		# We need to find the start and end states before we can make the HMM.
		# Luckily, we know their names.
		
		# Grab the start state
		start_state = states["{}-start".format(name)]
		end_state = states["{}-end".format(name)]
		
		# Make the HMM object to populate
		hmm = cls(name=name, start=start_state, end=end_state)
		
		for state in states.itervalues():
			if state != start_state and state != end_state:
				# This state isn't already in the HMM, so add it.
				hmm.add_state(state)
			
		# Now do the transitions (all the rest of the lines)
		for line in stream:
			# Pull out the from state name, to state name, and probability 
			# string
			(from_name, to_name, probability_string) = line.strip().split()
			
			# Make the probability as a float
			probability = float(probability_string)
			
			# Look up the states and add the transition
			hmm.add_transition(states[from_name], states[to_name], probability)
			
		# Now our HMM is done.
		# Bake and return it.
		hmm.bake()
		return hmm
	
	@classmethod
	def from_matrix( cls, transition_probabilities, distributions, starts, ends,
		state_names=None, name=None ):
		"""
		Take in a 2D matrix of floats of size n by n, which are the transition
		probabilities to go from any state to any other state. May also take in
		a list of length n representing the names of these nodes, and a model
		name. Must provide the matrix, and a list of size n representing the
		distribution you wish to use for that state, a list of size n indicating
		the probability of starting in a state, and a list of size n indicating
		the probability of ending in a state.

		For example, if you wanted a model with two states, A and B, and a 0.5
		probability of switching to the other state, 0.4 probability of staying
		in the same state, and 0.1 probability of ending, you'd write the HMM
		like this:

		matrix = [ [ 0.4, 0.5 ], [ 0.4, 0.5 ] ]
		distributions = [NormalDistribution(1, .5), NormalDistribution(5, 2)]
		starts = [ 1., 0. ]
		ends = [ .1., .1 ]
		state_names= [ "A", "B" ]

		model = Model.from_matrix( matrix, distributions, starts, ends, 
			state_names, name="test_model" )
		"""

		# Build the initial model
		model = Model( name=name )

		# Build state objects for every state with the appropriate distribution
		states = [ State( distribution, name=name ) for name, distribution in
			it.izip( state_names, distributions) ]

		n = len( states )

		# Add all the states to the model
		for state in states:
			model.add_state( state )

		# Connect the start of the model to the appropriate state
		for i, prob in enumerate( starts ):
			if prob != 0:
				model.add_transition( model.start, states[i], prob )

		# Connect all states to each other if they have a non-zero probability
		for i in xrange( n ):
			for j, prob in enumerate( transition_probabilities[i] ):
				if prob != 0.:
					model.add_transition( states[i], states[j], prob )

		# Connect states to the end of the model if a non-zero probability 
		for i, prob in enumerate( ends ):
			if prob != 0:
				model.add_transition( states[j], model.end, prob )

		model.bake()
		return model

	def train( self, sequences, stop_threshold=1E-9, min_iterations=0,
		max_iterations=None, algorithm='baum-welch', verbose=True ):
		"""
		Given a list of sequences, performs re-estimation on the model
		parameters. The two supported algorithms are "baum-welch" and
		"viterbi," indicating their respective algorithm. Neither algorithm
		makes use of inertia, meaning that the previous graph model is
		thrown out and replaced with the one generated from the training
		algorithm.

		Baum-Welch: Iterates until the log of the "score" (total likelihood of 
		all sequences) changes by less than stop_threshold. Returns the final 
		log score.
	
		
		Always trains for at least min_iterations.

		Viterbi: Training performed by running each sequence through the
		viterbi decoding algorithm. Edge weight re-estimation is done by 
		recording the number of times a hidden state transitions to another 
		hidden state, and using the percentage of time that edge was taken.
		Emission re-estimation is done by retraining the distribution on
		every sample tagged as belonging to that state.

		Baum-Welch training is usually the more accurate method, but takes
		significantly longer. Viterbi is a good for situations in which
		accuracy can be sacrificed for time.
		"""

		if algorithm.lower() == 'baum-welch':
			return self._train_baum_welch( sequences, stop_threshold,
				min_iterations, max_iterations, verbose )
		if algorithm.lower() == 'viterbi':
			return self._train_viterbi( sequences )

	def _train_baum_welch(self, sequences, stop_threshold, min_iterations, 
		max_iterations, verbose ):
		"""
		Given a list of sequences, perform Baum-Welch iterative re-estimation on
		the model parameters.
		
		Iterates until the log of the "score" (total likelihood of all 
		sequences) changes by less than stop_threshold. Returns the final log
		score.
		
		Always trains for at least min_iterations.
		"""

		sequences = numpy.array( sequences )
		for i, sequence in enumerate( sequences ):
			sequences[i] = numpy.array( sequence )

		# What's the current log score?
		log_score = self._train_once_baum_welch(sequences)
		# This holds how much we improve each step
		improvement = float("+inf")

		# How many iterations of training have we done (counting the first)
		iteration = 1
		while improvement > stop_threshold or iteration < min_iterations:
			if max_iterations and iteration >= max_iterations:
				break 

			# train again and get the new score
			new_log_score = self._train_once_baum_welch(sequences)
			
			iteration += 1
			
			# Calculate improvement signed, so we don't keep going if we 
			# decrease score
			improvement = new_log_score - log_score
			log_score = new_log_score
			
			if verbose:
				print( "Training improvement: {}".format(improvement) )
			
		return log_score

	cdef double _train_once_baum_welch(self, numpy.ndarray sequences ):
		"""
		Implements one iteration of the Baum-Welch algorithm, as described in:
		http://www.cs.cmu.edu/~durand/03-711/2006/Lectures/hmm-bw.pdf
			
		Returns the log of the "score" under the *previous* set of parameters. 
		The score is the sum of the likelihoods of all the sequences.
			
		Algorithm is generalized to work with silent states, and with continuous
		distributions according to the method that Prof. Karplus told me.
		"""        
			
		cdef double [:,:] transition_log_probabilities 
		cdef double [:,:] expected_transitions, e
		cdef list emitted_symbols 
		cdef double [:,:] emission_weights
		cdef numpy.ndarray sequence
		cdef double log_score, log_sequence_probability, weight
		cdef double equence_probability_sum
		cdef int k, i, l, m = len( self.states ), n, x=0, observation=0
		cdef object symbol
		cdef double [:] c

		transition_log_probabilities = self.transition_log_probabilities 
		# Find the expected number of transitions between each pair of states, 
		# given our data and our current parameters, but allowing the paths 
		# taken to vary. (Indexed: from, to)
		expected_transitions = numpy.zeros(( m, m ))
			
		# We also need to keep a list of all emitted symbols, and a list of 
		# weights for each state for each of those symbols.
		# This is the concatenated list of emitted symbols
		emitted_symbols = []

		total_characters = 0
		for sequence in sequences:
			total_characters += len( sequence )

		# This is a list lists of symbol weights, by state number, for 
		# non-silent states
		emission_weights = numpy.zeros(( self.silent_start, total_characters ))
			
		# Sum up the score to return
		log_score = NEGINF

		for sequence in sequences:
			n = len( sequence )

			# Calculate the emission table
			e = numpy.zeros(( n, self.silent_start )) 
			c = numpy.zeros( (n+1 ) )
			for k in xrange( n ):
				for i in xrange( self.silent_start ):
					e[k, i] = self.states[i].distribution.log_probability(
						sequence[k] )

			# Get the overall log probability of the sequence, and fill in self.f

			f = self.forward( sequence )
			if self.finite == 1:
				log_sequence_probability = f[ n, self.end_index ]
			else:
				log_sequence_probability = NEGINF
				for i in xrange( self.silent_start ):
					log_sequence_probability = pair_lse( f[n, i],
						log_sequence_probability )
				
			# Is the sequence impossible? If so, we can't train on it, so skip 
			# it
			if log_sequence_probability == NEGINF:
				print( "Warning: skipped impossible sequence {}".format(sequence) )
				continue
				
			# Add to the score
			log_score = pair_lse( log_score, log_sequence_probability )
				
			# Fill in self.b too
			b = self.backward(sequence)

			# Save the sequence in the running list of all emitted symbols
			for symbol in sequence:
				emitted_symbols.append(symbol)

			for k in xrange( m ):
				x = observation
				# For each state we could have come from
				for l in xrange( self.silent_start ):
					# For each state we could go to (and emit a character)
				
					# Sum up probabilities that we later normalize by 
					# probability of sequence.
					log_transition_emission_probability_sum = NEGINF
					for i in xrange( n ):
						# For each character in the sequence
						# Add probability that we start and get up to state k, 
						# and go k->l, and emit the symbol from l, and go from l
						# to the end.
						log_transition_emission_probability_sum = pair_lse( 
							log_transition_emission_probability_sum, 
							f[i, k] + 
							transition_log_probabilities[k, l] + 
							e[i, l] + b[ i+1, l ] )

					# Now divide by probability of the sequence to make it given
					# this sequence, and add as this sequence's contribution to 
					# the expected transitions matrix's k, l entry.

					expected_transitions[k, l] += cexp(
						log_transition_emission_probability_sum - 
						log_sequence_probability)

				for l in xrange( self.silent_start, m ):
					# For each silent state we can go to on the same character
						
					# Sum up probabilities that we later normalize by 
					# probability of sequence.
					log_transition_emission_probability_sum = NEGINF
					for i in xrange( n + 1 ):
						# For each row in the forward DP table (where we can
						# have transitions to silent states) of which we have 1 
						# more than we have symbols...

						# Add probability that we start and get up to state k, 
						# and go k->l, and go from l to the end. In this case, 
						# we use forward and backward entries from the same DP 
						# table row, since no character is being emitted.
						log_transition_emission_probability_sum = pair_lse( 
							log_transition_emission_probability_sum, 
							f[i, k] + transition_log_probabilities[k, l] 
							+ b[i, l] )

					# Now divide by probability of the sequence to make it given
					# this sequence, and add as this sequence's contribution to 
					# the expected transitions matrix's k, l entry.
					expected_transitions[k, l] += cexp(
						log_transition_emission_probability_sum -
						log_sequence_probability )

				if k < self.silent_start:
					# Now think about emission probabilities from this state
							  
					for i in xrange( n ):
						# For each symbol that came out
			   
						# What's the weight of this symbol for that state?
						# Probability that we emit index characters and then 
						# transition to state l, and that from state l we  
						# continue on to emit len(sequence) - (index + 1) 
						# characters, divided by the probability of the 
						# sequence under the model.
						# According to http://www1.icsi.berkeley.edu/Speech/
						# docs/HTKBook/node7_mn.html, we really should divide by
						# sequence probability.
						weight = cexp(f[i + 1, k] + b[i + 1, k] - 
							log_sequence_probability)

						# Add this weight to the weight list for this state
						emission_weights[k, x] = weight
						x += 1

			observation += n

		# We now have expected_transitions taking into account all sequences.
		# And a list of all emissions, and a weighting of each emission for each
		# state

		# Connect the data of tied states, to ensure enough information comes
		# in to train them.
		cdef double tied_state_probability_sum
		for i in xrange( total_characters ):
			for j in xrange( self.silent_start ):
				tied_state_probability_sum = 0
				for k in xrange( j, self.silent_start ): 
					if self.tied[j, k] == 1:
						tied_state_probability_sum += emission_weights[k, i]
				for k in xrange( j, self.silent_start ):
					if self.tied[j, k] == 1:
						emission_weights[k, i] = tied_state_probability_sum

		# Normalize transition expectations per row (so it becomes transition 
		# probabilities)
		# See http://stackoverflow.com/a/8904762/402891
		# Only modifies transitions for states a transition was observed from.
		# Work in log space
		cdef double norm

		for i in xrange( m ):
			norm = 0
			for l in xrange( m ):
				norm += expected_transitions[i, l]
			if norm == 0:
				continue
			for l in xrange( m ):
				transition_log_probabilities[i, l] = \
					_log( expected_transitions[i, l] ) - _log( norm )

		for k in xrange(self.silent_start):
			# Re-estimate the emission distribution for every non-silent state.
			# Take each emission weighted by the probability that we were in 
			# this state when it came out, given that the model generated the 
			# sequence that the symbol was part of.
			self.states[k].distribution.from_sample(emitted_symbols, 
				weights=emission_weights[k])
					
		# Now we have updated out transition log probabilities, and our emission
		# distributions.
		# Return the log total probability of all sequences (log score)
		self.transition_log_probabilities = transition_log_probabilities

		return log_score

	def _train_viterbi( self, sequences ):
		"""
		Performs a simple viterbi training algorithm. Each sequence is tagged
		using the viterbi algorithm, and both emissions and transitions are
		updated based on the probabilities in the observations.
		"""

		m = len( self.states )
		indices = { node: i for node, i in it.izip( self.states, xrange(m) ) }

		log_score = NEGINF
		emissions = {} 
		expected_transitions = numpy.zeros( (m,m) )

		for sequence in sequences:
			n = len( sequence )

			# Run the viterbi decoding on each observed sequence
			log_sequence_probability, sequence_path = self.viterbi( sequence )

			if log_sequence_probability[0] == NEGINF:
				print( "Warning: skipped impossible sequence {}".format(sequence) )
				continue

			# Filter out silent states, as they are not paired with an
			# observation
			filtered_path = filter( lambda state: not state[1].is_silent(), 
				sequence_path )

			# Update the log score 
			log_score = pair_lse( log_score, log_sequence_probability )

			# Assume that the starting character-generating hidden state is
			# the first hidden state after the start
			l = indices[ self.start ]
			k = indices[ filtered_path[0][1] ]
			expected_transitions[ l, k ] += 1

			# Assume the last character-generating hidden state is the last
			# hidden state before the end
			l = indices[ filtered_path[-1][1] ]
			k = indices[ self.end ]
			expected_transitions[ l, k ] += 1

			# Go through the path of character-generation states
			for (i, state), obs in it.izip( filtered_path, sequence ):
				# Add to a list of emissions from that state
				try:
					emissions[ state ].append( obs )
				except:
					emissions[ state ] = [ obs ]

			# Go through sequential pairs to add each edge to a matrix of counts
			for l, k in it.izip( xrange(n-1), xrange(1,n) ):
				l = indices[ filtered_path[l][1] ] 
				k = indices[ filtered_path[k][1] ]
				expected_transitions[ l, k ] += 1

		# Recalculate the emission distributions solely from new observations
		visited_states = []
		for state, emission in emissions.iteritems():
			i = indices[ state ]
			if i in visited_states:
				continue

			# Append all observations from all tied states
			# Train that distribution only once, to save time.
			visited_states.append( i )
			for j in xrange( self.silent_start ):
				if self.tied[i, j] == 1 and i != j:
					emission += emissions[ self.states[j] ]
					visited_states.append( j )

			state.distribution.from_sample( emission )

		# Normalize the matrix of counts to log probabilities
		row_norms = expected_transitions.sum( axis=1 )

		expected_transitions[row_norms != 0, :] = (
			log(expected_transitions[row_norms != 0, :])  -
			log(row_norms[row_norms != 0][:, numpy.newaxis]))

		expected_transitions[row_norms == 0, :] = NEGINF

		# Save the matrix as the new transition matrix
		self.transition_log_probabilities = expected_transitions

		return log_score
