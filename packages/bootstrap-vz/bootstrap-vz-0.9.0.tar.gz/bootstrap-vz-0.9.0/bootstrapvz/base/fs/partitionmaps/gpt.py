from abstract import AbstractPartitionMap
from ..partitions.gpt import GPTPartition
from ..partitions.gpt_swap import GPTSwapPartition
from bootstrapvz.common.tools import log_check_call


class GPTPartitionMap(AbstractPartitionMap):
	"""Represents a GPT partition map
	"""

	def __init__(self, data, bootloader):
		"""
		:param dict data: volume.partitions part of the manifest
		:param str bootloader: Name of the bootloader we will use for bootstrapping
		"""
		from bootstrapvz.common.bytes import Bytes
		# List of partitions
		self.partitions = []

		# Returns the last partition unless there is none
		def last_partition():
			return self.partitions[-1] if len(self.partitions) > 0 else None

		# If we are using the grub bootloader we need to create an unformatted partition
		# at the beginning of the map. Its size is 1007kb, which we will steal from the
		# next partition.
		if bootloader == 'grub':
			from ..partitions.unformatted import UnformattedPartition
			self.grub_boot = UnformattedPartition(Bytes('1007KiB'), last_partition())
			# Mark the partition as a bios_grub partition
			self.grub_boot.flags.append('bios_grub')
			self.partitions.append(self.grub_boot)

		# The boot and swap partitions are optional
		if 'boot' in data:
			self.boot = GPTPartition(Bytes(data['boot']['size']),
			                         data['boot']['filesystem'], data['boot'].get('format_command', None),
			                         'boot', last_partition())
			self.partitions.append(self.boot)
		if 'swap' in data:
			self.swap = GPTSwapPartition(Bytes(data['swap']['size']), last_partition())
			self.partitions.append(self.swap)
		self.root = GPTPartition(Bytes(data['root']['size']),
		                         data['root']['filesystem'], data['root'].get('format_command', None),
		                         'root', last_partition())
		self.partitions.append(self.root)

		# We need to move the first partition to make space for the gpt offset
		gpt_offset = Bytes('17KiB')
		self.partitions[0].offset += gpt_offset

		if hasattr(self, 'grub_boot'):
			# grub_boot should not increase the size of the volume,
			# so we reduce the size of the succeeding partition.
			# gpt_offset is included here, because of the offset we added above (grub_boot is partition[0])
			self.partitions[1].size -= self.grub_boot.get_end()
		else:
			# Avoid increasing the volume size because of gpt_offset
			self.partitions[0].size -= gpt_offset

		super(GPTPartitionMap, self).__init__(bootloader)

	def _before_create(self, event):
		"""Creates the partition map
		"""
		volume = event.volume
		# Disk alignment still plays a role in virtualized environment,
		# but I honestly have no clue as to what best practice is here, so we choose 'none'
		log_check_call(['parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'gpt'])
		# Create the partitions
		for partition in self.partitions:
			partition.create(volume)
