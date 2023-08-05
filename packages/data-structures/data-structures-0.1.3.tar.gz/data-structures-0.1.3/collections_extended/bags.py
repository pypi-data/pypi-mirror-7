import heapq
from operator import itemgetter
from collections import Set, Sized, Iterable, Container, Hashable

class _basebag(Sized, Iterable, Container):
	""" Base class for bag and frozenbag.	Is not mutable and not hashable, so there's 
	no reason to use this instead of either bag or frozenbag.
	"""
	## Basic object methods

	def __init__(self, iterable=None):
		""" Create a new basebag.  If iterable isn't given, is None or is empty then the 
		bag starts empty.  Otherwise each element from iterable will be added to the bag 
		however many times it appears.

		This runs in O(len(iterable))

		>>> _basebag()                     # create empty bag
		_basebag()
		>>> b =_basebag('abracadabra')        # create from an Iterable
		>>> b.count('a')
		5
		>>> b.count('b')
		2
		>>> b.count('r')
		2
		>>> b.count('c')
		1
		>>> b.count('d')
		1
		"""
		self._dict = dict()
		self._size = 0
		if iterable:
			if isinstance(iterable, _basebag):
				for elem, count in iterable._dict.items():
					self._inc(elem, count)
			else:
				for value in iterable:
					self._inc(value)
	
	def __repr__(self):
		""" The string representation is a call to the constructor given a tuple 
		containing all of the elements.
		
		This runs in whatever tuple(self) does, I'm assuming O(len(self))

		>>> ms = _basebag()
		>>> ms == eval(ms.__repr__())
		True
		>>> ms = _basebag('abracadabra')
		>>> ms == eval(ms.__repr__())
		True
		"""
		if self._size == 0:
			return '{0}()'.format(self.__class__.__name__)
		else:
			format = '{class_name}({tuple!r})'
			return format.format(class_name=self.__class__.__name__, tuple=tuple(self))
	
	def __str__(self):
		""" The printable string appears just like a set, except that each element 
		is raised to the power of the multiplicity if it is greater than 1.

		This runs in O(self.num_unique_elements())

		>>> print(_basebag())
		bag()
		>>> "'a'^5" in str(_basebag('abracadabra'))
		True
		>>> "'b'^2" in str(_basebag('abracadabra'))
		True
		>>> "'c'" in str(_basebag('abracadabra'))
		True
		>>> str(_basebag('abc')) == str(set('abc'))
		True
		"""
		if self._size == 0:
			return 'bag()'
		else:
			format_single = '{elem!r}'
			format_mult = '{elem!r}^{mult}'
			strings = []
			for elem, mult in self._dict.items():
				if mult > 1:
					strings.append(format_mult.format(elem=elem, mult=mult))
				else:
					strings.append(format_single.format(elem=elem))
			return '{{{}}}'.format(', '.join(strings))

	## Internal methods

	def _set(self, elem, value):
		""" Set the multiplicity of elem to count. 
		
		This runs in O(1) time
		"""
		if value < 0:
			raise ValueError
		old_count = self.count(elem)
		if value == 0:
			if elem in self:
				del self._dict[elem]
		else:
			self._dict[elem] = value
		self._size += value - old_count

	def _inc(self, elem, count=1):
		""" Increment the multiplicity of value by count (if count <0 then decrement). """
		self._set(elem, self.count(elem) + count)

	## New public methods (not overriding/implementing anything)

	def num_unique_elements(self):
		""" Returns the number of unique elements. 
		
		This runs in O(1) time
		"""
		return len(self._dict)

	def unique_elements(self):
		""" Returns a view of unique elements in this bag. 
		
		This runs in O(1) time
		"""
		return self._dict.keys()

	def count(self, value):
		""" Return the multiplicity of value.  If value is not in the bag no Error is
		raised, instead 0 is returned. 
		
		This runs in O(1) time

		>>> ms = _basebag('abracadabra')

		>>> ms.count('a')
		5
		>>> ms.count('x')
		0
		"""
		try:
			return self._dict[value]
		except KeyError:
			return 0
	
	def nlargest(self, n=None):
		""" List the n most common elements and their counts from the most
		common to the least.  If n is None, the list all element counts.

		Run time should be O(m log m) where m is len(self)

		>>> sorted(_basebag('abracadabra').nlargest(), key=lambda e: (-e[1], e[0]))
		[('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]
		>>> sorted(_basebag('abracadabra').nlargest(3), key=lambda e: (-e[1], e[0]))
		[('a', 5), ('b', 2), ('r', 2)]
		>>> _basebag('abcaba').nlargest(3)
		[('a', 3), ('b', 2), ('c', 1)]
		"""
		if n is None:
			return sorted(self._dict.items(), key=itemgetter(1), reverse=True)
		else:
			return heapq.nlargest(n, self._dict.items(), key=itemgetter(1))

	@classmethod
	def _from_iterable(cls, it):
		return cls(it)

	@classmethod
	def _from_map(cls, map):
		""" Creates a bag from a dict of elem->count.  Each key in the dict 
		is added if the value is > 0.

		This runs in O(len(map))
		
		>>> _basebag._from_map({'a': 1, 'b': 2}) == _basebag('abb')
		True
		"""
		out = cls()
		for elem, count in map.items():
			out._inc(elem, count)
		return out

	def copy(self):
		""" Create a shallow copy of self.

		This runs in O(len(self.num_unique_elements()))
		
		>>> _basebag().copy() == _basebag()
		True
		>>> abc = _basebag('abc')

		>>> abc.copy() == abc
		True
		"""
		return self._from_map(self._dict)

	## implementing Sized methods

	def __len__(self):
		""" Returns the cardinality of the bag. 

		This runs in O(1)
		
		>>> len(_basebag())
		0
		>>> len(_basebag('abc'))
		3
		>>> len(_basebag('aaba'))
		4
		"""
		return self._size

	## implementing Container methods

	def __contains__(self, value):
		""" Returns the multiplicity of the element. 

		This runs in O(1)
		
		>>> 'a' in _basebag('bbac')
		True
		>>> 'a' in _basebag()
		False
		>>> 'a' in _basebag('missing letter')
		False
		"""
		return self.count(value)
	
	## implementing Iterable methods

	def __iter__(self):
		""" Iterate through all elements, multiple copies will be returned if they exist. """
		for value, count in self._dict.items():
			for i in range(count):
				yield(value)

	## Comparison methods
	
	def __le__(self, other):
		""" Tests if self <= other where other is another bag

		This runs in O(l + n) where:
			n is self.num_unique_elements()
			if other is a bag:
				l = 1
			else:
				l = len(other)

		>>> _basebag() <= _basebag()
		True
		>>> _basebag() <= _basebag('a')
		True
		>>> _basebag('abc') <= _basebag('aabbbc')
		True
		>>> _basebag('abbc') <= _basebag('abc')
		False
		"""
		if not isinstance(other, _basebag):
			return NotImplemented
		if len(self) > len(other):
			return False
		for elem in self.unique_elements():
			if self.count(elem) > other.count(elem):
				return False
		return True

	def __lt__(self, other):
		return self <= other and len(self) < len(other)

	def __gt__(self, other):
		return other < self

	def __ge__(self, other):
		return other <= self

	def __eq__(self, other):
		if not isinstance(other, _basebag):
			return False
		return len(self) == len(other) and self <= other 

	def __ne__(self, other):
		return not (self == other)

	## Operations - &, |, +, -, ^, * and isdisjoint

	def __and__(self, other):
		""" Intersection is the minimum of corresponding counts. 
		
		This runs in O(l + n) where:
			n is self.num_unique_elements()
			if other is a bag:
				l = 1
			else:
				l = len(other)

		>>> bag('aabc') & bag('aacd') == bag('aac')
		True
		>>> bag() & bag('safgsd') == bag()
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		values = dict()
		for elem in self._dict:
			values[elem] = min(other.count(elem), self.count(elem))
		return self._from_map(values)

	def isdisjoint(self, other):
		""" This runs in O(len(other))

		TODO move isdisjoint somewhere more appropriate
		>>> bag().isdisjoint(bag())
		True
		>>> bag().isdisjoint(bag('abc'))
		True
		>>> bag('ab').isdisjoint(bag('ac'))
		False
		>>> bag('ab').isdisjoint(bag('cd'))
		True
		"""
		for value in other:
			if value in self:
				return False
		return True

	def __or__(self, other):
		""" Union is the maximum of all elements. 
		
		This runs in O(m + n) where:
			n is self.num_unique_elements()
			if other is a bag:
				m = other.num_unique_elements()
			else:
				m = len(other)

		>>> bag('abcc') | bag() == bag('abcc')
		True
		>>> bag('abcc') | bag('aabd') == bag('aabccd')
		True
		>>> bag('aabc') | set('abdd') == bag('aabcd')
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		values = dict()
		for elem in self.unique_elements() | other.unique_elements():
			values[elem] = max(self.count(elem), other.count(elem))
		return self._from_map(values)

	def __add__(self, other):
		"""
		other can be any iterable.
		self + other = self & other + self | other 

		This runs in O(m + n) where:
			n is self.num_unique_elements()
			m is len(other)
		
		>>> bag('abcc') & bag() == bag()
		True
		>>> bag('abcc') & bag('aabd') == bag('ab')
		True
		>>> bag('aabc') & set('abdd') == bag('ab')
		True
		"""
		out = self.copy()
		for value in other:
			out._inc(value)
		return out
	
	def __sub__(self, other):
		""" Difference between the sets.
		other can be any iterable.
		For normal sets this is all s.t. x in self and x not in other. 
		For bags this is count(x) = max(0, self.count(x)-other.count(x))

		This runs in O(m + n) where:
			n is self.num_unique_elements()
			m is len(other)

		>>> bag('abc') - bag() == bag('abc')
		True
		>>> bag('abbc') - bag('bd') == bag('abc')
		True
		"""
		out = self.copy()
		for value in other:
			try:
				out._inc(value, -1)
			except ValueError:
				pass
		return out

	def __mul__(self, other):
		""" Cartesian product of the two sets.
		other can be any iterable.
		Both self and other must contain elements that can be added together.

		This should run in O(m*n+l) where:
			m is the number of unique elements in self
			n is the number of unique elements in other
			if other is a bag:
				l is 0
			else:
				l is the len(other)
		The +l will only really matter when other is an iterable with MANY repeated elements
		For example: {'a'^2} * 'bbbbbbbbbbbbbbbbbbbbbbbbbb'
		The algorithm will be dominated by counting the 'b's

		>>> ms = _basebag('aab')

		>>> ms * set('a') == _basebag(('aa', 'aa', 'ba'))
		True
		>>> ms * set() == _basebag()
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		values = dict()
		for elem, count in self._dict.items():
			for other_elem, other_count in other._dict.items():
				new_elem = elem + other_elem
				new_count = count * other_count
				values[new_elem] = new_count
		return self._from_map(values)

	def __xor__(self, other):
		""" Symmetric difference between the sets. 
		other can be any iterable.

		This runs in O(m + n) where:
			m = len(self)
			n = len(other)

		>>> bag('abc') ^ bag() == bag('abc')
		True
		>>> bag('aabc') ^ bag('ab') == bag('ac')
		True
		>>> bag('aabcc') ^ bag('abcde') == bag('acde')
		True
		"""
		return (self - other) | (other - self)

class bag(_basebag):
	""" bag is a mutable _basebag, thus not hashable and unusable for dict keys or in
	other sets.
	"""

	def pop(self):
		# TODO can this be done more efficiently (no need to create an iterator)?
		it = iter(self)
		try:
			value = next(it)
		except StopIteration:
			raise KeyError
		self.discard(value)
		return value

	def add(self, elem):
		self._inc(elem, 1)
	
	def discard(self, elem):
		try:
			self.remove(elem)
		except ValueError:
			pass

	def remove(self, elem):
		self._inc(elem, -1)

	def clear(self):
		self._dict = dict()
		self._size = 0

	## In-place operations

	def __ior__(self, other):
		"""
		if isinstance(other, _basebag):
			This runs in O(other.num_unique_elements())
		else:
			This runs in O(len(other))

		>>> b = bag()
		>>> b |= bag()
		>>> b == bag()
		True
		>>> b = bag('aab')
		>>> b |= bag()
		>>> b == bag('aab')
		True
		>>> b = bag('aab')
		>>> b |= bag('ac')
		>>> b == bag('aabc')
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		for elem, other_count in other._dict.items():
			self_count = self.count(elem)
			self._set(elem, max(other_count, self_count))
		return self
	
	def __iand__(self, other):
		"""
		if isinstance(other, _basebag):
			This runs in O(other.num_unique_elements())
		else:
			This runs in O(len(other))

		>>> b = bag()
		>>> b &= bag()
		>>> print(b)
		bag()
		>>> b = bag('aab')
		>>> b &= bag()
		>>> print(b)
		bag()
		>>> b = bag('aab')
		>>> b &= bag('ac')
		>>> print(b)
		{'a'}
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		for elem, self_count in set(self._dict.items()):
			other_count = other.count(elem)
			self._set(elem, min(other_count, self_count))
		return self
	
	def __ixor__(self, other):
		"""
		if isinstance(other, _basebag):
			This runs in O(other.num_unique_elements())
		else:
			This runs in O(len(other))

		>>> b = bag('abbc')
		>>> b ^= bag('bg')
		>>> b == bag('abcg')
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		other_minus_self = other - self
		self -= other
		self |= other_minus_self
		return self
	
	def __isub__(self, other):
		"""
		if isinstance(it, _basebag):
			This runs in O(it.num_unique_elements())
		else:
			This runs in O(len(it))

		>>> b = bag('aabbc')
		>>> b -= bag('bd')
		>>> b == bag('aabc')
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		for elem, count in other._dict.items():
			try:
				self._inc(elem, -count)
			except ValueError:
				pass
		return self

	def __iadd__(self, other):
		"""
		if isinstance(it, _basebag):
			This runs in O(it.num_unique_elements())
		else:
			This runs in O(len(it))

		>>> b = bag('abc')
		>>> b += bag('cde')
		>>> b == bag('abccde')
		True
		"""
		if not isinstance(other, _basebag):
			other = self._from_iterable(other)
		for elem, count in other._dict.items():
			self._inc(elem, count)
		return self
	

class frozenbag(_basebag, Hashable):
	""" frozenbag is a Hashable _basebag, thus it is immutable and usable for dict keys
	"""
	def __hash__(self):
		""" Use the hash funtion from Set,
		I'm not sure that it works for collections with multiple elements.

		>>> hash(frozenbag()) == hash(frozenbag((0,)))
		False
		>>> hash(frozenbag('a')) == hash(frozenbag(('aa')))
		False
		>>> hash(frozenbag('a')) == hash(frozenbag(('aaa')))
		False
		>>> hash(frozenbag('a')) == hash(frozenbag(('aaaa')))
		False
		>>> hash(frozenbag('a')) == hash(frozenbag(('aaaaa')))
		False
		>>> hash(frozenbag('ba')) == hash(frozenbag(('ab')))
		True
		>>> hash(frozenbag('badce')) == hash(frozenbag(('dbeac')))
		True
		"""
		return Set._hash(self)

