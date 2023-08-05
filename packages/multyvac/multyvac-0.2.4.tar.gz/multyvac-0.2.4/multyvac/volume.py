import base64
import json
import os
import subprocess

from .multyvac import (
    Multyvac,
    MultyvacError,
    MultyvacModel,
    MultyvacModule,
)

class SyncError(MultyvacError):
    """Encapsulates errors during ``volume.sync_up()`` and
    ``volumesync_down()``."""
    pass

class Volume(MultyvacModel):
    """Represents a Multyvac Volume and its associated operations."""
    
    def __init__(self, name, **kwargs):
        """Creates a new volume."""
        MultyvacModel.__init__(self, **kwargs)
        
        self.name = name
        self.mount_path = kwargs.get('mount_path')
        self.mount_type = kwargs.get('mount_type')
        self.created_at = kwargs.get('created_at')
        self.size = kwargs.get('size')
        self.description = kwargs.get('description')
    
    def mkdir(self, path):
        """Creates a new directory at :param path:."""
        
        r = self.multyvac._ask(Multyvac._ASK_PUT,
                               '/volume/%s/mkdir' % self.name,
                               params={'path': path},
                               )
        return MultyvacModule.check_success(r)

    def put_contents(self, contents, target_path, target_mode=None):
        """
        Creates a new file with the specified contents.
        :param contents: A string of the contents of the new file.
        :param target_path: The path in the volume to create the new file.
        :param target_mode: The mode in octal notation of the new file.
             Ex. 0755.
        """
        files = {'file': (target_path, contents)}
        data = {'file_mode': target_mode}
        r = self.multyvac._ask(Multyvac._ASK_PUT,
                               '/volume/%s' % self.name,
                               files=files,
                               data=data,
                               )
        return MultyvacModule.check_success(r)

    def get_contents(self, path):
        """
        Returns the contents of the file as a string.
        :param path: The path to the file in this volume.
        """
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/volume/%s' % self.name,
                               params={'path': [path]},
                               )
        f = r['files'][0]
        f['contents'] = base64.b64decode(f['contents'])
        return f
    
    def get_file(self, remote_path, local_path):
        """
        Copies the file from the volume to the local filesystem.
        :param remote_path: Source path in volume.
        :param local_path: Destination path in local filesystem.
        """
        # FIXME: Make more memory efficient
        f = self.get_contents(remote_path)
        with open(local_path, 'w') as target_f:
            target_f.write(f['contents'])
    
    def put_file(self, local_path, remote_path, target_mode=None):
        """
        Copies a file from the local filesystem to the volume's.
        
        :param local_path: Source path in local filesystem.
        :param remote_path: Destination path in volume.
        """
        # FIXME: Make more memory efficient
        with open(local_path) as f:
            self.put_contents(f.read(), remote_path, target_mode)
    
    def ls(self, path):
        """
        Lists the contents of a directory.
        
        Returns a list of dicts. Each dict specifies the path to an element,
        the mode, the size, and the type of element, file (f) or directory (d).
        
        :param path: Path to directory.
        """
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/volume/%s/ls' % self.name,
                               params={'path': path},
                               )
        return r['ls']
    
    def rm(self, path):
        """Remove file or directory from volume"""
        # TODO: Support recursive flag
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/volume/%s/rm' % self.name,
                               params={'path': path},
                               )
        return MultyvacModule.check_success(r)

    def sync_up(self, local_path, remote_path, max_runtime=3600):
        """
        Syncs data up to Multyvac.
        
        :param local_path: Can be a string or list of strings.
        :param remote_path: The relative path in the volume to sync to.
        :param max_runtime: Number of seconds to allow the syncing job to run
            for before it's forcibly killed.
        
        This command only works if rsync is available on the system. 
        """
        
        if hasattr(local_path, '__iter__'):
            local_path = ' '.join(local_path)
        if remote_path.startswith('/'):
            raise ValueError('remote_path cannot be relative to root (/)')
        jid = self.multyvac.job.shell_submit(
            'sleep %s' % max_runtime,
            _name='volume sync up to %s' % self.name,
            _vol=[self.name],
        )
        job = self.multyvac.job.get(jid)
        try:
            if not job.wait_for_open_port(22):
                raise SyncError('Failed waiting for job to open port')
            port = job.ports['tcp']['22']['port']
            address = job.ports['tcp']['22']['address']
            
            cmd = ('rsync -avz -L -e " ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -p {port} -i {key_path}" '
                   '{local_path} multyvac@{address}:{remote_path}'.format(
                        port=port,
                        key_path=self.multyvac.config.path_to_private_key(),
                        local_path=local_path,
                        address=address,
                        remote_path=os.path.join(self.mount_path, remote_path))
                   )
            self.multyvac.volume._logger.info('Syncing up %s to %s:%s',
                                              local_path,
                                              self.name,
                                              remote_path)
            subprocess.check_output(cmd,
                                    #stderr=subprocess.PIPE,
                                    close_fds=True,
                                    shell=True)
        finally:
            job.kill()

    def sync_down(self, remote_path, local_path, max_runtime=3600):
        """
        Syncs data down from Multyvac.
        
        :param remote_path: The relative path in the volume to sync from.
        :param local_path: The local path to sync to.
        :param max_runtime: Number of seconds to allow the syncing job to run
            for before it's forcibly killed.
        
        This command only works if rsync is available on the system.
        """
        
        if remote_path.startswith('/'):
            raise ValueError('remote_path cannot be relative to root (/)')
        jid = self.multyvac.job.shell_submit(
            'sleep %s' % max_runtime,
            _name='volume sync down from %s' % self.name,
            _vol=[self.name],
        )
        job = self.multyvac.job.get(jid)
        try:
            if not job.wait_for_open_port(22):
                raise SyncError('Failed waiting for job to open port')
            port = job.ports['tcp']['22']['port']
            address = job.ports['tcp']['22']['address']
            
            cmd = ('rsync -avz -e " ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -p {port} -i {key_path}" '
                   'multyvac@{address}:{remote_path} {local_path}'.format(
                        port=port,
                        key_path=self.multyvac.config.path_to_private_key(),
                        local_path=local_path,
                        address=address,
                        remote_path=os.path.join(self.mount_path, remote_path))
                   )
            p = subprocess.Popen(cmd,
                                 stderr=subprocess.PIPE,
                                 close_fds=True,
                                 shell=True)
            _, stderr = p.communicate()
            if p.returncode:
                raise SyncError(stderr)
        finally:
            job.kill()

    def __repr__(self):
        return 'Volume(%s)' % repr(self.name)

class VolumeModule(MultyvacModule):
    """Top-level Volume module. Use this through ``multyvac.volume``."""
    
    def get(self, name):
        """
        Returns a Volume object.
        
        :param name: Name of volume.
        """
        vs = self.list(name)
        if vs:
            return vs[0]
    
    def create(self, name, mount_path, mount_type=None, description=None):
        """
        Creates a new volume.
        
        :param name: The name of the volume. Must not already exist.
        :param mount_path: The path in the filesystem that job's will see the
            volume mounted at.
        :param mount_type: Currently only 'bind' is supported.
        :param description: An optional description of the volume.
        """
        
        volume = {'name': name,
                  'mount_path': mount_path,
                  'mount_type': mount_type,
                  'description': description,
                  }
        MultyvacModule.clear_null_entries(volume)
        payload = {'volume': volume}
        headers = {'content-type': 'application/json'}
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/volume',
                               data=json.dumps(payload),
                               headers=headers)
        return MultyvacModule.check_success(r)

    def list(self, name=None):
        """
        Returns a list of volume objects.
        
        :param name: A string or list of strings to filter results to only a
            set of volumes. 
        """
        params = {}
        if name:
            params['name'] = name
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/volume',
                               params=params)
        for volume in r['volumes']:
            volume['created_at'] = MultyvacModule.convert_str_to_datetime(volume['created_at'])
        return [Volume(multyvac=self.multyvac, **v) for v in r['volumes']]
