import re
import conf

def get_ui_line_nums(player_num, handcards_num):
    base_line_num = conf.base_scale_of_view[player_num][0]
    # -1 // 8 == -1 in python
    extra_line_num = max((handcards_num - 1) // 8, 0)
    return base_line_num + extra_line_num

def remove_escape(s):
    return s.replace("\x1b[31m", "") \
            .replace("\x1b[32m", "") \
            .replace("\x1b[33m", "") \
            .replace("\x1b[34m", "") \
            .replace("\x1b[0m", "") 

def can_be_played_after(card_to_play, last_played_card):
    _card_to_play = remove_escape(card_to_play)
    _last_played_card = remove_escape(last_played_card)

    # print("A:", _card_to_play, "\tB,", _last_played_card)
    if _card_to_play == 'W' or _card_to_play == '+4':
        return False
    if _last_played_card[1:] == 'S' or _last_played_card[1:] == '+2' or _last_played_card[1:] == '+4':
        return False
    if _card_to_play[0] == _last_played_card[0]:
        return True
    if len(_last_played_card) > 1 and _card_to_play[1] == _last_played_card[1]:
        return True

def update_handcards(handcards, line):
    cursor_index = -1
    _line = line.split()[1:-1]
    for i in range(len(_line)):
        if _line[i][0] == '>':
            cursor_index = i
            _line[i] = _line[i][1:]
            break

    return handcards + _line, cursor_index

def next_frame(game, player_num):
    cur_line_num = 0
    is_updating_handcards = False
    is_my_turn = False
    stat = 0
    lines_left_num = -1

    # return value
    last_played_card = None
    handcards = []
    cursor_index = -1

    _pos_of_last_played_card = conf.pos_of_last_played_card[player_num]
    _pos_of_my_box = conf.pos_of_player_box[player_num][0]

    while True:
        line = game.stdout.readline().decode("UTF-8").replace("\n", "") 
        line = remove_escape(line)
        print(cur_line_num, "\t", line)

        if cur_line_num == 0 and re.match(".*Want to play again", line):
            stat = 4
            return stat, last_played_card, handcards, cursor_index

        if cur_line_num == _pos_of_last_played_card[0]:
            # last played card
            if len(line[_pos_of_last_played_card[1]:].split()) > 0:
                last_played_card = line[_pos_of_last_played_card[1]:].split()[0].strip()
        
        if cur_line_num == _pos_of_my_box[0] + 3:
            # handcards
            is_updating_handcards = True

        if is_updating_handcards:
            if re.match(".*\+--------", line):
                is_updating_handcards = False
            else:
                handcards, _cursor_index = update_handcards(handcards, line)
                if _cursor_index > -1:
                    cursor_index = _cursor_index

        if cur_line_num == get_ui_line_nums(player_num, len(handcards)) - 1:
            if line[_pos_of_my_box[1]] != '[':
                # it's not my turn
                return False

        if cur_line_num == get_ui_line_nums(player_num, len(handcards)):
            if re.match("Now it's your turn", line):
                lines_left_num = 3
                stat = 1
            elif re.match("Press Enter to play the card just drawn immediately", line):
                lines_left_num = 2
                stat = 2
            elif re.match("Specify the next color", line):
                lines_left_num = 1
                stat = 3
            else:
                assert False
        
        lines_left_num -= 1
        if lines_left_num == 0:
            return stat, last_played_card, handcards, cursor_index

        cur_line_num += 1