import pandas as pd
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Trainer, TrainingArguments, DataCollatorForLanguageModeling
import bitsandbytes as bnb
import os
import wandb
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model

# 모델 로드

# model_id = "LDCC/LDCC-SOLAR-10.7B"
model_id = "upstage/SOLAR-10.7B-Instruct-v1.0"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)
model = AutoModelForCausalLM.from_pretrained(model_id,
                                             quantization_config=bnb_config,
                                            #  device_map={"":0},
                                             device_map="auto",
                                             torch_dtype=torch.float16,
                                             #torch_dtype=orch.float32,
                                             )
tokenizer = AutoTokenizer.from_pretrained(model_id)

model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )


config = LoraConfig(
    r=8, 
    lora_alpha=32, 
    #target_modules=["query_key_value"],
    # target_modules=["self_attention", "ffn"],  # Modules to apply LoRA
    target_modules=[
        "q_proj",
        "up_proj",
        "o_proj",
        "k_proj",
        "down_proj",
        "gate_proj",
        "v_proj"
    ],
    lora_dropout=0.05, 
    bias="none", 
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, config)
print_trainable_parameters(model)

tokenizer.pad_token = tokenizer.eos_token

trainer = Trainer(
    model=model,
    train_dataset=formatted_data,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=1,
        #  max_steps=50,
        learning_rate=1e-4,
        fp16=True,
        logging_steps=10,
        output_dir="outputs",
        optim="paged_adamw_8bit"
    ),
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)
model.config.use_cache = False 
trainer.train()