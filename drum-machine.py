import pygame
from pygame import mixer
pygame.init()

WIDTH = 1400
HEIGHT = 800

black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
dark_gray = (50, 50, 50)
green = (0, 255, 0)
gold = (212, 175, 55)
blue = (0, 255, 255)

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Drum Machine')
label_font = pygame.font.Font('Pacifico.ttf', 32)
menu_label_font = pygame.font.Font('Roboto-Bold.ttf', 32)
medium_font = pygame.font.Font('Pacifico.ttf', 24)
menu_medium_font = pygame.font.Font('Roboto-Bold.ttf', 24)

fps = 60
timer = pygame.time.Clock()
beats = 8
instruments = 6
boxes = []
clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
active_channels = [1 for _ in range(instruments)]
bpm = 240
playing = True
active_length = 0
active_beat = 0
beat_changed = True
save_menu = False
load_menu = False
saved_beats = []
file = open('saved_beats.txt', 'r')
for line in file:
    saved_beats.append(line)
beat_name = ''
typing = False


# load in sounds
hi_hat = mixer.Sound('sounds\hi hat.WAV')
snare = mixer.Sound('sounds\snare.WAV')
kick = mixer.Sound('sounds\kick.WAV')
crash = mixer.Sound('sounds\crash.WAV')
clap = mixer.Sound('sounds\clap.WAV')
tom = mixer.Sound('sounds\\tom.WAV')

# pygame defaults to 8 channels which could lead to issues later
pygame.mixer.set_num_channels(instruments * 3)


def play_notes():
    for i in range(len(clicked)):
        if clicked[i][active_beat] == 1 and active_channels[i] == 1:
            if i == 0:
                hi_hat.play()
            if i == 1:
                snare.play()
            if i == 2:
                kick.play()
            if i == 3:
                crash.play()
            if i == 4:
                clap.play()
            if i == 5:
                tom.play()


def draw_grid(clicked, beat, active_channels):
    left_box = pygame.draw.rect(screen, gray, [0, 0, 200, HEIGHT - 195], 5)
    bottom_box = pygame.draw.rect(
        screen, gray, [0, HEIGHT - 200, WIDTH, 200], 5)
    boxes = []
    colors = [gray, white, gray]
    hi_hat_text = label_font.render('Hi-Hat', True, colors[active_channels[0]])
    screen.blit(hi_hat_text, (30, 30))
    snare_text = label_font.render('Snare', True, colors[active_channels[1]])
    screen.blit(snare_text, (30, 130))
    kick_text = label_font.render('Bass Drum', True, colors[active_channels[2]])
    screen.blit(kick_text, (30, 230))
    crash_text = label_font.render('Crash', True, colors[active_channels[3]])
    screen.blit(crash_text, (30, 330))
    clap_text = label_font.render('Clap', True, colors[active_channels[4]])
    screen.blit(clap_text, (30, 430))
    floor_tom_text = label_font.render('Floor Tom', True, colors[active_channels[5]])
    screen.blit(floor_tom_text, (30, 530))

    for i in range(1, instruments):
        pygame.draw.line(screen, gray, (0, i * 100), (195, i * 100), 3)

    for i in range(beats):
        for j in range(instruments):
            if clicked[j][i] == -1:
                color = gray
            else:
                if active_channels[j] == 1:
                    color = green
                else:
                    color = dark_gray
            # drum pad buttons
            rect = pygame.draw.rect(
                screen,
                color,
                [i * ((WIDTH - 200) // beats) + 205, (j * 100) + 5,
                    ((WIDTH - 200) // beats) - 10, ((HEIGHT - 200) // instruments) - 10],
                0,
                3
            )
            # drum pad button inner highlight
            pygame.draw.rect(
                screen,
                gold,
                [i * ((WIDTH - 200) // beats) + 200, (j * 100),
                    ((WIDTH - 200) // beats), ((HEIGHT - 200) // instruments)],
                5,
                5
            )
            # grid liens between buttons
            pygame.draw.rect(
                screen,
                black,
                [i * ((WIDTH - 200) // beats) + 200, (j * 100),
                    ((WIDTH - 200) // beats), ((HEIGHT - 200) // instruments)],
                2,
                5
            )
            boxes.append((rect, (i, j)))
        # moving rectangle highlighting active beat
    active = pygame.draw.rect(
        screen,
        blue,
        [beat * ((WIDTH-200)//beats) + 200, 0,
         ((WIDTH-200)//beats), instruments*100],
        5,
        3
    )
    return boxes

def draw_save_menu(beat_name, typing):
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = menu_label_font.render('SAVE MENU: Enter a name for current beat', True, white)
    screen.blit(menu_text, (400, 40))
    if typing:
        pygame.draw.rect(screen, dark_gray, [400, 200, 600, 200], 0, 5)
    entry_rect = pygame.draw.rect(screen, gray, [400, 200, 600, 200], 5, 5)
    entry_txt = menu_label_font.render(f'{beat_name}', True, white)
    screen.blit(entry_txt, (430, 250))
    menu_save_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 200, HEIGHT * 0.75, 400, 100], 0, 5)
    menu_save_txt = menu_label_font.render('Save Beat', True, white)
    screen.blit(menu_save_txt, (WIDTH // 2 - 72, HEIGHT * 0.75 + 30))
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH-200, HEIGHT-100, 180, 90], 0, 5)
    exit_txt = label_font.render('Close', True, white)
    screen.blit(exit_txt, (WIDTH-160, HEIGHT-85))
    return exit_btn, menu_save_btn, entry_rect

def draw_load_menu():
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = menu_label_font.render('LOAD MENU: Select a beat', True, white)
    screen.blit(menu_text, (510, 40))
    menu_load_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 200, HEIGHT * .87, 400, 100], 0, 5)
    menu_load_txt = menu_label_font.render('Load Beat', True, white)
    screen.blit(menu_load_txt, (WIDTH // 2 - 72, HEIGHT * 0.87 + 30))
    menu_delete_btn = pygame.draw.rect(screen ,gray, [(WIDTH//2) - 500, HEIGHT * .87, 200, 100], 0, 5)
    menu_delete_txt = menu_label_font.render('Delete Beat', True, white)
    screen.blit(menu_delete_txt, (WIDTH // 2 - 485, HEIGHT * .87 + 30))
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH-200, HEIGHT-100, 180, 90], 0, 5)
    exit_txt = label_font.render('Close', True, white)
    screen.blit(exit_txt, (WIDTH-160, HEIGHT-85))
    loaded_rectangle = pygame.draw.rect(screen, gray, [190, 90, 1000, 600], 5, 5)
    for beat in range(len(saved_beats)):
        if beat < 10:
            beat_clicked = []
            row_text = medium_font.render(f'{beat+1}', True, white)
            screen.blit(row_text, (200, 100 + beat * 50))
            name_index_start = saved_beats[beat].index('name: ') + 6
            name_index_end = saved_beats[beat].index(', beats:')
            name_text = medium_font.render(saved_beats[beat][name_index_start:name_index_end], True, white)
            screen.blit(name_text, (240, 100 + beat*50))
        if 0 <= index < len(saved_beats)
    return exit_btn, menu_load_btn, menu_delete_btn, loaded_rectangle

# game loop
run = True
while run:
    timer.tick(fps)
    screen.fill(black)

    boxes = draw_grid(clicked, active_beat, active_channels)

    # lower menu buttons (should i put near draw_grid?)
    play_pause = pygame.draw.rect(
        screen, gray, [50, HEIGHT - 150, 200, 100], 0, 5)
    play_text = label_font.render('Play/Pause', True, white)
    screen.blit(play_text, (70, HEIGHT - 150))
    if playing:
        play_text2 = medium_font.render('Playing', True, dark_gray)
    else:
        play_text2 = medium_font.render('Paused', True, dark_gray)
    screen.blit(play_text2, (70, HEIGHT - 100))

    # drawing 'bpm stuff'
    bpm_rect = pygame.draw.rect(
        screen,
        gray,
        [300, HEIGHT - 150, 200, 100],
        5,
        5
    )
    bpm_text = medium_font.render('Beats Per Minute', True, white)
    screen.blit(bpm_text, (308, HEIGHT - 145))
    bpm_text2 = label_font.render(f'{bpm}', True, white)
    screen.blit(bpm_text2, (370, HEIGHT - 115))
    bpm_add_rect = pygame.draw.rect(
        screen,
        gray,
        [510, HEIGHT - 150, 48, 48],
        0,
        5
    )
    bpm_sub_rect = pygame.draw.rect(
        screen,
        gray,
        [510, HEIGHT - 98, 48, 48],
        0,
        5
    )
    bpm_add_text = medium_font.render('+5', True, white)
    bpm_sub_text = medium_font.render('-5', True, white)
    screen.blit(bpm_add_text, (520, HEIGHT - 152))
    screen.blit(bpm_sub_text, (524, HEIGHT - 102))

    # drawing 'beats stuff'
    beats_rect = pygame.draw.rect(
        screen,
        gray,
        [600, HEIGHT - 150, 200, 100],
        5,
        5
    )
    beats_text = medium_font.render('Beats In Loop', True, white)
    screen.blit(beats_text, (625, HEIGHT - 145))
    beats_text2 = label_font.render(f'{beats}', True, white)
    screen.blit(beats_text2, (670, HEIGHT - 115))
    beats_add_rect = pygame.draw.rect(
        screen,
        gray,
        [810, HEIGHT - 150, 48, 48],
        0,
        5
    )
    beats_sub_rect = pygame.draw.rect(
        screen,
        gray,
        [810, HEIGHT - 98, 48, 48],
        0,
        5
    )
    beats_add_text = medium_font.render('+1', True, white)
    beats_sub_text = medium_font.render('-1', True, white)
    screen.blit(beats_add_text, (820, HEIGHT - 152))
    screen.blit(beats_sub_text, (824, HEIGHT - 102))

    # instrument rects
    instrument_rects = []
    for i in range(instruments):
        rect = pygame.rect.Rect((0, i * 100), (200, 100))
        instrument_rects.append(rect)

    # save and load rects
    save_button = pygame.draw.rect(screen, gray, [900, HEIGHT - 150, 200, 48], 0, 5)
    save_text = label_font.render('Save Beat', True, white)
    screen.blit(save_text, (920, HEIGHT - 155))
    load_button = pygame.draw.rect(screen, gray, [900, HEIGHT - 98, 200, 48], 0, 5)
    load_text = label_font.render('Load Beat', True, white)
    screen.blit(load_text, (920, HEIGHT - 110))

    # clear board rect
    clear_button = pygame.draw.rect(screen, gray, [1150, HEIGHT - 150, 200, 100], 0, 5)
    clear_text = label_font.render('Clear Board', True, white)
    screen.blit(clear_text, (1160, HEIGHT - 130))

    if save_menu:
        menu_exit_button, menu_save_button, entry_rectangle = draw_save_menu(beat_name, typing)
    if load_menu:
        menu_exit_button, menu_load_button, menu_delete_button, loaded_rect = draw_load_menu()

    if beat_changed:
        play_notes()
        beat_changed = False

    # user-action events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not save_menu and not load_menu:
            for i in range(len(boxes)):
                if boxes[i][0].collidepoint(event.pos):
                    coords = boxes[i][1]
                    clicked[coords[1]][coords[0]] *= -1
        if event.type == pygame.MOUSEBUTTONUP and not save_menu and not load_menu:
            if play_pause.collidepoint(event.pos):
                if playing:
                    playing = False
                elif not playing:
                    playing = True
            elif bpm_add_rect.collidepoint(event.pos):
                bpm += 5
            elif bpm_sub_rect.collidepoint(event.pos):
                bpm -= 5
            elif beats_add_rect.collidepoint(event.pos):
                beats += 1
                for i in range(len(clicked)):
                    clicked[i].append(-1)
            elif beats_sub_rect.collidepoint(event.pos):
                beats -= 1
                for i in range(len(clicked)):
                    clicked[i].pop(-1)
            elif clear_button.collidepoint(event.pos):
                clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
            elif save_button.collidepoint(event.pos):
                save_menu = True
            elif load_button.collidepoint(event.pos):
                load_menu = True
            for i in range(len(instrument_rects)):
                if instrument_rects[i].collidepoint(event.pos):
                    active_channels[i] *= -1
        elif event.type == pygame.MOUSEBUTTONUP:
            if menu_exit_button.collidepoint(event.pos):
                save_menu = False
                load_menu = False
                playing = True
                beat_name = ''
                typing = False
            elif entry_rectangle.collidepoint(event.pos):
                if typing:
                    typing = False
                elif not typing:
                    typing = True
            elif menu_save_button.collidepoint(event.pos):
                file = open('saved_beats.txt', 'w')
                saved_beats.append(f'\nname: {beat_name}, beats: {beats}, bpm: {bpm}, selected: {clicked}')
                for i in range(len(saved_beats)):
                    file.write(str(saved_beats[i]))
                file.close()
                save_menu = False
                typing = False
                beat_name = ''
        if event.type == pygame.TEXTINPUT and typing:
            beat_name += event.text
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(beat_name) > 0 and typing:
                beat_name = beat_name[:-1]

    beat_length = 3600 // bpm

    if playing:
        if active_length < beat_length:
            active_length += 1
        else:
            active_length = 0
            if active_beat < beats - 1:
                active_beat += 1
                beat_changed = True
            else:
                active_beat = 0
                beat_changed = True

    pygame.display.flip()
pygame.quit()
