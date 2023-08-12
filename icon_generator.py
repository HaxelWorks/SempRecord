from tkinter import Y
from PIL import Image, ImageDraw


SIZE = 32
SIZES = [256, 128, 64, 32]
SSAA = 4 # super sampling anti aliasing
TRANSP = (0, 0, 0, 0)
RED = (234, 10, 3, 255)
YELLOW = (255, 255, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)
GRAY = (156, 156, 156, 255)
ORANGE = (255, 165, 0, 255)


def icoratio(size: int):
    sizes = [285, 235, 176, 73]
    ratio = 256 / size
    factor = 256 / 285
    sizes = [int((size/ratio) * factor) for size in sizes]
    return sizes


def icon_generator(size:int, color:tuple):
    """Generates an icon using the cicle diameters from icoratio"""
    size = size * SSAA
    image = Image.new("RGBA", size=(size, size), color=TRANSP)
    draw = ImageDraw.Draw(image)
    d1,d2,d3,d4 =icoratio(size)
    # draw a circle with diameter d1
    delta = (size-d1)/2
    draw.ellipse((delta, delta, size-delta-1, size-delta-1), fill=color)
    # cut out a circle with diameter d2 from the center aka make it transparent
    r1 = d1/2
    r2 = d2/2
    draw.ellipse((r1-r2, r1-r2, r1+r2, r1+r2), fill=TRANSP)
    # fill with a circle with diameter d3
    r3 = d3/2
    draw.ellipse((r1-r3, r1-r3, r1+r3, r1+r3), fill=color)
    # cut out a circle with diameter d4 from the center aka make it transparent
    r4 = d4/2
    draw.ellipse((r1-r4, r1-r4, r1+r4, r1+r4), fill=TRANSP)
    
    # downsample the image
    image = image.resize((size//SSAA, size//SSAA), resample=Image.LANCZOS)
    return image
    
    
class ICONS:
    active = icon_generator(SIZE, RED)
    paused = icon_generator(SIZE, YELLOW)
    standby = icon_generator(SIZE, ORANGE)
    inactive = icon_generator(SIZE, GRAY)
    rendering = icon_generator(SIZE, BLUE)
    
if __name__ == "__main__":
    # When running this file as a script, it will generate an icon containing the folloring resolutions:
    muli_res = [icon_generator(size, RED) for size in SIZES]
    ico_image = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
    ico_image.save("icon.ico", format="ICO",transparency=0, append_images=muli_res)
    
