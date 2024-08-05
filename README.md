---
title: LRPG
app_file: demo_hf_space.py
sdk: gradio
sdk_version: 4.37.2
---
# lRPG (LLM RPG)

This project is demo of TRPG using LLM (Solar) with korean.

### Introduction

You can enjoy your own rpg on your own world. You can make any decision, then llm game master will handle them.

This demo version can be played in gradio. You can choose harry potter (example) or generate your own world.

You can play the demo version on huggingface space (https://huggingface.co/spaces/pizb/LRPG)


## 1. Structure  

Consist of
1. World Preparation
2. Character Preparation
3. Game Play

## 2. Stack

1. Solar
2. Graph db (WIP)

### 3. How to play

1. Clone this repository and install packages
```
pip install -r requirements.txt
```

2. Create .env file with your own api key
(UPSTAGE_API_KEY: required, OPENAI_API_KEY(with credit): only required when you use image generation)

3. Execute demo file

```
python demo.py
```
or
```
gradio demo.py
```