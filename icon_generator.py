from PIL import Image, ImageDraw

SIZE = 32
BLACK = (0, 0, 0, 0)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)
GRAY = (64, 64, 64, 255)
def solid_circle(size: int, color: tuple, margin: int = 2):
    image = Image.new("RGBA", size=(size, size), color=BLACK)
    dc = ImageDraw.Draw(image)
    # draw a red circle
    delta = size - margin
    dc.ellipse((margin, margin, delta, delta), fill=color)
    return image

def ring_circle(size: int, color: tuple, margin: int = 2, width: int = 4):
    image = Image.new("RGBA", size=(size, size), color=BLACK)
    dc = ImageDraw.Draw(image)
    # draw a red circle
    delta = size - margin
    dc.ellipse((margin, margin, delta, delta), fill=color)
    # draw a black circle
    delta = size - margin - width
    dc.ellipse((margin + width, margin + width, delta, delta), fill=BLACK)
    return image

class ICONS:
    active = solid_circle(SIZE, RED)
    standby = ring_circle(SIZE, RED, width=5)
    paused = ring_circle(SIZE, BLUE, width=5)
    inactive = solid_circle(SIZE, GRAY)

if __name__ == "__main__":
    # use pil to show the icons
    ICONS.active.show()
    ICONS.standby.show()
    ICONS.paused.show()
    ICONS.inactive.show()