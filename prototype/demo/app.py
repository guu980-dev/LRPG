import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

gr.Number(label='Age', info='In years, must be greater than 0')

demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
    title="세계관을 만들어 보세요. ",
    description="<img src='https://github.com/gradio-app/gradio/blob/main/guides/assets/annotated.png?raw=true' alt='annotated'>",
)



demo.launch()