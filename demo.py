import gradio as gr

from create_world.creator_gradio import create_custom_world, create_scenario, create_storyline
from create_world.utils import load_txt

# 1. Main & World Selection
# 2. Character Creation
# 3. Game Play

    # topic, world_summary = create_custom_world(config['create_custom_world_prompt'], language='한국어', save=False)
    # scenario = create_scenario(topic, world_summary, config['create_scenario_prompt'], output_count=1)
    # round_stories = create_storyline(topic, scenario[0], config['create_storyline_prompt'])


def main():
    with gr.Blocks() as demo:
        gr.Markdown("## LRPG")
        game_topic = gr.State()
        world_summary = gr.State()
        stories = gr.State([])
        
        with gr.Tab("게임 세계 생성"):
            theme_choices = gr.Radio(["Harry Potter", "직접 생성"], label="테마 선택", info="게임의 테마를 선택하세요.")
            
            @gr.render(inputs=[theme_choices])
            def on_world_choices(theme):
                if theme == "직접 생성":
                    topic = gr.Textbox("ex)마법사 세계, 우주 전쟁", label="주제", info="세계의 주제를 알려주세요.", interactive=True)
                    world_story = gr.Textbox(label="설명", info="구체적인 세계관 설명과 룰을 소개하세요", interactive=True)
                    world_create_btn = gr.Button("세계관 자동 생성")
                    create_story_btn = gr.Button("스토리 생성", visible=False)
                    result = gr.Markdown("## 스토리 생성이 완료되었습니다. 캐릭터 생성 탭으로 이동해주세요.", visible=False)
                    
                    # @world_create_btn.click(inputs=[ topic, world_story ], outputs=[ game_topic, world_summary, create_story_btn ])
                    def click_world_create_btn(topic, world_story):
                        topic, summary = create_custom_world(topic, world_story)
                        return { game_topic: topic, world_summary: summary, create_story_btn: gr.Button(visible=True) }
                    world_create_btn.click(fn=click_world_create_btn, inputs=[ topic, world_story ], outputs=[ game_topic, world_summary, create_story_btn ])

                    # @create_story_btn.click(inputs=[ game_topic, world_summary ], outputs= [ stories, result ])
                    def click_create_story_btn(topic, summary):
                        scenario = create_scenario(topic, summary, output_count=1, save=False)
                        _stories = create_storyline(topic, scenario[0], save=False)
                        return { stories: _stories, result: gr.Markdown(visible=True) }
                    create_story_btn.click(fn=click_create_story_btn, inputs=[ game_topic, world_summary ], outputs= [ stories, result ])

                elif theme == "Harry Potter":
                    create_story_btn = gr.Button("스토리 생성")
                    result = gr.Markdown("## 스토리 생성이 완료되었습니다. 캐릭터 생성 탭으로 이동해주세요.", visible=False)
                    def click_create_story_btn():
                        topic = "Harry Potter"
                        _world_summary = load_txt("harrypotter_scenario/world_summary.txt")
                        scenario = create_scenario(topic, _world_summary, output_count=1, save=False)
                        _stories = create_storyline(topic, scenario[0], save=False)
                        return { game_topic: topic, world_summary: _world_summary, stories: _stories, result: gr.Markdown(visible=True) }
                    create_story_btn.click(fn=click_create_story_btn, outputs=[ game_topic, world_summary, stories, result ])

        with gr.Tab("캐릭터 생성"):
            gr.Markdown("캐릭터 생성 탭입니다.")
            @gr.render(inputs=[game_topic])
            def on_game_topic(topic):
                return gr.Markdown(f"게임 주제: {topic}")

        with gr.Tab("게임 플레이"):
            gr.Markdown("게임 플레이 탭입니다.")
            
            
        # For Debugging
        game_topic_debugging = gr.Textbox(game_topic.value, label="game_topic_debugging")
        game_topic.change(lambda x: gr.Textbox(x), inputs=[game_topic], outputs=game_topic_debugging)
        world_summary_debugging=gr.Textbox(world_summary.value, label="world_summary_debugging")
        world_summary.change(lambda x: gr.Textbox(x), inputs=[world_summary], outputs=world_summary_debugging)
        stories_debugging=gr.Textbox(stories.value, label="stories_debugging")
        stories.change(lambda x: gr.Textbox(x), inputs=[stories], outputs=world_summary_debugging)


    demo.launch(share=True)


if __name__ == "__main__":
    main()