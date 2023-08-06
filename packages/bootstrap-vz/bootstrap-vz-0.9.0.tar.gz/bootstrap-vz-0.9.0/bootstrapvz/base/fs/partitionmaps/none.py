from ..partitions.single import SinglePartition


class NoPartitions(object):
	"""Represents a virtual 'NoPartitions' partitionmap.
	This virtual partition map exists because it is easier for tasks to
	simply always deal with partition maps and then let the base abstract that away.
	"""

	def __init__(self, data, bootloader):
		"""
		:param dict data: volume.partitions part of the manifest
		:param str bootloader: Name of the bootloader we will use for bootstrapping
		"""
		from bootstrapvz.common.bytes import Bytes
		# In the NoPartitions partitions map we only have a single 'partition'
		self.root = SinglePartition(Bytes(data['root']['size']),
		                            data['root']['filesystem'], data['root'].get('format_command', None))
		self.partitions = [self.root]

	def is_blocking(self):
		"""Returns whether the partition map is blocking volume detach operations

		:rtype: bool
		"""
		return self.root.fsm.current == 'mounted'

	def get_total_size(self):
		"""Returns the total size the partitions occupy

		:return: The size of all the partitions
		:rtype: Bytes
		"""
		return self.root.get_end()
