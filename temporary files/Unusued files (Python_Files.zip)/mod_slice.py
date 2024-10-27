# mod_slice will slice an array but wrap around so mod_slice(('a','b','c'), 0, 5, 1) will return ['a', 'b', 'c', 'a', 'b']
def mod_slice(arr, start, stop, step=1):
	length = len(arr)
	indices = range(start, stop, step)

	# Wrap each index using modulo
	wrapped_indices = [(i % length) for i in indices]

	# Use list comprehension to get the elements
	return [arr[i] for i in wrapped_indices]