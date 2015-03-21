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
        w, h = self.width + 2, self.height + 2
        if self.goban[x * h + y] != BOARD_EMPTY:
            return None, 0

        child = self.copy()
        child.parent = self

        child.goban[x * h + y] = color

        def _has_libs(goban, x, y, color, other):
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
            return _recur(x * h + y)

        def _kill(goban, x, y, color, other):
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

            return _recur(x * h + y)

        killed = 0
        for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            elem = child.goban[a * h + b]
            if elem == other and not _has_libs(child.goban, a, b, other, color):
                killed += _kill(child.goban, a, b, other, color)

        if not killed and not _has_libs(child.goban, x, y, color, other):
            return None, 0

        ancestor = self
        while ancestor is not None:
            if child.goban == ancestor.goban:
                return None, -1
            ancestor = ancestor.parent

        return child, killed

    def get_empty(self):
        h, w = self.height + 2, self.width + 2
        ret = []
        for x in xrange(1, self.width + 1):
            for y in xrange(1, self.height + 1):
                if self.goban[x * h + y] == BOARD_EMPTY:
                    ret.append((x - 1, y - 1))
        #if len(ret) <= 2:
        ret.append((-1, -1))
        return ret

    def count(self, color):
        h, w = self.height + 2, self.width + 2
        ret = 0
        for x in xrange(1, self.width + 1):
            for y in xrange(1, self.height + 1):
                if self.goban[x * h + y] == color:
                    ret += 1
        return ret

    def hash(self):
        return ''.join(self.goban)

    def copy(self):
        bkp_parent = self.parent
        self.parent = None
        #new_board = copy.deepcopy(self)
        new_board = Board()
        new_board.height = self.height
        new_board.width = self.width
        new_board.goban = [x[:] for x in self.goban]

        self.parent = bkp_parent
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
