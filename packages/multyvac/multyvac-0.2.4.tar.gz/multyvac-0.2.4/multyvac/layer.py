import base64
import json

from .multyvac import (
    Multyvac,
    MultyvacModel,
    MultyvacModule,
)

class Layer(MultyvacModel):
    """Represents a Multyvac Layer and its associated operations."""
    
    def __init__(self, name, **kwargs):
        """Creates a new layer."""
        MultyvacModel.__init__(self, **kwargs)
        
        self.name = name
        self.size = kwargs.get('size')
        self.created_at = kwargs.get('created_at')
    
    def mkdir(self, path):
        """
        Creates a new directory in the layer.
        :param path: Path to create new directory.
        """
        r = self.multyvac._ask(Multyvac._ASK_PUT,
                               '/layer/%s/mkdir' % self.name,
                               params={'path': path},
                               )
        return MultyvacModule.check_success(r)

    def put_contents(self, contents, target_path, target_mode=None):
        """
        Creates a new file with the specified contents.
        :param contents: A string of the contents of the new file.
        :param target_path: The path in the layer to create the new file.
        :param target_mode: The mode in octal notation of the new file.
            Ex. 0755.
        """
        files = {'file': (target_path, contents)}
        data = {'file_mode': target_mode}
        r = self.multyvac._ask(Multyvac._ASK_PUT,
                               '/layer/%s' % self.name,
                               files=files,
                               data=data,
                               )
        return MultyvacModule.check_success(r)

    def get_contents(self, path):
        """
        Returns the contents of the file as a string.
        :param path: The path to the file in this layer.
        """
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/layer/%s' % self.name,
                               params={'path': [path]},
                               )
        f = r['files'][0]
        f['contents'] = base64.b64decode(f['contents'])
        return f
    
    def get_file(self, remote_path, local_path):
        """
        Copies the file from the layer to the local filesystem.
        :param remote_path: Source path to file in layer.
        :param local_path: Destination path in local filesystem.
        """
        # FIXME: Make more memory efficient
        f = self.get_contents(remote_path)
        with open(local_path, 'w') as target_f:
            target_f.write(f['contents'])
    
    def put_file(self, local_path, remote_path, target_mode=None):
        """
        Copies the file from the local filesystem to the layer.
        :param local_path: Source path in local filesystem.
        :param remote_path: Destination path in layer.
        """
        # FIXME: Make more memory efficient
        with open(local_path) as f:
            self.put_contents(f.read(), remote_path, target_mode)
    
    def ls(self, path):
        """
        Lists the contents of a directory.
        
        Returns a list of dicts. Each dict specifies the path to an element,
        the mode, the size, and the type of element, file (f) or directory (d).
        
        :param path: Path to directory in layer.
        """
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/layer/%s/ls' % self.name,
                               params={'path': path},
                               )
        return r['ls']
    
    def rm(self, path):
        """Remove file or directory from the layer"""
        # TODO: Support recursive flag
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/layer/%s/rm' % self.name,
                               params={'path': path},
                               )
        return MultyvacModule.check_success(r)

    def modify(self, vol=None, max_runtime=3600):
        """
        Creates a job that can be SSH-ed into. You can SSH into this job,
        and any modifications you make to the filesystem will become a
        permanent part of the layer.
        
        Returns a job_id. You'll want to run layer.open_ssh_console(job_id)
        to open an SSH console to do things like "apt-get". You can also use
        sudo for root access.
        
        Be sure to call layer.snapshot(job_id) after you're done to kill
        the job and save your modifications.
        
        :param vol: The names of any volumes you want to have mounted in the
            new job.
        :param max_runtime: The number of seconds before the modification job
            is forcibly killed. This helps prevent runaway jobs.
        """
        jid = self.multyvac.job.shell_submit(
            'sleep %s' % max_runtime,
            _name='layer modify %s' % self.name,
            _vol=vol,
            _layer={'name': self.name, 'mount_rw': True},
        )
        return jid
    
    def open_ssh_console(self, jid):
        """Given a jid from `modify()`, this will wait for the job to start
        running, and then open an ssh console."""
        job = self.multyvac.job.get(jid)
        if not job.wait_for_open_port(22):
            raise Exception('Job did not open port 22. Standard error is "%s"'
                            % job.stderr)
        job.open_ssh_console()
    
    def get_ssh_info(self, jid):
        """
        Given a jid from `modify()`, returns a dict containing username,
        address, port, and identity_file to be used to SSH into the job.
        
        If job fails to start an SSH server for some reason, False is returned.
        """
        job = self.multyvac.job.get(jid)
        return job.wait_for_open_port(22)
    
    def snapshot(self, jid):
        """Saves the changes made to the layer"""
        job = self.multyvac.job.get(jid)
        job.run_command('killall -10 python')
        job.wait()

    def abort(self, jid):
        """Aborts the changes made to the layer."""
        job = self.multyvac.job.get(jid)
        job.kill()

    def __repr__(self):
        return "Layer(%s)" % repr(self.name)

class LayerModule(MultyvacModule):
    """Top-level Layer module. Use this through ``multyvac.layer``."""
    
    def get(self, name):
        """Returns the volume with :param name:."""
        ls = self.list(name)
        if ls:
            return ls[0]
    
    def create(self, name):
        """
        Creates a new layer.
        
        :param name: The name of the layer. Must not already exist.
        """
        layer = {'name': name,
                 }
        MultyvacModule.clear_null_entries(layer)
        payload = {'layer': layer}
        headers = {'content-type': 'application/json'}
        r = self.multyvac._ask(Multyvac._ASK_POST,
                               '/layer',
                               data=json.dumps(payload),
                               headers=headers)
        return MultyvacModule.check_success(r)

    def list(self, name=None):
        """
        Returns a list of layer objects.
        
        :param name: A string or list of strings to filter results to only a
            set of layers. 
        """
        params = {}
        if name:
            params['name'] = name
        r = self.multyvac._ask(Multyvac._ASK_GET,
                               '/layer',
                               params=params)
        for layer in r['layers']:
            layer['created_at'] = MultyvacModule.convert_str_to_datetime(layer['created_at'])
        return [Layer(multyvac=self.multyvac, **v) for v in r['layers']]
