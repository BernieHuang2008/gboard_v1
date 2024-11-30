"""
Objects:
* Point
* Segment
* Line

"""
import random
from tkinter.messagebox import *

from calc import *
from tkinter import *

objects = dict()
cooref = dict()
canvas: Canvas


def r(relation):
    if relation[0] == '.':
        return relation[1:]
    else:
        return relation


def cooRef(x, y, objID=None):
    global cooref
    xx, yy = x, y
    x //= 15
    y //= 15
    if objID is None:
        return cooref.get(x, dict()).get(y, set())
    cooref[x] = cooref.get(x, dict())
    cooref[x][y] = cooref[x].get(y, set())
    if objID not in cooref[x][y]:
        cooref[x][y].add(objID)
        return True
    else:
        return False


def del_cooRef(x, y, objID):
    global cooref
    xx, yy = x, y
    x //= 15
    y //= 15
    error = None
    if not objects.get(objID, False):
        raise Exception("Error while deleting cooRef: obj ( {} ) does not exist.".format(error))

    for xi, yi in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        try:
            cooref[x + xi][y + yi].remove(objID)
        except KeyError as e:
            error = e
    if error:
        if error == str(objID):
            raise Exception("Error while deleting cooRef: obj ( {} ) does not exist.".format(error))


def ErrorWindow(tit, msg):
    showerror(tit, msg)


def void(*args, **kwargs):
    pass


class BoardObj:
    @classmethod
    def check_relation(cls, elements: list, relation: str):
        """
        a function to test relationships between objects.

        :param elements: a list of objectID.
        :param relation: a type of relationship.
        :return: the result of test, True for 'valid' while False for 'invalid'
        """

        return True

    @classmethod
    def newID(cls):
        objectID = random.random()
        while objects.get(objectID, -1) != -1:
            objectID = random.random()
        return objectID

    def __init__(self, type_: str, attr: dict):
        self.type = type_
        self.attr = attr
        self.id = BoardObj.newID()
        objects[self.id] = self
        self.relation = []
        self.shows = [0, 0, 0]

    def newRelation(self, others: list, relation: str, do=False):
        """
        a function to add relationships between this object and other objects
        :param do: Parse or not parse the relationship.
        :param others: a list of objectID
        :param relation: a type of relationship
        :return:
        """
        if BoardObj.check_relation([self.id] + others, r(relation)):
            relationship = (tuple(others), relation)
            self.relation.append(relationship)
            if relation[0] != '.' and do:
                self.parseRelation(relationship)

    def parseRelation(self, relation):
        pass

    def parseAllRelations(self):
        for rel in self.relation:
            self.parseRelation(rel)

    def show_info(self):
        global win
        showin = Toplevel()

        showin.geometry('{}x{}+100+100'.format(600, 500))
        # showin.overrideredirect(True)
        showin.attributes("-topmost", True)
        showin.focus()

        scrollBar = Scrollbar(showin)
        scrollBar.pack(side=RIGHT, fill=Y)

        box = Listbox(showin, yscrollcommand=scrollBar.set, width=showin.winfo_reqwidth(),
                      height=showin.winfo_reqheight())
        scrollBar.config(command=box.yview)

        box.insert(END, "ID: " + str(self.id))
        box.insert(END, "Type: " + self.type)
        box.insert(END, "")

        box.insert(END, "Relations:")
        for rel in self.relation:
            box.insert(END, "    {} ( {} ) ".format(rel[1], ', '.join([str(x) for x in rel[0]])))

        box.pack()

    def moveto(self, *args, **kwargs):
        pass


class Point(BoardObj):
    """
    relationships for Point:
        * Segment(Point, Point) ...................... segment between Points
    """

    def __init__(self, x, y):
        super().__init__('Point', {'x': x, 'y': y})
        self.x = x
        self.y = y
        cooRef(x, y, self.id)
        self.show()

    def __str__(self):
        return "<Point object at ({}, {})>".format(self.x, self.y)

    def show(self, state=0):
        """
        :param state: 0 for default, 1 for selected.
        """
        canvas.delete(self.shows[0])
        canvas.delete(self.shows[1])
        canvas.delete(self.shows[2])
        x = self.x
        y = self.y
        if state == 1:  # selected
            self.shows[1] = canvas.create_arc(x - 12, y - 12, x + 12, y + 12, width=2, start=0, extent=359.9,
                                              outline='#ff57ff', fill='#FF57FF')
            self.shows[2] = canvas.create_arc(x - 8, y - 8, x + 8, y + 8, width=2, start=0, extent=359.9,
                                              outline='white', fill='white')
        self.shows[0] = canvas.create_arc(x - 7, y - 7, x + 7, y + 7, width=2, start=0, extent=359.9, fill='red')

    def parseRelation(self, relation):
        def segment(args):
            a = self
            b = objects[args[0]]
            line: Segment = objects[args[1]]
            try:
                line.del_cooref()
            except BaseException as e:
                print("e188", e)
            line.attr = {'a': a.id, 'b': b.id, 'x0': a.x, 'y0': a.y, 'x1': b.x, 'y1': b.y,
                         'k': LineSlope((a.x, a.y), (b.x, b.y))}
            line.show()
            a.show()
            b.show()
            line.cooref()
            line.parseAllRelations()

        def line(args):
            a = self
            if args[0] == 1:
                l, b = args[1], args[2]
                l = objects[l]
                b = objects[b]
                l.k = LineSlope((a.x, a.y), (b.x, b.y))
                l.bias = l.k * a.x - a.y
                l.attr = {'class': args[0], 'a': a.id, 'b': b.id, 'k': l.k, 'bias': l.bias}
                l.show()
                a.show()
                b.show()
                l.parseAllRelations()

        def default(args):
            raise Exception("Error while parsing relation: invalid relation '{}'.".format(relation[1]))

        if relation[1][0] != '.':
            {
                'segment': segment,
                'line': line,
            }.get(relation[1], default)(relation[0])

    def moveto(self, newx, newy, alert=False):
        if self.available(newx, newy):
            self.attr = {'x': newx, 'y': newy}
            del_cooRef(self.x, self.y, self.id)
            self.x = newx
            self.y = newy
            cooRef(self.x, self.y, self.id)
            self.parseAllRelations()
            self.show()
            canvas.moveto(self.shows[0], newx - 7, newy - 7)
            return True
        elif alert:
            ErrorWindow("Contradiction", "Contradiction Relations at \nPoint ( {} )".format(self.id))
            raise GeometryError("Contradiction Relations at Point({}).".format(self.id))
        else:
            return False

    def available(self, newx, newy):
        for rel in self.relation:
            relName = rel[1]
            relArgs = rel[0]
            if relName[0] != '.':
                continue
            if relName == '.on_segment':
                # must be on the segment
                line = relArgs[1]
                line = objects[line]
                if PointOnLine((newx, newy), line.attr['k'], self.y - self.x * line.attr['k']):
                    if min(line.attr['x0'], line.attr['x1']) <= newx <= max(line.attr['x0'], line.attr['x1']) \
                            and min(line.attr['y0'], line.attr['y1']) <= newy <= max(line.attr['y0'], line.attr['y1']):
                        continue
                    return False
                return False
            if relName == '.mid_point':
                seg = objects[relArgs[0]]
                if (newx, newy) == ((seg.a.x + seg.b.x) / 2, (seg.a.y + seg.b.y) / 2):
                    continue
                else:
                    return False

        return True

    def info(self):
        return {"id": self.id, "relations": self.relation, "position": (self.x, self.y)}

    def show_info(self):
        global win
        showin = Toplevel()

        showin.geometry('{}x{}+100+100'.format(600, 500))
        # showin.overrideredirect(True)
        showin.attributes("-topmost", True)
        showin.focus()

        scrollBar = Scrollbar(showin)
        scrollBar.pack(side=RIGHT, fill=Y)

        box = Listbox(showin, yscrollcommand=scrollBar.set, width=showin.winfo_reqwidth(),
                      height=showin.winfo_reqheight())
        scrollBar.config(command=box.yview)

        box.insert(END, "ID: " + str(self.id))
        box.insert(END, "Type: " + self.type)
        box.insert(END, "")

        box.insert(END, "Position: " + str((self.x, self.y)))
        box.insert(END, "")

        box.insert(END, "Relations:")
        for rel in self.relation:
            box.insert(END, "    {} ( {} ) ".format(rel[1], ', '.join([str(x) for x in rel[0]])))

        box.pack()


class Segment(BoardObj):
    def __init__(self, a: Point, b: Point):
        if not isinstance(a, Point) or not isinstance(b, Point):
            raise Exception('Error while creating Line: params must be Points')

        self.a = a
        self.b = b
        super().__init__('Segment',
                         {'a': a.id, 'b': b.id, 'x0': a.x, 'y0': a.y, 'x1': b.x, 'y1': b.y,
                          'k': LineSlope((a.x, a.y), (b.x, b.y))})
        a.newRelation([b.id, self.id], "segment", do=True)
        b.newRelation([a.id, self.id], "segment")
        self.newRelation([a.id, b.id], ".segment")

    def __str__(self):
        return "<Segment object a=({}, {}) b=({}, {})>".format(self.a.x, self.a.y, self.b.x, self.b.y)

    def cooref(self):
        a = self.a
        b = self.b
        moveX = moveY = 0
        if self.attr['k']:
            moveX = 1 / sqrt(pow(self.attr['k'], 2) + 1) * 15
            moveY = self.attr['k'] * moveX
        else:
            if a.x == b.x:
                moveY = 15
            else:
                moveX = 15
        dif = 1 if a.x < b.x else -1
        for i in range(1, floor(PointDistance((a.x, a.y), (b.x, b.y)) // 15)):
            cx = a.x + i * moveX * dif
            cy = a.y + i * moveY * dif
            cooRef(cx, cy, self.id)

    def del_cooref(self):
        moveX = moveY = 0
        if self.attr['k']:
            moveX = 1 / sqrt(pow(self.attr['k'], 2) + 1) * 15
            moveY = self.attr['k'] * moveX
        else:
            if self.attr['x0'] == self.attr['x1']:
                moveY = 15
            else:
                moveX = 15
        dif = 1 if self.attr['x0'] < self.attr['x1'] else -1
        for i in range(1, floor(PointDistance((self.attr['x0'], self.attr['y0']),
                                              (self.attr['x1'], self.attr['y1'])) // 15)):
            cx = self.attr['x0'] + i * moveX * dif
            cy = self.attr['y0'] + i * moveY * dif
            del_cooRef(cx, cy, self.id)

    def show(self, state=0):
        a, b = self.a, self.b
        canvas.delete(self.shows[0])
        canvas.delete(self.shows[1])
        canvas.delete(self.shows[2])
        try:
            self.del_cooref()
        except:
            pass
        if state == 1:  # selected
            self.shows[1] = canvas.create_line(a.x, a.y, b.x, b.y, width=14, fill='#ff57ff')
            self.shows[2] = canvas.create_line(a.x, a.y, b.x, b.y, width=10, fill='white')
        self.shows[0] = canvas.create_line(a.x, a.y, b.x, b.y, width=8, fill='#000080')
        self.cooref()

    def show_info(self):
        global win
        showin = Toplevel()

        showin.geometry('{}x{}+100+100'.format(600, 500))
        # showin.overrideredirect(True)
        showin.attributes("-topmost", True)
        showin.focus()

        scrollBar = Scrollbar(showin)
        scrollBar.pack(side=RIGHT, fill=Y)

        box = Listbox(showin, yscrollcommand=scrollBar.set, width=showin.winfo_reqwidth(),
                      height=showin.winfo_reqheight())
        scrollBar.config(command=box.yview)

        box.insert(END, "ID: " + str(self.id))
        box.insert(END, "Type: " + self.type)
        box.insert(END, "")
        box.insert(END, "A: " + str((self.a.x, self.a.y)))
        box.insert(END, "B: " + str((self.b.x, self.b.y)))
        box.insert(END, "k: " + str(self.attr['k']))

        box.insert(END, "")
        box.insert(END, "Relations:")
        for rel in self.relation:
            box.insert(END, "    {} ( {} ) ".format(rel[1], ', '.join([str(x) for x in rel[0]])))

        box.pack()

    def parseRelation(self, relation):
        def mid_point(args):
            newx, newy = (self.a.x + self.b.x) / 2, (self.a.y + self.b.y) / 2
            p: Point = objects[args[0]]
            if p.available(newx, newy):
                p.moveto(newx, newy)
            else:
                ErrorWindow("Contradiction",
                            "Relations at\nmid_point( {} , {} )".format(p.id, self.id))

                raise GeometryError("Contradiction Relation between mid_point( {} , {} ).".format(p.id, self.id))

        def default(args):
            raise Exception("Error while parsing relation: invalid relation '{}'.".format(relation[1]))

        {
            'mid_point': mid_point,
            '.segment': void,
        }.get(relation[1], default)(relation[0])


class Line(BoardObj):
    def __init__(self, a: Point = None, b: Point = None, k: int = None, bias: int = None):
        if k and bias:
            self.cls = 0
            self.k = k
            self.bias = bias
            super().__init__("Line", {'class': 0, 'k': k, 'bias': bias})
        elif a and b:
            self.cls = 1
            self.k = LineSlope((a.x, a.y), (b.x, b.y))
            self.bias = self.k * a.x - a.y
            self.a = a
            self.b = b
            super().__init__("Line", {'class': 1, 'a': a.id, 'b': b.id, 'k': k, 'bias': bias})
            a.newRelation([1, self.id, b.id], "line")
            b.newRelation([1, self.id, a.id], "line")
        elif a and k:
            self.k = k
            self.a = a
            self.cls = 2
            self.b = a.y - self.k * a.x
            super().__init__("Line", {'class': 2, 'a': a.id, 'k': k, 'bias': bias})
            a.newRelation([2, self.id, k], "line")

    def cooref(self):
        ...

    def del_cooref(self):
        ...

    def show(self, state):
        a, b = self.a, self.b
        canvas.delete(self.shows[0])
        canvas.delete(self.shows[1])
        canvas.delete(self.shows[2])
        try:
            self.del_cooref()
        except:
            pass
        if state == 1:  # selected
            self.shows[1] = canvas.create_line(0, self.bias, 4000, 4000 * self.k + self.bias, width=14, fill='#ff57ff')
            self.shows[2] = canvas.create_line(0, self.bias, 4000, 4000 * self.k + self.bias, width=10, fill='white')
        self.shows[0] = canvas.create_line(0, self.bias, 4000, 4000 * self.k + self.bias, width=8, fill='#000080')
        self.cooref()


class GeometryError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


def clear():
    ...
