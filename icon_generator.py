from PIL import Image, ImageDraw

SIZE = 32
UPSAMPLE = 4
TRANSP = (0, 0, 0, 0)
RED = (245, 3, 1, 255)
YELLOW = (255, 255, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)
GRAY = (64, 64, 64, 255)

def icoratio(size: int):
    sizes = [285, 247, 206, 56]
    ratio = 256 / size
    factor = 256 / 285
    sizes = [int((size/ratio) * factor) for size in sizes]
    return sizes


def tray_icon_generator(size:int, color:tuple):
    """Generates a tray icon using the cicle diameters from icoratio"""
    size = size * UPSAMPLE
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
    image = image.resize((size//UPSAMPLE, size//UPSAMPLE), resample=Image.LANCZOS)
    return image
    
    

    
    

class ICONS:
    active = tray_icon_generator(SIZE, RED)
    paused = tray_icon_generator(SIZE, YELLOW)
    standby = tray_icon_generator(SIZE, BLUE)
    inactive = tray_icon_generator(SIZE, GRAY)
    
if __name__ == "__main__":
    # use pil to show the icons
    ICONS.active.show()
    ICONS.standby.show()
    ICONS.paused.show()
    ICONS.inactive.show()