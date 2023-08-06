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

from .constants import MSG_ADDED_BEFORE
from .server_message_serializer import ServerMessageSerializer

__all__ = ['AddedBeforeMessageSerializer']


class AddedBeforeMessageSerializer(ServerMessageSerializer):
    MESSAGE_TYPE = MSG_ADDED_BEFORE

    def serialize_fields(self, message):
        fields = {
            'collection': message.collection,
            'id': message.id,
            'before': message.before,
        }
        if message.has_fields():
            fields['fields'] = message.fields
        return fields

