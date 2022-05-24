import math
from PIL import Image, ImageOps

class EscposImage(object):
    def __init__(self, img_source, image_size, max_len_line):
        """
        Load in an image

        :param img_source: PIL.Image, or filename to load one from.
        :param image_size: one of this sm, md, lg.
        :param max_len_line: width based on size paper of printer.
        """
        if isinstance(img_source, Image.Image):
            img_original = img_source
        else:
            img_original = Image.open(img_source)

            maxwidth = max_len_line * 11
            wpercent  = (maxwidth / float(img_original.size[0]))
            maxheight = math.ceil((float(img_original.size[1]) * float(wpercent)))
            width_percent = maxwidth / img_original.size[0]
            height_percent = maxheight / img_original.size[1]

            img_original = self.resize_image(img_original, image_size, width_percent, height_percent)

        self.img_original = img_original
        # Convert to white RGB background, paste over white background
        # to strip alpha.
        img_original = img_original.convert('RGBA')
        im = Image.new("RGB", img_original.size, (255, 255, 255))
        im.paste(img_original, mask=img_original.split()[3])
        # Convert down to greyscale
        im = im.convert("L")
        # Invert: Only works on 'L' images
        im = ImageOps.invert(im)
        # Pure black and white
        self._im = im.convert("1")

    @property
    def width(self):
        """
        Width of image in pixels
        """
        width_pixels, _ = self._im.size
        return width_pixels

    @property
    def width_bytes(self):
        """
        Width of image if you use 8 pixels per byte and 0-pad at the end.
        """
        return (self.width + 7) >> 3

    @property
    def height(self):
        """
        Height of image in pixels
        """
        _, height_pixels = self._im.size
        return height_pixels

    def to_column_format(self, high_density_vertical=True):
        """
        Extract slices of an image as equal-sized blobs of column-format data.

        :param high_density_vertical: Printed line height in dots
        """
        im = self._im.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
        line_height = 24 if high_density_vertical else 8
        width_pixels, height_pixels = im.size
        top = 0
        left = 0
        while left < width_pixels:
            box = (left, top, left + line_height, top + height_pixels)
            im_slice = im.transform((line_height, height_pixels), Image.EXTENT, box)
            im_bytes = im_slice.tobytes()
            yield(im_bytes)
            left += line_height

    def to_raster_format(self):
        """
        Convert image to raster-format binary
        """
        return self._im.tobytes()

    def split(self, fragment_height):
        """
        Split an image into multiple fragments after fragment_height pixels

        :param fragment_height: height of fragment
        :return: list of PIL objects
        """
        passes = int(math.ceil(self.height/fragment_height))
        fragments = []
        for n in range(0, passes):
            left = 0
            right = self.width
            upper = n * fragment_height
            lower = min((n + 1) * fragment_height, self.height)
            box = (left, upper, right, lower)
            fragments.append(self.img_original.crop(box))
        return fragments

    def center(self, max_width):
        """In-place image centering

        :param: Maximum width in order to deduce x offset for centering
        :return: None
        """
        old_width, height = self._im.size
        new_size = (max_width, height)

        new_im = Image.new("1", new_size)
        paste_x = int((max_width - old_width) / 2)

        new_im.paste(self._im, (paste_x, 0))

        self._im = new_im

    def resize_image(self, im, image_size, width_percent, height_percent):
        base_percent = min(width_percent, height_percent)

        if image_size == 'sm':
            base_percent *= 0.5
        if image_size == 'md':
            base_percent *= 0.75
        if image_size == 'lg':
            dimensions = (math.ceil(im.size[0] * base_percent), math.ceil(im.size[1] * base_percent))
        else:
            dimensions = (int(im.size[0] * base_percent), int(im.size[1] * base_percent))
            
        im = im.resize(dimensions, Image.ANTIALIAS)
        return im