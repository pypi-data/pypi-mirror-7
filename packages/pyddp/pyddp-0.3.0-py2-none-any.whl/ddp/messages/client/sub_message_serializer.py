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

from .client_message_serializer import ClientMessageSerializer
from .constants import MSG_SUB

__all__ = ['SubMessageSerializer']


class SubMessageSerializer(ClientMessageSerializer):
    MESSAGE_TYPE = MSG_SUB

    def serialize_fields(self, message):
        fields = {'id': message.id, 'name': message.name}
        if message.has_params():
            fields['params'] = message.params
        return fields

