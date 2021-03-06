import numpy as np
from trust_based_filterer import TrustBasedFilterer
from surprise import Dataset, AlgoBase, PredictionImpossible
from surprise.model_selection import cross_validate


class Inverse_distance_weighted_tbr(AlgoBase):

	def __init__(self, sim_options={}):

		AlgoBase.__init__(self, sim_options=sim_options)


	def fit(self, trainset):

		AlgoBase.fit(self, trainset)

		self.sim = self.compute_similarities()

		self._filterer = TrustBasedFilterer(list(trainset.all_ratings()), self.sim)

		return self


	def estimate(self, u, i):

		if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
			raise PredictionImpossible('User and/or item is unknown.')

		indexes = np.nonzero(self._filterer._customers_versus_products_table[:, i])[0]
		rate_array = self._filterer._customers_versus_products_table[indexes, i]
		weight_array = self._filterer._weight_matrix[u, indexes]
		"""
		indexes = np.argsort(weight_array)[-10:]
		"""
		indexes = np.argpartition(weight_array, max(-10, 1-weight_array.size))[-10:]

		rate_array = rate_array[indexes]
		weight_array = weight_array[indexes]

		numerator = np.sum(rate_array * weight_array)
		denominator = np.sum(weight_array)
		estimation = 0 if denominator == 0 else float(numerator)/denominator 

		return estimation


if __name__ == '__main__':
	data = Dataset.load_builtin('ml-100k')
	sim_options = {'name': 'cosine',}
	algo = Inverse_distance_weighted_tbr(sim_options=sim_options)
	cross_validate(algo, data, cv=5, verbose=True)