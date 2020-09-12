import favicon
import base64
import requests
import io
from PIL import Image, UnidentifiedImageError


def get_favicon_base64(url):
    image_bytes = requests.get(url).content
    return image_bytes


def get_favicon_dimensions(base64):
    icon = Image.open(io.BytesIO(base64))
    return icon.size[0]


# def get_favicon(url):

#     icon_list = favicon.get(url)
#     icon = icon_list[0]

#     result = get_base64(icon.url)

#     # this is the HTML format Icon data
#     # icon = "data:image/" + icon.format + ";base64," + result.decode()

#     icon_bytes = result.decode()

#     return icon_bytes


def get_favicon_iconuri(url):

    globe_icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAH6SURBVDiNdZO/axRREMc/8y7h2DtSnKcQRBSuyx9gKYFYJbbGVrE4YyMEYt4mpFgVYXNbXHGJpBFFy9QxaVLoH2AhGLDwCBIRDBYJuptw3hubXV0ecbr5vu+PYXgjeBVFUS1N0xngujHmEoBz7gDYHQwGW91uNyvzpdyEYXhXVZ8C457vL6AOfBOR5TiOXxYPpjCy1j5T1edniI+CIBg3xtwAvqvqC2vtWhEuANbaFeCJJ/zsnLuVJMn7Ami326ONRqMH3AOWVldXYwnDsKWqe0C1JB4EQXA+iqJjf0ezs7OVVqu1BUyKyMSIc25ORKoebzTLsiNrbdEfAOv9fj/Z3NwcWmsfAh+cc3MjwLSfkteeqm6LyFXgQr7EoiaAQ2PMtFhrj4ExT/wqTdN2r9c7LYAwDKecc1dE5BOwk2uOR85IznwxwHA4HBpj1oGgjBtg3zP43Ww2B75rkiRv0zRtAIcFJiL7RlV3PO5YlmWPFhYW6h5OvV6/BjSL3jm3bYwxG8Cpx12pVCo/rbU/yqCqLvPv850YYzZMHMd94LGflte5KIpqAIuLizeBydL4URzH+8UtiLV2Hbh/hsltEfmoqu+AWi5ei+P4AaD+Md3Jj+nifyb6qqpLnU7n9d9JfMb8/HxQrVZngCngcg5/cc7t1mq1N1EUnZT5fwBV0MXmOmx04gAAAABJRU5ErkJggg=="

    try:
        icon_list = favicon.get(url)
    except:
        return (None, globe_icon)

    icons = []

    for i in icon_list:
        img_bytes = get_favicon_base64(i.url)
        try:
            dim = get_favicon_dimensions(img_bytes)
        except UnidentifiedImageError:
            continue
        img_base64 = base64.b64encode(img_bytes)
        img_html = "data:image/" + i.format + ";base64," + img_base64.decode()
        icons.append((dim, i.url, img_html))

    try:
        icons.sort()
        if icons[0][0] > 196:
            raise Exception("Image too big!!")
        icon = icons[0][1:]
    except IndexError:
        icon = (None, globe_icon)
    except:
        icon = (None, globe_icon)

    return icon

