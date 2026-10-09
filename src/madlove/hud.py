"""Drawing helpers shared by the scenes: score display, screen fades, blinking text and centring."""

import functools

import pygame as pg

from madlove import config, utils
from madlove import strings as str_r


def render_fading(screen, fade_step, invert_fading=0):
    # fade screen
    if invert_fading:
        alpha = abs(fade_step - 254)
    else:
        alpha = fade_step
    fading_surf = pg.Surface(screen.get_size(), pg.SRCALPHA)
    fade_color = pg.Color(config.BG_COLOR)  # copy, so the global background color stays opaque
    alpha = 80 * round(alpha / 80)  # fades a bit rougher
    # print('fading {} {}'.format(('out' if invert_fading else 'in'), alpha))
    fade_color.a = alpha
    fading_surf.fill(fade_color)
    screen.blit(fading_surf, (0, 0))
    # decrease fade_step until 0
    fade_step -= 10

    return fade_step


@functools.cache
def pack_image():
    """the cigarette pack next to the lives, loaded the first time the HUD is drawn: it needs the display"""
    return pg.image.load(config.asset('graphics', 'pack.png')).convert()


def render_hud(game, screen, hud_score, stage, lives, timer, highlight_combo=0):
    if timer <= 2000:
        # blink labels at beginning of game
        pass

    if highlight_combo:
        # 1 for black, 2 for white
        if highlight_combo > 1:
            color = (0, 0, 0)
        else:
            color = (255, 255, 255)
        score_text = game.font_16.render(str_r.get_str('combo').format(game.combo.value), True, color)
    else:
        score_text = game.font_16.render(str(hud_score), True, config.TEXT_COLOR)

    stage_text = game.font_16.render(stage, True, config.TEXT_COLOR)
    stage_pos = stage_text.get_rect()
    stage_pos.midtop = (screen.get_width() / 2, 8)
    screen.blit(stage_text, stage_pos)

    lives_text = game.font_16.render(str(lives), True, config.TEXT_COLOR)
    lives__text_pos = lives_text.get_rect()
    lives__text_pos.topright = (screen.get_width() - 28, 8)
    screen.blit(lives_text, lives__text_pos)

    screen.blit(pack_image(), (screen.get_width() - 24, 8))

    score_pos = score_text.get_rect()
    score_pos.topleft = (8, 8)
    screen.blit(score_text, score_pos)


def update_highlight_text(scene):
    if scene.ready_to_play:
        scene.highlight_clock += scene.game.dt
        if scene.highlight_clock >= 100:
            scene.highlight_color = utils.invert_color(scene.highlight_color)
            scene.highlight_clock = 0
    else:
        scene.highlight_clock += scene.game.dt
        if scene.highlight_clock >= 500:
            scene.highlight_clock = 0
            scene.draw_coin_text = not scene.draw_coin_text

    if scene.game.wallet.credit > 0:
        scene.ready_to_play = True
        scene.draw_coin_text = True
        scene.coin_text = str_r.get_str('start') if scene.game.wallet.credit > 0 else str_r.get_str('coin')


def render_coin_text(scene, screen, y_pos=0.7):
    if scene.draw_coin_text:
        insert_coin = scene.game.font_16.render(scene.coin_text, True, scene.highlight_color)
        pos_insert = insert_coin.get_rect()
        pos_insert.center = (screen.get_rect().centerx, screen.get_rect().height * y_pos)
        screen.blit(insert_coin, pos_insert)


def render_credit(scene, screen):
    if not scene.game.settings.free_mode:
        if scene.draw_credit and scene.game.wallet.credit:
            credit = scene.game.font_16.render(
                scene.credit_text.format(scene.game.wallet.credit), True, config.TEXT_COLOR
            )
            pos_credit = credit.get_rect()
            pos_credit.midtop = (screen.get_width() / 2, screen.get_height() * 0.96)
            screen.blit(credit, pos_credit)


def center_to(center_surface, surface):
    """will return the position needed to set surface to the center of center_surface"""
    pos = surface.get_rect()
    pos.center = center_surface.get_rect().center
    return pos


def x_center_to(center_surface, surface):
    """will return the position needed to set surface to the horizontal center of center_surface"""
    pos = surface.get_rect()
    pos.centerx = center_surface.get_rect().centerx
    return pos.x
