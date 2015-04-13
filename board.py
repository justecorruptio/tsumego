import copy
import re

BOARD_EMPTY = '.'
BOARD_EDGE = '+'
BOARD_BLACK = 'X'
BOARD_WHITE = 'O'


class Board(object):
    def __init__(self):
        self.parent = None
        self._hash = None

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

        if killed:
            ancestor = self
            while ancestor is not None:
                if child.hash() == ancestor.hash():
                    return None, -1
                ancestor = ancestor.parent

        return child, killed

    def has_libs(self, pos, color, other):
        h = self.height + 2
        if self.unkillable[pos]:
            return True
        goban = self.goban

        # must copy
        marks = self.marks[:]

        stack = []
        ptr = 0
        while True:
            if goban[pos] == BOARD_EMPTY:
                return True
            if marks[pos] or goban[pos] != color:
                if ptr >= len(stack):
                    return False
                pos = stack[ptr]
                ptr += 1
                continue
            marks[pos] = 1
            stack.extend((
                pos + h,
                pos - h,
                pos + 1,
            ))
            pos -= 1

        return False

    def kill(self, pos, color, other):
        h = self.height + 2
        goban = self.goban

        # must copy
        marks = self.marks[:]

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

    def is_lonely(self, x, y):
        x += 1; y += 1
        h = self.height + 2
        libs = 0
        pos = x * h + y
        color = self.goban[pos]
        for tonari in (pos + h, pos - h, pos + 1, pos - 1):
            if self.goban[tonari] == BOARD_EMPTY:
                libs += 1
            if self.goban[tonari] == color:
                return False
        return libs == 1

    def get_empty(self):
        h, w = self.height + 2, self.width + 2
        ret = [(-1, -1)]
        for x in self.x_range:
            for y in self.y_range:
                if self.goban[x * h + y] == BOARD_EMPTY:
                    ret.append((x - 1, y - 1))

        mh = h >> 1
        mw = w >> 1
        ret.sort(key=lambda v: -abs(v[0] - mw) - abs(v[1] - mh))
        # We use this in reverse order later.
        return ret

    def count(self, color):
        ret = 0
        for elem in self.goban:
            if elem == color:
                ret += 1
        return ret

    def hash(self):
        if not self._hash:
            self._hash = ''.join(self.goban)
        return self._hash

    def copy(self):
        new_board = Board()
        new_board.height = self.height
        new_board.width = self.width
        new_board.goban = self.goban[:]

        # OK to reference first items, we make a copy anyways
        new_board.marks = self.marks
        new_board.x_range = self.x_range
        new_board.y_range = self.y_range

        new_board.unkillable = self.unkillable
        return new_board

    def load(self, pos_string):
        rows = pos_string.strip().split('\n')
        rows = [re.sub('[^\+\-\.\|OX]', '', x) for x in rows]
        self.height = len(rows)
        self.width = len(rows[0])
        h, w = self.height + 2, self.width + 2
        self.goban = [BOARD_EMPTY] * (h * w)
        self.marks = [0] * len(self.goban)
        self.x_range = range(1, self.width + 1)
        self.y_range = range(1, self.height + 1)

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

        self.unkillable = [0] * (h * w)

        def mark_unkillable(pos):
            color = self.goban[pos]
            if color not in (BOARD_BLACK, BOARD_WHITE):
                return

            def _recur(pos):
                if self.goban[pos] != color or self.unkillable[pos]:
                    return
                self.unkillable[pos] = 1
                _recur(pos + h)
                _recur(pos - h)
                _recur(pos + 1)
                _recur(pos - 1)

            return _recur(pos)

        for x in xrange(self.width):
            mark_unkillable((x + 1) * h + 1)
            mark_unkillable((x + 1) * h + self.height)

        for y in xrange(self.height):
            mark_unkillable(h + y)
            mark_unkillable(self.width * h + y)

        self.unkillable = tuple(self.unkillable)

    def __str__(self):
        h, w = self.height + 2, self.width + 2
        ret = ''
        for y in self.y_range:
            for x in self.x_range:
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
