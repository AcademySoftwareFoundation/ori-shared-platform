def rv_to_itview(width, height, x, y=None):
    if y is None:
        a = rv_to_itview(width, height, 0, 0)
        b = rv_to_itview(width, height, x, 0)
        return b[0] - a[0]
    return [x * height / width + 0.5, y + 0.5]


def itview_to_rv(width, height, x, y=None):
    if y is None:
        a = itview_to_rv(width, height, 0, 0)
        b = itview_to_rv(width, height, x, 0)
        return b[0] - a[0]
    return [(x - 0.5) * width / height, y - 0.5]


def image_to_rv(width, height, x, y=None):
    if y is None:
        a = image_to_rv(width, height, 0, 0)
        b = image_to_rv(width, height, x, 0)
        return b[0] - a[0]
    return [(x - 0.5 * width) / height, y / height - 0.5]


def rv_to_image(width, height, x, y=None):
    if y is None:
        a = rv_to_image(width, height, 0, 0)
        b = rv_to_image(width, height, x, 0)
        return b[0] - a[0]
    return [x * height + 0.5 * width, (y + 0.5) * height]