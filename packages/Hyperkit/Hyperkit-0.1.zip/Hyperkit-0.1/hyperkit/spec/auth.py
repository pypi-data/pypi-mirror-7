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


class Auth(object):
    pass


class PasswordAuth(Auth):
    def __init__(self, username="hyperkit", password="password"):
        self.username = username
        self.password = password

    def __str__(self):
        return "password authentication for username '%s'" % (self.username, )


class SSHAuth(Auth):
    def __init__(self, username, public_key, private_key=None):
        self.username = username
        self.public_key = public_key
        self.private_key = private_key

    def __str__(self):
        return "SSH authentication for username '%s' using public key '%s'" % (self.username, self.public_key, )

__all__ = [Auth, PasswordAuth, SSHAuth]
