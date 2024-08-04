import gradio as gr
import re

from create_world.creator_gradio import create_custom_world, create_scenario, create_storyline
from create_world.utils import load_txt
from create_character.gradio import generate_character_creation_questions, create_character_profile, parse_character_data_to_json
from play_game.main import create_initial_conversation, create_round_description, create_round_result, create_bad_ending, create_good_ending, convert_to_image_prompt, generate_image
from play_game.formatter import player_profile_to_str, to_round_result

# 1. Main & World Selection
# 2. Character Creation
# 3. Game Play

def main():
    with gr.Blocks() as demo:
        gr.Markdown("## LRPG")
        game_topic = gr.State()
        world_summary = gr.State()
        stories = gr.State([])
        player_profile = gr.State()
        
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
                        gr.Info("세계관 생성중입니다...")
                        topic, summary = create_custom_world(topic, world_story)
                        gr.Info("세계관 생성 완료!")
                        return { game_topic: topic, world_summary: summary, create_story_btn: gr.Button(visible=True) }
                    world_create_btn.click(fn=click_world_create_btn, inputs=[ topic, world_story ], outputs=[ game_topic, world_summary, create_story_btn ])

                    # @create_story_btn.click(inputs=[ game_topic, world_summary ], outputs= [ stories, result ])
                    def click_create_story_btn(topic, summary):
                        gr.Info("스토리 생성중입니다...")
                        scenario = create_scenario(topic, summary, output_count=1, save=False)
                        _stories = create_storyline(topic, scenario[0], save=False)
                        gr.Info("스토리 생성 완료!")
                        return { stories: _stories, result: gr.Markdown(visible=True) }
                    create_story_btn.click(fn=click_create_story_btn, inputs=[ game_topic, world_summary ], outputs= [ stories, result ])

                elif theme == "Harry Potter":
                    create_story_btn = gr.Button("스토리 생성")
                    result = gr.Markdown("## 스토리 생성이 완료되었습니다. 캐릭터 생성 탭으로 이동해주세요.", visible=False)
                    def click_create_story_btn():
                        gr.Info("스토리 생성중입니다...")
                        topic = "Harry Potter"
                        _world_summary = load_txt("harrypotter_scenario/world_summary.txt")
                        scenario = create_scenario(topic, _world_summary, output_count=1, save=False)
                        _stories = create_storyline(topic, scenario[0], save=False)
                        gr.Info("스토리 생성 완료!")
                        return { game_topic: topic, world_summary: _world_summary, stories: _stories, result: gr.Markdown(visible=True) }
                    create_story_btn.click(fn=click_create_story_btn, outputs=[ game_topic, world_summary, stories, result ])

        with gr.Tab("캐릭터 생성"):
            @gr.render(inputs=[world_summary])
            def on_game_topic(summary):
                questions = generate_character_creation_questions(summary)
                answers = []
                for question_idx, question in enumerate(questions):
                    answer = gr.Textbox(key=question_idx, label=question, placeholder="당신의 대답을 입력하세요.", interactive=True)
                    answers.append(answer)
                char_create_btn = gr.Button("캐릭터 생성")
                result = gr.Markdown("## 캐릭터 생성이 완료되었습니다. 게임 진행 탭으로 이동해주세요.", visible=False)

                def click_char_create_btn(*_answers):
                    gr.Info("캐릭터 생성중입니다...")
                    character_profile = parse_character_data_to_json(create_character_profile(questions, _answers))
                    profile_keys = [key for key in character_profile.keys()]
                    required_keys = ["name", "gender", "age", "race", "job", "background"]
                    params_keys = [key for key in character_profile["params"].keys()]
                    required_params_keys = ["stamina", "intelligence", "combat_power", "agility"]
                    if not all(item in profile_keys for item in required_keys) or not all(item in params_keys for item in required_params_keys):
                        gr.Error("캐릭터 생성에 실패했습니다. 항목들을 자세하게 빠짐없이 기입해주세요.")
                        return
                    gr.Info("캐릭터 생성 완료!")
                    return { player_profile: character_profile, result: gr.Markdown(visible=True) }
                char_create_btn.click(fn=click_char_create_btn, inputs=answers, outputs=[player_profile, result])
                

        with gr.Tab("게임 플레이"):
            round = gr.State(0)
            player_restriction = gr.State()
            player_capability = gr.State()
            previous_conversation = gr.State("")
            previous_round_result = gr.State("")

            @gr.render(inputs=[world_summary, stories, player_profile, round, player_restriction, player_capability, previous_conversation, previous_round_result, game_topic], triggers=[round.change, player_profile.change])
            def on_round(_world_summary, _stories, _player_profile, _round, _player_restriction, _player_capability, _previous_conversation, _previous_round_result, _game_topic):
                entire_story = [f"{idx+1}. {scenario['title']}\n{scenario['story']}\n\n" for idx, scenario in enumerate(_stories)]
                player_profile_str = player_profile_to_str({ **_player_profile, 'params': _player_capability })

                round_scenario = _stories[_round-1]
                if _round == 0:
                    introduction = gr.Markdown(create_initial_conversation(_world_summary, player_profile_str, _player_restriction, _player_capability, entire_story))
                    game_start_btn = gr.Button("게임 시작")
                    
                    def click_game_start_btn():
                        return { round: 1, player_restriction: { "life": 20, "money": 20 }, player_capability: _player_profile["params"] }
                    game_start_btn.click(fn=click_game_start_btn, outputs=[round, player_restriction, player_capability])
                else:
                    round_story = f"{_round}. {round_scenario['title']}: {round_scenario['story']}\n"
                    if _player_restriction["life"] <= 0 or _player_restriction["money"] <= 0:
                        gr.Markdown("## 아쉽게도 게임 오버되었습니다. 다른 선택을 통해 새로운 이야기의 결말을 만들어보세요.")
                        bad_ending = create_bad_ending(_world_summary, player_profile_str, _player_restriction, _player_capability, entire_story, round_story, _previous_conversation, _previous_round_result)
                        display_bad_ending = gr.Markdown(bad_ending)
                        restart_button = gr.Button("다시 시작하기")
                        def click_restart_button():
                            return { round: 0, player_restriction: {}, player_capability: {}, previous_conversation: "", previous_round_result: "" }
                        restart_button.click(fn=click_restart_button, outputs=[round, player_restriction, player_capability, previous_conversation, previous_round_result])
                    
                    elif _round > len(_stories):
                        gr.Markdown("## 축하합니다! 게임 클리어에 성공하셨습니다")
                        good_ending = create_good_ending(_world_summary, player_profile_str, _player_restriction, _player_capability, entire_story, _previous_conversation)
                        display_good_ending = gr.Markdown(good_ending)
                        restart_button = gr.Button("다시 시작하기")
                        def click_restart_button():
                            return { round: 0, player_restriction: {}, player_capability: {}, previous_conversation: "", previous_round_result: "" }
                        restart_button.click(fn=click_restart_button, outputs=[round, player_restriction, player_capability, previous_conversation, previous_round_result])

                    else:
                        round_description = create_round_description(_world_summary, player_profile_str, _player_restriction, _player_capability, entire_story, round_story, _previous_conversation, _previous_round_result)
                        gr.Markdown(f"## {_round}. {round_scenario['title']}")
                        with gr.Row():
                            gr.Markdown(round_description)
                            with gr.Column():
                                image_output = gr.Image(interactive=False, scale=5)
                                generate_image_btn = gr.Button("이미지 생성")
                                def click_generate_image_btn():
                                    gr.Info("이미지 생성중입니다...")
                                    image_generation_prompt = convert_to_image_prompt(_game_topic, _world_summary, _player_profile, round_description)
                                    image_url = generate_image(image_generation_prompt)
                                    gr.Info("이미지 생성 완료!")
                                    return gr.Image(image_url)
                                generate_image_btn.click(fn=click_generate_image_btn, outputs=image_output)
                                
                        with gr.Row():
                            player_response = gr.Textbox(label="당신만의 결정을 내려주세요!", info="하나의 문장으로 당신이 할 행동과 그에 대한 근거와 이유를 명확하게 설명해주세요", interactive=True, scale=10)
                            submit_btn = gr.Button("결정", scale=1)

                        def click_submit_btn(_player_response, _previous_conversation, _player_restriction, _player_capability):
                            gr.Info("결정을 반영중입니다...")
                            __round = _round
                            _round_description = round_description

                            # Reflect the result and update player status
                            round_result = create_round_result(_world_summary, player_profile_str, _player_restriction, _player_capability, _round_description, _player_response)
                            round_effect = round_result["effect"]
                            round_result_explanation = round_result["reason"]  
                            for key, value in round_effect["player_restriction"].items():
                                if _player_restriction.get(key) is not None:
                                    modified_value = _player_restriction[key] + value
                                    if modified_value > 10:
                                        _player_restriction[key] = 10
                                    elif modified_value < -10:
                                        _player_restriction[key] = -10
                                    else:
                                        _player_restriction[key] = modified_value

                            for key, value in round_effect["player_capability"].items():
                                if _player_capability.get(key) is not None:
                                    modified_value = _player_capability[key] + value
                                    if modified_value > 100:
                                        _player_capability[key] = 100
                                    elif modified_value < -100:
                                        _player_capability[key] = -100
                                    else:
                                        _player_capability[key] = modified_value

                            return {
                                round: __round+1,
                                previous_conversation: _previous_conversation + f"Game Master: {_round_description}\nPlayer: {_player_response}\n",
                                previous_round_result: to_round_result(round_effect, round_result_explanation),
                                player_restriction: _player_restriction,
                                player_capability: _player_capability,
                            }
                        submit_btn.click(
                            fn=click_submit_btn,
                            inputs=[ player_response, previous_conversation, player_restriction, player_capability ],
                            outputs=[round, previous_conversation, previous_round_result, player_restriction, player_capability]
                        )

                        player_name = re.sub(r'"', '', _player_profile['name'])
                        player_status_display = gr.Markdown(f"## {player_name}님의 상태")
                        with gr.Group():
                            with gr.Row():
                                gr.Textbox(_player_restriction['life'], interactive=False, label="목숨")
                                gr.Textbox(_player_restriction['money'], interactive=False, label="소지금")
                            with gr.Row():
                                gr.Textbox(_player_capability["stamina"], interactive=False, label="스태미너")
                                gr.Textbox(_player_capability["intelligence"], interactive=False, label="지능")
                                gr.Textbox(_player_capability["combat_power"], interactive=False, label="전투력")
                                gr.Textbox(_player_capability["agility"], interactive=False, label="민첩성")


        # # For Debugging
        # game_topic_debugging = gr.Textbox(game_topic.value, label="game_topic_debugging")
        # game_topic.change(lambda x: gr.Textbox(x), inputs=[game_topic], outputs=game_topic_debugging)
        # world_summary_debugging=gr.Textbox(world_summary.value, label="world_summary_debugging")
        # world_summary.change(lambda x: gr.Textbox(x), inputs=[world_summary], outputs=world_summary_debugging)
        # stories_debugging=gr.Textbox(stories.value, label="stories_debugging")
        # stories.change(lambda x: gr.Textbox(x), inputs=[stories], outputs=stories_debugging)
        # player_profile_debugging=gr.Textbox(player_profile.value, label="player_profile_debugging")
        # player_profile.change(lambda x: gr.Textbox(x), inputs=[player_profile], outputs=player_profile_debugging)


    demo.launch(share=True)


if __name__ == "__main__":
    main()