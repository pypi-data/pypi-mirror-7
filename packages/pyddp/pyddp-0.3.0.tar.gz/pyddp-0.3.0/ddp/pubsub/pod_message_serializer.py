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
from .topics import PodSend, RawSend

__all__ = ['PodMessageSerializer']


class PodMessageSerializer(Subscriber):
    def __init__(self, board, serializer):
        super(PodMessageSerializer, self).__init__(board,
                {PodSend: self._on_send})
        self._board = board
        self._serializer = serializer

    def _on_send(self, topic, pod):
        self._board.publish(RawSend, self._serializer.serialize(pod))

