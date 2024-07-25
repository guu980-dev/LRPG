import pandas as pd
import numpy as np
import torch
import transformers
import bitsandbytes as bnb
import os
import wandb

from transformers import PreTrainedTokenizerFast, AdamW, AutoModelForCausalLM, BitsAndBytesConfig
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model
from tqdm import tqdm

# 데이터 로드
data = pd.read_csv('train.csv')
tokenizer = PreTrainedTokenizerFast.from_pretrained('LDCC/LDCC-SOLAR-10.7B',  eos_token='</s>')

max_length = 128

formatted_data = []
for _, row in tqdm(data.iterrows()):
  for q_col in ['질문_1', '질문_2']:
    for a_col in ['답변_1', '답변_2', '답변_3', '답변_4', '답변_5']:
      input_text = row[q_col] + tokenizer.eos_token + row[a_col]
      input_ids = tokenizer.encode(input_text, return_tensors='pt', padding='max_length', truncation=True, max_length=max_length)
      formatted_data.append(input_ids)
print('Done.')

formatted_data = torch.cat(formatted_data, dim=0)