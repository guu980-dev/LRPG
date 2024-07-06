import gradio as gr
import random

# Initial title and description
initial_title = "당신의 선택은? "
initial_description = "<div style='display: flex; justify-content: center; align-items: center; height: auto;'><img src='https://i.ytimg.com/vi/Reo3MnaVb5M/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLD6ZP2I8d1yVXB9Aet0fv1qCeZmNQ' alt='annotated'></div>"


def scenario():
    answer = random.randint(1, 100)
    return answer


def select_option(option, var1):
    var1 = [4, 5, 6]  # Update var1
    var2 = scenario()
    return var2, "https://dummyimage.com/300/09f.png", gr.update(choices=var1), var1


# Define initial state
var1 = [1, 2, 3]

with gr.Blocks() as demo:
    var1_state = gr.State(var1)


    def update_radio(var1):
        return gr.update(choices=var1)


    gr.Markdown(f"### {initial_title}")
    gr.HTML(initial_description)

    with gr.Row():
        with gr.Column():
            radio_input = gr.Radio(var1, label="Options")
            submit_button = gr.Button("Submit")
        with gr.Column():
            output_text = gr.Textbox(label="Generated number")
            output_image = gr.Image(label="Generated image")

    submit_button.click(fn=select_option, inputs=[radio_input, var1_state],
                        outputs=[output_text, output_image, radio_input, var1_state])

    submit_button.click(fn=update_radio, inputs=[var1_state],
                        outputs=[radio_input])

demo.launch()
