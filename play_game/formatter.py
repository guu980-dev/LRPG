def to_round_result(round_effect_dict, round_result_explanation):
  vocab_dictionary = {
    "life": "생명력이",
    "money": "돈이",
    "stamina": "체력이",
    "intelligence": "지능이",
    "combat_power": "전투력이",
    "agility": "민첩성이",
  }
  
  round_effect_str = ""
  for status in ['player_restriction', 'player_capability']:
    for key, value in round_effect_dict[status].items():
      if value > 0:
        round_effect_str += f"{vocab_dictionary[key]} {value}만큼 증가했습니다. "
      elif value == 0:
        round_effect_str += f"{vocab_dictionary[key]} 변화하지 않았습니다. "
      else:
        round_effect_str += f"{vocab_dictionary[key]} {value*(-1)}만큼 감소했습니다. "
  
  return round_effect_str + round_result_explanation


def player_profile_to_str(player_profile_dict):
  return '\n' + '\n'.join([f"{key}: {value}" for key, value in player_profile_dict.items()])