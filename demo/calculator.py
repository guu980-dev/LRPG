import gradio as gr
def generate_fake_image(num1, operation, num2):
    if operation == "add":
        return num1 + num2, "https://dummyimage.com/300/09f.png"
    elif operation == "subtract":
        return num1 - num2, "https://dummyimage.com/300/09f.png"
    elif operation == "multiply":
        return num1 * num2, "https://dummyimage.com/300/09f.png"
    elif operation == "divide":
        if num2 == 0:
            raise gr.Error("Cannot divide by zero!")
        return num1 / num2, "https://dummyimage.com/300/09f.png"

def track_score(score):

    return ["1", "2", "3", "4"]

scores = track_score

def generate_fake_image(num1, operation, num2):
    if operation == "add":
        return num1 + num2, "https://dummyimage.com/300/09f.png"
    elif operation == "subtract":
        return num1 - num2, "https://dummyimage.com/300/09f.png"
    elif operation == "multiply":
        return num1 * num2, "https://dummyimage.com/300/09f.png"
    elif operation == "divide":
        if num2 == 0:
            raise gr.Error("Cannot divide by zero!")
        return num1 / num2, "https://dummyimage.com/300/09f.png"

demo = gr.Interface(
    generate_fake_image,
    [
        "number",
        gr.Radio(scores),
        "number"
    ],
    ["textbox", "image"],
    examples=[
        [45, "add", 3],
        [3.14, "divide", 2],
        [144, "multiply", 2.5],
        [0, "subtract", 1.2],
    ],
    title="Toy Calculator",
    description="Here's a sample toy calculator. Allows you to calculate things like $2+2=4$",
)

demo.launch()