import copy
import re

BOARD_EMPTY = '.'
BOARD_EDGE = '+'
BOARD_BLACK = 'X'
BOARD_WHITE = 'O'


class Board(object):
    def __init__(self):
        self.parent = None

    def play(self, x, y, color):

        if x == -1 and y == -1:
            child = self.copy()
            child.parent = self
            return child, 0

        other = color == BOARD_BLACK and BOARD_WHITE or BOARD_BLACK

        x += 1; y += 1;
        h = self.height + 2
        pos = x * (self.height + 2) + y

        if self.goban[pos] != BOARD_EMPTY:
            return None, 0

        child = self.copy()
        child.parent = self

        child.goban[pos] = color

        killed = 0
        for tonari in (pos + h, pos - h, pos + 1, pos - 1):
            elem = child.goban[tonari]
            if elem == other and not child.has_libs(tonari, other, color):
                killed += child.kill(tonari, other, color)

        if not killed and not child.has_libs(pos, color, other):
            return None, 0

        ancestor = self
        while ancestor is not None:
            if child.goban == ancestor.goban:
                return None, -1
            ancestor = ancestor.parent

        return child, killed

    def has_libs(self, pos, color, other):
        h = self.height + 2
        goban = self.goban
        marks = [0] * len(goban)
        def _recur(pos):
            if goban[pos] == BOARD_EMPTY:
                return True
            if marks[pos] or goban[pos] != color:
                return False
            marks[pos] = 1
            return (
                _recur(pos + h) or
                _recur(pos - h) or
                _recur(pos + 1) or
                _recur(pos - 1)
            )
        return _recur(pos)

    def kill(self, pos, color, other):
        h = self.height + 2
        goban = self.goban
        marks = [0] * len(goban)
        def _recur(pos):
            if marks[pos] or goban[pos] != color:
                return 0
            goban[pos] = BOARD_EMPTY
            marks[pos] = 1

            return (
                _recur(pos + h) +
                _recur(pos - h) +
                _recur(pos + 1) +
                _recur(pos - 1) +
                1
            )

        return _recur(pos)

    def get_empty(self):
        h, w = self.height + 2, self.width + 2
        ret = []
        x_list = range(1, self.width + 1)
        y_list = range(1, self.height + 1)
        for x in x_list:
            for y in y_list:
                if self.goban[x * h + y] == BOARD_EMPTY:
                    ret.append((x - 1, y - 1))
        ret.append((-1, -1))
        return ret

    def count(self, color):
        ret = 0
        for elem in self.goban:
            if elem == color:
                ret += 1
        return ret

    def hash(self):
        return ''.join(self.goban)

    def copy(self):
        new_board = Board()
        new_board.height = self.height
        new_board.width = self.width
        new_board.goban = self.goban[:]
        return new_board

    def load(self, pos_string):
        rows = pos_string.strip().split('\n')
        rows = [re.sub('[^\+\-\.\|OX]', '', x) for x in rows]
        self.height = len(rows)
        self.width = len(rows[0])
        h, w = self.height + 2, self.width + 2
        self.goban = [BOARD_EMPTY] * (h * w)
        for x in xrange(self.width):
            for y in xrange(self.height):
                self.goban[(x + 1) * h + y + 1] = {
                    '.': BOARD_EMPTY,
                    '+': BOARD_EDGE,
                    '-': BOARD_EDGE,
                    '|': BOARD_EDGE,
                    'X': BOARD_BLACK,
                    'O': BOARD_WHITE,
                }.get(rows[y][x])

    def __str__(self):
        h, w = self.height + 2, self.width + 2
        ret = ''
        for y in xrange(1, self.height + 1):
            for x in xrange(1, self.width + 1):
                elem = self.goban[x * h + y]
                if elem == BOARD_EMPTY:
                    c = '. '
                elif elem == BOARD_EDGE:
                    c = '+ '
                elif elem == BOARD_BLACK:
                    c = 'X '
                elif elem == BOARD_WHITE:
                    c = 'O '
                else:
                    c = '%2s' % (elem,)
                ret += c
            ret += '\n'
        return ret


if __name__ == '__main__':
    b = Board()
    b.load(open('data/001_goban.txt', 'r').read())
    print b
    c = b.play(2, 1, BOARD_BLACK)
    print c
