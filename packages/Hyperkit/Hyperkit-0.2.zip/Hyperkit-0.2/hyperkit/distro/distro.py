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

import abc
import os
import urllib2
import logging

from hyperkit.spec import image
from hyperkit.error import FetchFailedException

logger = logging.getLogger(__name__)


class DistroImage(image.BaseDistroImage):

    """ Represents a cloud image file for a specified release and
    architecture, with a local copy of the image, which is only downloaded if
    required. If no image exists locally it is fetched from the source
    provided by the distribution. """

    # size of blocks fetched from remote resources
    blocksize = 81920

    def __init__(self, pathname, release, arch):
        self.pathname = pathname
        self.release = release
        self.arch = arch
        self.remote_hash = None
        self.local_hash = None

    @abc.abstractproperty
    def hash_function(self):
        """ The hash function used to hash local files """

    @abc.abstractmethod
    def remote_image_url(self):
        """ Return a complete url of the remote virtual machine image """

    @abc.abstractmethod
    def remote_hashfile_url(self):
        """ Return a complete url of the remote hash file that contains the
        hash for the virtual machine image. Return None if no hash file is
        available. """

    @abc.abstractmethod
    def image_hash(self, hashes):
        """ From the dictionary of all hashes provided in the remote hash
        file, return the hash of the virtual machine image """

    def fetch(self):
        """ Fetch the remote image to the local pathname. """
        remote_url = self.remote_image_url()
        logger.info("Retrieving {0} to {1}".format(remote_url, self.pathname))
        try:
            response = urllib2.urlopen(remote_url)
        except urllib2.HTTPError:
            raise FetchFailedException("Unable to fetch {0}".format(remote_url))
        local = open(self.pathname, "w")
        while True:
            data = response.read(self.blocksize)
            if not data:
                break
            local.write(data)

    def decode_hashes(self, data):
        """ Parse the hash file data provided and return a dictionary of hash values keyed on filenames.
        Hash file formats vary quite a bit, this is quite tolerant.
        """
        hashes = {}
        for line in data.splitlines():
            parts = line.strip().split()
            if len(parts) == 2:
                value, filename = parts[0], parts[1]
                if filename in hashes:
                    raise KeyError("Two hashes for the same file: {0}".format(filename))
                hashes[filename] = value
        return hashes

    def get_remote_hashes(self):
        """ Fetch the remote hash file and return the decoded hashes. """
        remote_url = self.remote_hashfile_url()
        logger.info("Checking remote hashes")
        logger.debug("Fetching {0}".format(remote_url))
        try:
            response = urllib2.urlopen(remote_url)
        except urllib2.HTTPError:
            return {}
        return self.decode_hashes(response.read())

    def get_local_sum(self):
        """ Calculate the sum for the local downloaded image. """
        h = self.hash_function()
        if os.path.exists(self.pathname):
            h.update(open(self.pathname).read())
            return h.hexdigest()

    def update_hashes(self):
        """ Fetch the remote and local hashes. The remote hash is presumed
        not to change once we have it once. """
        if self.remote_hash is None:
            self.remote_hash = self.image_hash(self.get_remote_hashes())
        self.local_hash = self.get_local_sum()

    def requires_update(self):
        """ Returns true if the local file needs to be downloaded. """
        if self.local_hash is None:
            logger.info("Image not present locally, fetching")
            return True
        elif self.local_hash != self.remote_hash:
            logger.info("Local image does not match remote sum, fetching")
            return True
        else:
            return False

    def update(self):
        """ Check if the file needs to be updated, and update it if so.
        Throws an error if the image still doesn't match the remote hash once
        downloaded. """
        self.update_hashes()
        if self.requires_update():
            self.fetch()
        self.update_hashes()
        if self.requires_update():
            logger.error("Local image sum {0} does not match remote {1} after fetch.".format(self.local_hash, self.remote_hash))
            raise FetchFailedException("Local image missing or wrong after fetch")


class StandardDistroImage(DistroImage):

    """ Ubuntu and Fedora share some of the standards for how they distributed their images """

    def remote_image_url(self):
        url = self.source + "/" + self.prefix + self.image_suffix
        return url.format(server=self.server,
                          release=self.release,
                          arch=self.arch)

    def remote_hashfile_url(self):
        url = self.source + "/" + self.checksums
        return url.format(server=self.server,
                          release=self.release,
                          arch=self.arch)

    def image_hash(self, hashes):
        template = "*" + self.prefix + self.image_suffix
        filename = template.format(release=self.release, arch=self.arch)
        return hashes.get(filename, None)

__all__ = [DistroImage, StandardDistroImage]
