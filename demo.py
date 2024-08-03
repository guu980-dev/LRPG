import gradio as gr

# 1. Main & World Selection
# 2. Character Creation
# 3. Game Play


def main():
    with gr.Blocks() as demo:
        gr.Markdown("## LRPG")
        world = gr.State()
        
        with gr.Tab("World Selection"):
            world_choices = gr.Radio(["Harry Potter", "Custom"], label="World", info="Select a world to play in.")
            gr.Button("Next")
            
            @gr.render(inputs=[world_choices], triggers=["select"])
            def on_world_choices(choice, world):
                if world == "Harry Potter":
                    
                elif world == "Custom":
                    pass
            world_choices.select()
            pass
        with gr.Tab("Character Creation"):
            pass
        with gr.Tab("Game Play"):
            pass
        
        
        
        page = gr.State()
        
        turn = gr.Textbox("X", interactive=False, label="Turn")
        board = gr.Dataframe(value=[["", "", ""]] * 3, interactive=False, type="array")

        def place(board: list[list[int]], turn, evt: gr.SelectData):  # type: ignore
            if evt.value:
                return board, turn
            board[evt.index[0]][evt.index[1]] = turn
            turn = "O" if turn == "X" else "X"
            return board, turn

        board.select(place, [board, turn], [board, turn], show_progress="hidden")

    demo.launch()


if __name__ == "__main__":
    main()