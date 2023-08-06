from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import packages
from bootstrapvz.providers.virtualbox.tasks import guest_additions
from bootstrapvz.providers.ec2.tasks import ebs
from bootstrapvz.common.fs import remount
from shutil import copyfile
import os.path
import time
import logging
log = logging.getLogger(__name__)


class Snapshot(Task):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.package_installation
	predecessors = [packages.InstallPackages, guest_additions.InstallGuestAdditions]

	@classmethod
	def run(cls, info):
		def mk_snapshot():
			return info.volume.snapshot()
		snapshot = remount(info.volume, mk_snapshot)
		msg = 'A snapshot of the bootstrapped volume was created. ID: ' + snapshot.id
		log.info(msg)


class CreateFromSnapshot(Task):
	description = 'Creating EBS volume from a snapshot'
	phase = phases.volume_creation
	successors = [ebs.Attach]

	@classmethod
	def run(cls, info):
		snapshot = info.manifest.plugins['prebootstrapped']['snapshot']
		ebs_volume = info._ec2['connection'].create_volume(info.volume.size.get_qty_in('GiB'),
		                                                   info._ec2['host']['availabilityZone'],
		                                                   snapshot=snapshot)
		while ebs_volume.volume_state() != 'available':
			time.sleep(5)
			ebs_volume.update()

		info.volume.volume = ebs_volume
		set_fs_states(info.volume)


class CopyImage(Task):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.package_installation
	predecessors = [packages.InstallPackages, guest_additions.InstallGuestAdditions]

	@classmethod
	def run(cls, info):
		loopback_backup_name = 'volume-{id}.{ext}.backup'.format(id=info.run_id, ext=info.volume.extension)
		destination = os.path.join(info.manifest.bootstrapper['workspace'], loopback_backup_name)

		def mk_snapshot():
			copyfile(info.volume.image_path, destination)
		remount(info.volume, mk_snapshot)
		msg = 'A copy of the bootstrapped volume was created. Path: ' + destination
		log.info(msg)


class CreateFromImage(Task):
	description = 'Creating loopback image from a copy'
	phase = phases.volume_creation
	successors = [volume.Attach]

	@classmethod
	def run(cls, info):
		info.volume.image_path = os.path.join(info.workspace, 'volume.' + info.volume.extension)
		loopback_backup_path = info.manifest.plugins['prebootstrapped']['image']
		copyfile(loopback_backup_path, info.volume.image_path)

		set_fs_states(info.volume)


def set_fs_states(volume):
		volume.fsm.current = 'detached'

		p_map = volume.partition_map
		partitions_state = 'attached'
		from bootstrapvz.base.fs.partitionmaps.none import NoPartitions
		if isinstance(p_map, NoPartitions):
			partitions_state = 'formatted'
		else:
			p_map.fsm.current = 'unmapped'
			partitions_state = 'unmapped_fmt'
		for partition in p_map.partitions:
			partition.fsm.current = partitions_state
