import os
import torch
import transformers
from datasets import load_from_disk
from transformers import (
    BitsAndBytesConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TextStreamer,
    pipeline
)
from peft import (
    LoraConfig,
    prepare_model_for_kbit_training,
    get_peft_model,
    get_peft_model_state_dict,
    set_peft_model_state_dict,
    TaskType,
    PeftModel
)
from trl import SFTTrainer

# BASE_MODEL = "yanolja/EEVE-Korean-10.8B-v1.0"
BASE_MODEL = "upstage/SOLAR-10.7B-Instruct-v1.0"

model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, load_in_4bit=True, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

prompt = "한국의 아이돌 문화에 대해 알려줘."

# 텍스트 생성을 위한 파이프라인 설정
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256) # max_new_tokens: 생성할 최대 토큰 수
outputs = pipe(
    prompt,
    do_sample=True, # 샘플링 전략 사용. 확률 분포를 기반으로 다음 토큰을 선택
    temperature=0.2, # 샘플링의 다양성을 조절하는 파라미터. 값이 높을수록 랜덤성 증가
    top_k=50, # 다음 토큰을 선택할 때 상위 k개의 후보 토큰 중에서 선택. 여기에서는 상위 50개의 후보 토큰 중에서 샘플링
    top_p=0.95, # 누적 확률이 p가 될 때까지 후보 토큰을 포함
    repetition_penalty=1.2, # 반복 패널티를 적용하여 같은 단어나 구절이 반복되는 것 방지
    add_special_tokens=True # 모델이 입력 프롬프트의 시작과 끝을 명확히 인식할 수 있도록 특별 토큰 추가
)
print(outputs[0]["generated_text"][len(prompt):]) # 입력 프롬프트 이후에 생성된 텍스트만 출력