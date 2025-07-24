from dataclasses import dataclass, field


@dataclass
class Color:
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 0.0

    def __getstate__(self):
        return [self.r, self.g, self.b, self.a]

    def __setstate__(self, state):
        self.r, self.g, self.b, self.a = state
        return self


@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, state):
        self.x, self.y = state
        return self


def image_to_itview(width, height, x, y=None):
    if y is None:
        a = image_to_itview(width, height, 0, 0)
        b = image_to_itview(width, height, x, 0)
        return b[0] - a[0]
    return x / width, y / height


def itview_to_image(width, height, x, y=None):
    if y is None:
        a = itview_to_image(width, height, 0, 0)
        b = itview_to_image(width, height, x, 0)
        return b[0] - a[0]
    return x * width, y * height


def screen_to_itview(geometry, x, y):
    t = geometry[0]
    u = [geometry[1][0] - t[0], geometry[1][1] - t[1]]
    v = [geometry[3][0] - t[0], geometry[3][1] - t[1]]
    k = 1.0 / (u[0] * v[1] - v[0] * u[1])
    d = [x - t[0], y - t[1]]
    return k * (v[1] * d[0] - v[0] * d[1]), k * (u[0] * d[1] - u[1] * d[0])


def itview_to_screen(geometry, x, y=None):
    if y is None:
        a = itview_to_screen(geometry, 0, 0)
        b = itview_to_screen(geometry, x, 0)
        return ((b[0] - a[0]) ** 2.0 + (b[1] - a[1]) ** 2.0) ** 0.5
    t = geometry[0]
    u = [geometry[1][0] - t[0], geometry[1][1] - t[1]]
    v = [geometry[3][0] - t[0], geometry[3][1] - t[1]]
    return u[0] * x + v[0] * y + t[0], u[1] * x + v[1] * y + t[1]


def insert_list_into_list(main_list, list_to_insert, index):
    out = []
    if len(main_list) == 0:
        out = list_to_insert
    elif index >= len(main_list):
        out = main_list + list_to_insert
    elif index < 0:
        out = list_to_insert + main_list
    else:
        for i, source_group in enumerate(main_list):
            if i == index:
                out.extend(list_to_insert)
            out.append(source_group)
    return out

def move_list_items_to_index(all_items, items_to_move, target_index):
    items_to_move = set(items_to_move)

    items_not_to_move = [id for id in all_items if id not in items_to_move]
    items_to_move = [id for id in all_items if id in items_to_move]
    count = sum(1 for i, item in enumerate(all_items) \
                if item in items_to_move and i <= target_index)

    if target_index < 0:
        actual_index = 0
    elif target_index >= len(all_items):
        actual_index = len(items_not_to_move)
    else:
        actual_index = target_index if count == 1 else \
            target_index - count + (1 if count > 1 else 0)

    reordered_items = items_not_to_move[:actual_index] + \
        items_to_move + items_not_to_move[actual_index:]

    return reordered_items

def negative_list_move(all_items, items_to_move, offset):
    num_of_items = len(all_items)
    moved_item_indexes = []
    for i in range(0, num_of_items):
        item = all_items[i]
        if item in items_to_move:
            offset_index = i+offset
            offset_index = max(0, offset_index)
            while all_items[offset_index] in \
                items_to_move and (offset_index < i):
                offset_index += 1
            for j in range(i, offset_index, -1):
                all_items[j] = all_items[j-1]
            all_items[offset_index] = item
            moved_item_indexes.append(offset_index)
    return moved_item_indexes

def positive_list_move(all_items, items_to_move, offset):
    num_of_items = len(all_items)
    moved_item_indexes = []
    for i in range(num_of_items-1, -1, -1):
        item = all_items[i]
        if item in items_to_move:
            offset_index = i+offset
            offset_index = min(num_of_items-1, offset_index)
            while all_items[offset_index] in \
                items_to_move and (offset_index > i):
                offset_index -= 1
            for j in range(i, offset_index):
                all_items[j] = all_items[j+1]
            all_items[offset_index] = item
            moved_item_indexes.append(offset_index)
    moved_item_indexes.reverse()
    return moved_item_indexes
