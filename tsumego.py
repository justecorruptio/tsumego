from collections import Counter

from board import (
    Board,
    BOARD_EMPTY,
    BOARD_EDGE,
    BOARD_BLACK,
    BOARD_WHITE,
)

MAX_DEBUG_DEPTH = -1
MAX_DEPTH = 200


class Solver(object):
    def __init__(self, board):
        self.board = board

    def find_kill(self, color=BOARD_BLACK):
        other = color == BOARD_BLACK and BOARD_WHITE or BOARD_BLACK

        self.cache_hits = 0
        self.cache_misses = 0

        mem = {}
        good_as_dead = int(self.board.count(other) * .33)
        def _find_killer(board, depth=0):
            if depth > MAX_DEPTH:
                raise Exception("too deep")
                #return None

            hx = board.hash()
            if hx in mem:
                self.cache_hits += 1
                return mem[hx]
            self.cache_misses += 1

            #print board

            prospects = board.get_empty()

            ret = None
            while prospects:
                x, y = prospects.pop()
                if x == -1 and y == -1:
                    continue
                after_me, killed = board.play(x, y, color)
                if after_me is None:
                    continue
                if depth <= MAX_DEBUG_DEPTH:
                    print '  ' * depth, "X:", (x, y)
                if killed > good_as_dead or after_me.count(other) < 5:
                    ret = (x, y)
                    break

                if killed == 1 and after_me.is_lonely(x, y):
                    after_me, killed = after_me.parent.play(x, y, other)

                sol = _find_refute(after_me, depth + 1)

                if sol is None:
                    ret = (x, y)
                    break
                else:
                    if sol in prospects:
                        prospects.remove(sol)
                        prospects.append(sol)

                    if depth <= MAX_DEBUG_DEPTH:
                        print '  ' * depth, "r:", sol
                    pass
            mem[hx] = ret
            return ret

        jar = {}
        def _find_refute(after_me, depth):
            hx = after_me.hash()
            if hx in jar:
                return jar[hx]

            prospects = after_me.get_empty()
            while prospects:
                a, b = prospects.pop()
                after_them, killed = after_me.play(a, b, other)
                if after_them is None:
                    continue

                if depth <= MAX_DEBUG_DEPTH:
                    print '  ' * depth, "O:", (a, b)

                if killed == 1 and after_them.is_lonely(a, b):
                    # direct ko, give white another move
                    if _find_refute(after_them, depth + 1):
                        jar[hx] = (a, b)
                        return (a, b)

                sol = _find_killer(after_them, depth + 1)
                if sol is None:
                    jar[hx] = (a, b)
                    return (a, b)
                else:
                    if sol in prospects:
                        prospects.remove(sol)
                        prospects.append(sol)
            jar[hx] = None
            return None

        solution = _find_killer(self.board)
        print solution
        if not solution:
            return
        t = self.board
        print t
        x, y = solution
        t, killed = t.play(x, y, color)
        print t

        print "  CACHE HITS:", self.cache_hits
        print "CACHE MISSES:", self.cache_misses
        print "        RATE:", self.cache_hits * 1.0/ (self.cache_hits + self.cache_misses)


if __name__ == '__main__':
    b = Board()
    b.load(open('data/002_goban.txt', 'r').read())

    s = Solver(b)
    '''
    s.find_kill()

    '''
    import cProfile
    import pstats
    import StringIO
    cProfile.run('s.find_kill()', 'statsfile')
    stream = StringIO.StringIO()
    stats = pstats.Stats('statsfile', stream=stream)
    stats.sort_stats('time')
    stats.print_stats()
    print stream.getvalue()
