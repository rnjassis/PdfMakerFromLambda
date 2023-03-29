from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

config = {}

class Config:
    def __init__(self, wtm, font, footer, marginX, marginY, footer_color):
        self.watermark = wtm
        self.font = font
        self.footer = footer
        self.marginX = marginX
        self.marginY = marginY
        self.footer_color = footer_color

def create_pdf(imgs, cfg):
    """
    Convert the list of images to a pdf with watermark and footer
    :param imgs: [:py:class:`PIL.Image`]
    :param cfg: :py:class:`~Config`
    :return :py:class:`io.BytesIO` of PDF
    """

    global config
    config = cfg

    Image.frombytes

    result = make_pdf_images(imgs)
    rBytes = put_images_into_pdf(result)
    return rBytes

def make_pdf_images(baseImages):
    imgs = convert_images_to_jpg(baseImages)
    add_watermark_to_images(imgs)
    make_footer(imgs)
    return imgs

def put_images_into_pdf(result):
    r = result.pop()
    rBytes = BytesIO()
    r.save(rBytes, format='pdf', save_all=True, append_images=result)
    return rBytes

def convert_images_to_jpg(orgs):
    jpgs = []
    for org in orgs:
        jpgs.append(org.convert('RGB'))
    return jpgs

def add_watermark_to_images(jpgs):
    new_jpgs = []
    for jpg in jpgs:
        width, height = jpg.size
        wm = config.watermark.resize((width, height))
        jpg.paste(wm, (100, 100), mask=wm)

def make_footer(jpgs):
    new_jpgs = []
    text = config.footer
    for jpg in jpgs:
        draw = ImageDraw.Draw(jpg)
        width, height = jpg.size
        draw.text(xy=(config.marginX, height - config.marginY), text=text, font=config.font, fill=config.footer_color)

