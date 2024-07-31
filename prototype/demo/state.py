import gradio as gr

def store_message(message: str, history: list[str]):
    output = {
        "Current messages": message,
        "Previous messages": history[::-1]
    }
    history.append(message)
    return output, history

demo = gr.Interface(fn=store_message,
                    inputs=["textbox", gr.State(value=[])],
                    outputs=["json", gr.State()])

demo.launch()