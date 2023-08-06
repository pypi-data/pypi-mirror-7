# -*- coding: utf-8 -*-

# Copyright 2014 Foxdog Studios
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .client_message_parser import ClientMessageParser
from .connect_message import ConnectMessage
from .constants import MSG_CONNECT

__all__ = ['ConnectMessageParser']


class ConnectMessageParser(ClientMessageParser):
    MESSAGE_TYPE = MSG_CONNECT

    def parse(self, pod):
        return ConnectMessage(
            pod['version'],
            support=pod.get('support'),
            session=pod.get('session'),
        )

