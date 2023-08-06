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

from .subscriber import Subscriber
from .topics import PodReceived, RawReceived

__all__ = ['PodMessageParser']


class PodMessageParser(Subscriber):
    def __init__(self, board, parser):
        super(PodMessageParser, self).__init__(board, {
                RawReceived: self._on_received})
        self._board = board
        self._parser = parser

    def _on_received(self, topic, raw):
        self._board.publish(PodReceived, self._parser.parse(raw))

