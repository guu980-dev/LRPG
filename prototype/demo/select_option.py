import gradio as gr
import random

# Initial title and description
initial_title = "당신의 헤리포터 입니다. "
initial_description = "<div style='display: flex; justify-content: center; align-items: center; height: auto;'><img src='https://img1.daumcdn.net/thumb/R1280x0.fjpg/?fname=http://t1.daumcdn.net/brunch/service/user/9YNi/image/AXr3ysfuWGTglNOgTbghg80Fr6o.jfif' alt='annotated'></div>"


# 통신해서 결과값을 가져오기.
def scenario():
    answer = random.randint(1, 100)
    return "호그와트 성은 어둠의 군대와 호그와트의 수호자들 사이의 전장입니다. 볼드모트는 죽음을 먹는 자들과 함께 호그와트를 공격하고, 해리 포터와 그의 친구들, 그리고 호그와트를 지키려는 이들은 이에 맞섭니다. 볼드모트가 죽고, 그의 군대는 패배합니다. 해리는 모든 호크룩스를 파괴함으로써 볼드모트를 영원히 물리치게 됩니다. 마법 세계는 다시 평화를 되찾고, 호그와트는 복구됩니다. 해리와 그의 친구들은 자신들의 삶을 다시 찾으며 미래를 향해 나아갑니다. "


def select_option(option, var1):
    var1 = ["해그리드를 따라 호그와트로 가기로 한 선택", "세베루스 스네이프를 믿기로 한 선택", "볼드모트에게 자발적으로 맞서기로 한 선택"]  # Update var1
    var2 = scenario()
    return var2, "https://res.heraldm.com/content/image/2011/07/14/20110714000370_0.jpg", gr.update(choices=var1), var1


# Define initial state
var1 = ["마술 지팡이를 사용하고 싶나오?", "주문으로만 하나요?", "초능력을 사용합니까?"]

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
