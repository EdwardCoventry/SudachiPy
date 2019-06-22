import os
from unittest import mock

from sudachipy.dictionarylib.charactercategory import CharacterCategory
from sudachipy.dictionarylib.grammar import Grammar

mocked_grammar = mock.Mock(spec=Grammar)
mocked_grammar.get_part_of_speech_size.return_value = 0
mocked_grammar.get_part_of_speech_string.return_value = None
mocked_grammar.get_part_of_speech_id.return_value = 0
mocked_grammar.get_connect_cost.return_value = 0
# mocked_grammar.set_connect_cost.return_value = None
mocked_grammar.get_bos_parameter.return_value = None
mocked_grammar.get_eos_parameter.return_value = None


def mocked_get_character_category():
    cat = CharacterCategory()
    test_resources_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.pardir,
        'resources')
    try:
        cat.read_character_definition(os.path.join(test_resources_dir, 'char.def'))
    except IOError as e:
        print(e)
    return cat


mocked_grammar.get_character_category.side_effect = mocked_get_character_category


mocked_grammar.set_character_category.return_value = None