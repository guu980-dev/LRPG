import gradio as gr
import random

var1 = [1, 2, 3]
def track_score(var1):
    return var1

def scenario():
    answer = random.randint(1, 100)
    return answer

var2 = scenario()

def select_option(option):
    return var2, "https://dummyimage.com/300/09f.png"

scores = track_score(var1)

demo = gr.Interface(
    fn=select_option,
    inputs=gr.Radio(scores),
    outputs=["text", "image"],
    title="당신의 선택은? ",
    description="<div style='display: flex; justify-content: center; align-items: center; height: auto;'><img src='https://i.ytimg.com/vi/Reo3MnaVb5M/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLD6ZP2I8d1yVXB9Aet0fv1qCeZmNQ' alt='annotated'></div>",
)

demo.launch()
