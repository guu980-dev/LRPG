import gradio as gr

from create_world.creator_gradio import create_custom_world, create_scenario, create_storyline

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
        
        with gr.Tab("게임 세계 생성", interactive=False):
            theme_choices = gr.Radio(["Harry Potter", "직접 생성"], label="테마 선택", info="게임의 테마를 선택하세요.")
            
            @gr.render(inputs=[theme_choices])
            def on_world_choices(theme):
                if theme == "직접 생성":
                    topic = gr.Textbox("ex)마법사 세계, 우주 전쟁", label="주제", info="세계의 주제를 알려주세요.", interactive=True)
                    world_story = gr.Textbox(label="설명", info="구체적인 세계관 설명과 룰을 소개하세요", interactive=True)
                    world_create_btn = gr.Button(label="세계관 자동 생성")
                    
                    @world_create_btn.click(input={ topic, world_story }, outputs={ game_topic, world_summary })
                    def click_world_create_btn(user_input):
                        topic, summary = create_custom_world(user_input["topic"], user_input["world_story"])
                        return { game_topic: topic, world_summary: summary }
                    
                create_story_btn = gr.Button(label="스토리 생성")
                @create_story_btn.click(input={ game_topic, world_summary }, outputs={ stories })
                def click_create_story_btn(topic, summary):
                    scenario = create_scenario(topic, world_summary, output_count=1, save=False)
                    gr.js('switchToCharacterCreationTab')
                    return { stories: create_storyline(topic, scenario[0], save=False) }

        with gr.Tab("캐릭터 생성", interactive=False):
            gr.Markdown("캐릭터 생성 탭입니다.")
            gr.Textbox(game_topic, label="game_topic_debugging")
            gr.Textbox(world_summary, label="world_summary_debugging")
            gr.Textbox(stories, label="stories_debugging")
        with gr.Tab("게임 플레이", interactive=False):
            gr.Markdown("게임 플레이 탭입니다.")
        
        # Custom JavaScript to switch tabs
        demo.load("""
            <script>
            function switchToCharacterCreationTab() {
                // Assuming the "캐릭터 생성" tab is the second tab
                document.querySelectorAll('.gradio-tabs div[role="tab"]')[1].click();
            }
            </script>
        """, outputs=None)

    demo.launch(share=True)


if __name__ == "__main__":
    main()