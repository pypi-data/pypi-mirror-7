# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile
import logging
import StringIO
import yaml
import random
import crypt

from hyperkit.hypervisor.command import Command

logger = logging.getLogger(__name__)


class GenIsoImage(Command):
    command_name = "genisoimage"
    subcommands = {
        "generate": ["-output", "{pathname}", "-volid", "cidata", "-joliet", "-rock"],
    }
    log_execution = True


class CloudConfig:

    filename = "user-data"

    terms = [
        "package_upgrade",
        "package_update",
        "package_reboot_if_required",
        "packages",
        "runcmd",
        "write_files",
    ]

    def __init__(self, spec):
        self.spec = spec

    def get_config(self):
        config = {}
        for t in self.terms:
            if hasattr(self, t):
                config[t] = getattr(self, t)
        self.base_user(config)
        if self.password is not None:
            self.set_password_auth(config)
        if self.public_key is not None:
            self.set_public_key_auth(config)
        return config

    @property
    def username(self):
        return getattr(self.spec.auth, "username", None)

    @property
    def password(self):
        return getattr(self.spec.auth, "password", None)

    @property
    def public_key(self):
        return getattr(self.spec.auth, "public_key", None)

    @property
    def hashed_password(self):
        if self.password is None:
            return None
        return self.encrypt(self.password)

    def base_user(self, config):
        default_user = {
            "name": self.username,
            "gecos": "Yaybu",
            "homedir": "/home/%s" % self.username,
            "shell": "/bin/bash",
            "groups": ["adm", "audio", "cdrom", "dialout", "floppy", "video", "plugdev", "dip", "netdev"],
            "lock-passwd": False,
            "inactive": False,
            "sudo": "ALL=(ALL) NOPASSWD:ALL",
        }
        config['users'] = [default_user]

    def set_password_auth(self, config):
        config['users'][0]['passwd'] = self.hashed_password
        config['ssh_pwauth'] = True
        config['chpasswd'] = {'expire': False}
        config['password'] = self.password

    def set_public_key_auth(self, config):
        key = open(self.public_key).read()
        config['users'][0]['ssh-authorized-keys'] = [key]

    def encrypt(self, passwd):
        """ Return the password hash for the specified password """
        salt = self.generate_salt()
        return crypt.crypt(passwd, "$5${0}$".format(salt))

    def generate_salt(self, length=16):
        salt_set = ('abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    '0123456789./')
        return ''.join([random.choice(salt_set) for i in range(length)])

    def open(self):
        config = self.get_config()
        f = StringIO.StringIO()
        print >> f, "#cloud-config"
        print >> f, yaml.dump(config)
        return StringIO.StringIO(f.getvalue())


class MetaData:

    filename = "meta-data"

    def __init__(self, instance_id, localhost="localhost"):
        self.instance_id = instance_id
        self.localhost = localhost

    def as_dict(self):
        return {
            "local-hostname": self.localhost,
            "instance-id": self.instance_id,
        }

    def open(self):
        return StringIO.StringIO(yaml.dump(self.as_dict()))


class Seed:

    seed_file_name = "seed.iso"

    def __init__(self, directory, cloud_config, meta_data, *files):
        self.cloud_config = cloud_config
        self.meta_data = meta_data
        self.directory = directory
        self.files = [self.cloud_config, self.meta_data]
        self.files.extend(files)
        self.tmpdir = tempfile.mkdtemp()

    @property
    def pathname(self):
        return os.path.join(self.directory, self.seed_file_name)

    @property
    def filenames(self):
        for f in self.files:
            yield f.filename

    def _save(self):
        """ Overwrite the seed ISO file. Will clobber it potentially."""
        genisoimage = GenIsoImage()
        genisoimage("generate", *self.filenames, pathname=self.pathname, cwd=self.tmpdir)

    def open(self, filename):
        path = os.path.join(self.tmpdir, filename)
        return open(path, "w")

    def _output(self, cloudfile):
        fout = self.open(cloudfile.filename)
        fin = cloudfile.open()
        fout.write(fin.read())

    def write(self):
        for f in self.files:
            self._output(f)
        self._save()
        self._cleanup()

    def _cleanup(self):
        for f in self.filenames:
            os.unlink(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

__all__ = [MetaData, CloudConfig, Seed]
