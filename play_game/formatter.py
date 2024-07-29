def to_round_result(round_effect_dict, round_result_explanation):
  # vocab_dictionary = {
  #   "life": "생명 포인트가",
  #   "money": "돈이",
  #   "stamina": "체력이",
  #   "intelligence": "지능이",
  #   "combat_power": "전투력이",
  #   "agility": "민첩성이",
  # }
  
  round_effect_str = ""
  for key, value in round_effect_dict.items():
    if value > 0:
      round_effect_str += f"{key} is increased by {value}. "
    elif value == 0:
      round_effect_str += f"{key} is not changed. "
    else:
      round_effect_str += f"{key} is decreased by {value*(-1)}. "
  
  return round_effect_str + round_result_explanation