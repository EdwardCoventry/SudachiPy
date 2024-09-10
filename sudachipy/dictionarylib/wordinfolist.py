# Copyright (c) 2019 Works Applications Co., Ltd.
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

import struct

from .wordinfo import WordInfo

CUSTOM_OFFSET = 10 ** 8


class WordInfoList(object):
    def __init__(self, bytes_, offset, word_size, has_synonym_gid):
        self.bytes = bytes_
        self.offset = offset
        self._word_size = word_size
        self.has_synonym_gid = has_synonym_gid

    def get_word_info(self, word_id, lex_id, lexes, _offset=None):
        orig_pos = self.bytes.tell()
        index = self.word_id_to_offset(word_id, _offset)
        self.bytes.seek(index)
        try:
            surface = self.buffer_to_string()
        except UnicodeDecodeError as e:
            raise e
        head_word_length = self.buffer_to_string_length()
        pos_id = int.from_bytes(self.bytes.read(2), 'little')
        normalized_form = self.buffer_to_string()
        if not normalized_form:
            normalized_form = surface
        dictionary_form_word_id = int.from_bytes(self.bytes.read(4), 'little', signed=True)
        reading_form = self.buffer_to_string()
        if not reading_form:
            reading_form = surface
        a_unit_split = self.buffer_to_int_array()
        b_unit_split = self.buffer_to_int_array()
        word_structure = self.buffer_to_int_array()

        # edits
        self.word_id_int = word_id
        self.word_id = word_id

        synonym_gids = []
        if self.has_synonym_gid:
            synonym_gids = self.buffer_to_int_array()

        if dictionary_form_word_id == -1:
            dictionary_form_lex_id = -1
        else:
            dictionary_form_lex_id, dictionary_form_word_id = divmod(dictionary_form_word_id, CUSTOM_OFFSET)

        if dictionary_form_word_id == -1 or (dictionary_form_word_id, dictionary_form_lex_id) == (word_id, lex_id):
            dictionary_form = surface
        else:
            if lexes is None:
                raise ValueError("lexes has not been passed but dictionary_form_lex_id is not -1")
            else:
                # if this function get_word_info is being called from a user dictionary wordinfolist
                # but the dictionary version is from the general user dict
                # then we need a reference to the general user dict
                # in order to get the right token for dictionary_form_word_id
                wi = lexes[dictionary_form_lex_id].get_word_info(dictionary_form_word_id, dictionary_form_lex_id, lexes)

            dictionary_form = wi.surface

        self.bytes.seek(orig_pos)


        word_id = self.adjust_word_id(lex_id, word_id)
        dictionary_form_word_id = self.adjust_word_id(dictionary_form_lex_id, dictionary_form_word_id)

        word_info = WordInfo(surface, head_word_length, pos_id, normalized_form, dictionary_form_word_id,
                             dictionary_form, reading_form, a_unit_split, b_unit_split, word_structure, synonym_gids,
                             word_id=word_id, lex_id=lex_id, dictionary_form_lex_id=dictionary_form_lex_id)

        return word_info

    def adjust_word_id(self, lex_id, word_id):
        if word_id < CUSTOM_OFFSET * lex_id:
            word_id += CUSTOM_OFFSET * lex_id
        return word_id

    def word_id_to_offset(self, word_id, _offset=None):
        i = self.offset + 4 * word_id
        return int.from_bytes(self.bytes[i:i + 4], 'little', signed=False)

    def buffer_to_string_length(self):
        length = self.bytes.read_byte()
        if length < 128:
            return length
        low = self.bytes.read_byte()
        return ((length & 0x7F) << 8) | low

    def buffer_to_string(self):
        length = self.buffer_to_string_length()
        try:
            return self.bytes.read(2 * length).decode('utf-16-le')
        except UnicodeDecodeError as e:
            raise e

    def buffer_to_int_array(self):
        length = self.bytes.read_byte()
        _bytes = self.bytes.read(4 * length)
        return list(struct.unpack('{}i'.format(length), _bytes))

    def size(self):
        return self._word_size
