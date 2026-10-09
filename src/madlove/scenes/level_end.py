"""The bonus count after a level."""

from madlove import audio, config, hud, levels, scores
from madlove import strings as str_r
from madlove.scenes import base, game_over, intro


class FinishedLevelScene(base.Scene):
    def __init__(self, game, game_scene):
        super().__init__(game)
        self.game_scene = game_scene
        self.finished_lvl = game_scene.level_data.no + 1
        self.current_stage = game_scene.current_stage
        self.next_level = self.finished_lvl
        self.fadein_step = 255
        self.fadeout_step = 0
        self.leave = False

        self.finished_lines = str_r.get_str('finished_lines').splitlines()

        self.level_clear = True if len(game_scene.bricks) == 0 else False
        self.no_continue = game_scene.no_continue
        self.bonus_time = int(game_scene.bonus_timer / 1000)
        self.time_bonus = max(self.bonus_time * scores.get_bonus('time_bonus'), 0)
        self.collected_all_pus = game_scene.collected_all_pus
        self.lost_life = game_scene.lost_life
        self.perfect_play = (
            False if False in [not self.lost_life, self.level_clear, self.no_continue, self.collected_all_pus] else True
        )
        self.level_clear_bonus = scores.get_bonus('clear') if self.level_clear else 0
        self.no_continue_bonus = scores.get_bonus('no_continue') if self.no_continue else 0
        self.collected_all_pus_bonus = scores.get_bonus('all_pus') if self.collected_all_pus else 0
        self.perfect_play_bonus = scores.get_bonus('perfect') if self.perfect_play else 0

        self.all_values = [
            self.game.score,
            self.time_bonus,
            self.level_clear_bonus,
            self.no_continue_bonus,
            self.collected_all_pus_bonus,
            self.perfect_play_bonus,
        ]

        self.finished_all_levels = True if self.next_level == levels.get_total_levels() else False

        self.blit_elements = [False] * 6
        self.blit_timer = 0
        self.score_timer = 0

        audio.stop_music()

    def render(self, screen):
        screen.fill(config.BG_COLOR)
        lines = []

        finished_text = self.game.font_16.render(
            str_r.get_str('finished').format(self.finished_lvl), True, config.TEXT_COLOR
        )
        finished_pos = finished_text.get_rect()
        finished_pos.centerx = screen.get_rect().centerx
        finished_pos.centery = screen.get_height() * 0.1
        screen.blit(finished_text, finished_pos)

        for idx, line in enumerate(self.finished_lines):
            new_line = f'{line:<12} {self.all_values[idx]:>13}'
            text_surf = self.game.font_16.render(new_line, True, config.TEXT_COLOR)
            text_pos = text_surf.get_rect()
            text_pos.topleft = (34, 150 + (40 * idx))
            lines.append((text_surf, text_pos))

        for idx, blit in enumerate(self.blit_elements):
            if blit:
                screen.blit(lines[idx][0], lines[idx][1])

        # fade screen
        if self.fadein_step > 0:
            self.fadein_step = hud.render_fading(screen, self.fadein_step, 0, self.game.steps)
        if self.fadeout_step > 0:
            self.fadeout_step = hud.render_fading(screen, self.fadeout_step, 1, self.game.steps)

    def update(self):
        self.blit_timer += self.game.dt
        if self.blit_timer >= 100:
            self.blit_timer = 0
            if False in self.blit_elements:
                self.blit_elements.insert(0, True)
                self.blit_elements.remove(False)

        if False not in self.blit_elements:
            self.score_timer += self.game.dt
            if self.score_timer > 500:
                if self.time_bonus > 0:
                    self.time_bonus -= scores.get_bonus('time_bonus')
                    self.game.score += scores.get_bonus('time_bonus')
                    audio.play_sfx('point')

                    if self.time_bonus <= 0:
                        self.time_bonus = 0
                        self.score_timer = 0
                elif self.level_clear_bonus > 0:
                    self.level_clear_bonus -= 1000
                    self.game.score += 1000
                    audio.play_sfx('point')

                    if self.level_clear_bonus <= 0:
                        self.level_clear_bonus = 0
                        self.score_timer = 0
                elif self.no_continue_bonus > 0:
                    self.no_continue_bonus -= 1000
                    self.game.score += 1000
                    audio.play_sfx('point')

                    if self.no_continue_bonus <= 0:
                        self.no_continue_bonus = 0
                        self.score_timer = 0
                elif self.collected_all_pus_bonus > 0:
                    self.collected_all_pus_bonus -= 1000
                    self.game.score += 1000
                    audio.play_sfx('point')

                    if self.collected_all_pus_bonus <= 0:
                        self.collected_all_pus_bonus = 0
                        self.score_timer = 0
                elif self.perfect_play_bonus > 0:
                    self.perfect_play_bonus -= 4000
                    self.game.score += 4000
                    audio.play_sfx('point')

                    if self.perfect_play_bonus <= 0:
                        self.perfect_play_bonus = 0
                        self.score_timer = 0
                elif not self.leave:
                    self.fadeout_step = 255
                    self.leave = True

        self.all_values = [
            self.game.score,
            self.time_bonus,
            self.level_clear_bonus,
            self.no_continue_bonus,
            self.collected_all_pus_bonus,
            self.perfect_play_bonus,
        ]

        if self.leave and self.fadeout_step <= 0:
            if self.finished_all_levels:
                self.manager.go_to(game_over.GameOver(self.game, self.game_scene))
            else:
                self.manager.go_to(intro.IntroScene(self.game, self.next_level))

    def handle_events(self, events):
        pass
