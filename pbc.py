#!/usr/bin/env python3
"""
This is pbc (Python Background Creator).
A program that can generate background-images for your presentations.

Use this program to easily create a nice looking background for your presentations!
So far it has proven to work with PowerPoint, LibreOffice Impress, and LaTeX's Beamer.
All you have to do essentially, is to set the image as the slide background and voílà!
Custom made backdrops!  You could of course make these by hand but it becomes quite
tedious if you wanna make multiple images.

As a little side note: This program is not an add-on for the above mentioned softwares
(PowerPoint, etc.) but rather its own program which can be used to make images that
are intendet to be used in such software.  Essentially: create your own designs!

You can find more information about the program in the manual.
"""

from PIL import Image
from PIL import ImageFilter
import os.path
from os import getcwd
from os import chdir


class Background:

    #image_location = None  # location of the images to import
    save_location = ''     # location to which images are saved

    def __init__(self, image_name, **margins):
        """Initialize all the values for the program.

        image_name:   Argument specifying the name of the image. You can also specify the
                      path to the image. NOTE that the image extension must be given.
                      Examples:

                        im1 = Background('my_picture.jpg')
                        im2 = Background('path/to/my_picture.png')   [linux, mac]
                        im3 = Background('path\\to\\my_picture.png') [windows]

        **margins:   Keyword arguments specifying margin sizes. If the value entered is
                     smaller than 1 then the margin thickness is expressed as a relative
                     value. If the value is greater or equal to 1 then the thickness is
                     expressed as the number of pixels. Below are listed the different
                     keywords which you can use alongside their default values, as well as
                     examples at the end to illustrate.

                        header_left = 0.1
                        header_right = 0.1
                        header_top = 0.2
                        header_bottom = 0.2

                        body_left = 0.15
                        body_right = 0.15
                        body_top = 0.1
                        body_bottom = 0.1

                    The above keywords can also be given under a different form:

                        header = {
                            'left': 0.1,
                            'right': 0.1,
                            'top': 0.2,
                            'bottom': 0.2
                        }
                        body = {
                            'left': 0.15,
                            'right': 0.15,
                            'top': 0.1,
                            'bottom': 0.1
                        }

                    There is also a special keyword with which you can set the header to
                    body ratio:

                        hbratio = 0.2

                    The following examples will be presented under the different forms in
                    which you can enter the values.
                    Examples:

                        im = Background('pic.png', header_left=0.2, header_right=0.2)
                        im = Background('pic.png', header={'left': 0.2, 'right': 0.2})

                    Here the left and right margin have the size of:
                    0.2 * 'width of the image'.

                        im = Background('pic.jpg', body={'left': 0, 'right': 0})
                        im = Background('pic.jpg', body_left=0, body_right=0)

                    The left and right margin of the body is non-existent. They are
                    basically the right and left margin of the image.

                        im = Background('pic.jpg', header_top=0.5, header={'bottom': 0})
                        im = Background('pic.jpg', header={'top': 0.5}, header_bottom=0)
                        im = Background('pic.jpg', header_top=0.5, header_bottom=0)
                        im = Background('pic.jpg', header={'top': 0.5, 'bottom': 0})

                    The top margin has half the size of the height of the header and the
                    bottom margin is non-existent, which means that the bottom margin of
                    the header is basically where the body begins.

                        im = Background('pic.png', body_bottom=0.5)
                        im = Background('pic.png', body={'bottom': 0.5})

                    The bottom margin has half the size of the height of the body.

                    So the values smaller than 1 are expressed relative to their
                    respective area. Either the image width for 'left' and 'right' or the
                    header/body height for 'top' and 'bottom'.

                    You can replace the values in the examples above with a number greater
                    or equal to 1, in which case the thickness is expressed in pixels. If
                    the value exceeds the borders of the respective area (header or body),
                    an error will raise: ValueError.

                    The header to body ratio can be set the following way:

                        im1 = Background('pic.png', hbratio = 0.25)
                        im2 = Background('pic.png', hbratio = 0.5)

                    For im1 the header will take up a quarter of the image and for im2
                    the header and the body will be split in the middle of the image.
                    NOTE that there is only one way to specify this keyword. You can only
                    insert a value smaller or equal to 1.
        """

        # Calculate width and height differences as well as box sizes.
        # To be used with a 4 length tuple defining a box/rectangle.
        delta_x = lambda box: box[2] - box[0]
        delta_y = lambda box: box[3] - box[1]
        delta = lambda box: (delta_x(box), delta_y(box))
        boxsize = delta

        self.image_name = os.path.split(image_name)[1]
        self.image_path = os.path.split(image_name)[0]
        self.im_obj = Image.open(image_name)
        self.__imco = self.im_obj.copy()  # copy of the original image. Don't alter it!

        # Image dimensions
        self.width =   self.im_obj.size[0]   # Pillow module attribute
        self.height =  self.im_obj.size[1]
        self.size =    self.im_obj.size
        self.rect =    (0,0,self.size)

        self.hbratio = margins.get("hbratio", 0.2)  # header-body ratio
        self._include_margins = True  # set whether margins are included or not by default
        #### SET WHETHER TO USE i.e. 'top-incl' or 'top-excl' as default
        self.__silent_include = False  # Output a message when in/excluding margins

        # HEADER dimensions
        self.header_width =   self.width
        self.header_height =  int(self.height * self.hbratio)
        self.header_size =    (self.header_width, self.header_height)
        self.header_rect =    (0, 0, self.header_width, self.header_height)

        # may be altered through **margins
        #-header margin thickness
        margin_size = margins.get("header_left", margins.get("header", {}).get("left", 0.1))
        if margin_size < 0 or margin_size > self.header_width:
            raise ValueError("Value exceeds boundary! Header width = {}, given value = {}".format(self.header_width, margin_size))
        elif margin_size < 1:
            self.header_margin_left_thickness_factor = margin_size
            self.header_margin_left_thickness = int(self.header_width * self.header_margin_left_thickness_factor)
        else:
            self.header_margin_left_thickness = int(margin_size)
            self.header_margin_left_thickness_factor = self.header_margin_left_thickness / self.header_width

        margin_size = margins.get("header_right", margins.get("header", {}).get("right", 0.1))
        if margin_size < 0 or margin_size > self.header_width:
            raise ValueError("Value exceeds boundary! Header width = {}, given value = {}".format(self.header_width, margin_size))
        elif margin_size < 1:
            self.header_margin_right_thickness_factor = margin_size
            self.header_margin_right_thickness = int(self.header_width * self.header_margin_right_thickness_factor)
        else:
            self.header_margin_right_thickness = int(margin_size)
            self.header_margin_right_thickness_factor = self.header_margin_right_thickness / self.header_width

        margin_size = margins.get("header_top", margins.get("header", {}).get("top", 0.2))
        if margin_size < 0 or margin_size > self.header_height:
            raise ValueError("Value exceeds boundary! Header height = {}, given value = {}".format(self.header_height, margin_size))
        elif margin_size < 1:
            self.header_margin_top_thickness_factor = margin_size
            self.header_margin_top_thickness = int(self.header_height * self.header_margin_top_thickness_factor)
        else:
            self.header_margin_top_thickness = int(margin_size)
            self.header_margin_top_thickness_factor = self.header_margin_top_thickness / self.header_height

        margin_size = margins.get("header_bottom", margins.get("header", {}).get("bottom", 0.2))
        if margin_size < 0 or margin_size > self.header_height:
            raise ValueError("Value exceeds boundary! Header height = {}, given value = {}".format(self.header_height, margin_size))
        elif margin_size < 1:
            self.header_margin_bottom_thickness_factor = margin_size
            self.header_margin_bottom_thickness = int(self.header_height * self.header_margin_bottom_thickness_factor)
        else:
            self.header_margin_bottom_thickness = int(margin_size)
            self.header_margin_bottom_thickness_factor = self.header_margin_bottom_thickness / self.header_height

        # BODY dimensions
        self.body_width =   self.width
        self.body_height =  int(self.height*(1-self.hbratio))
        self.body_size =    (self.body_width, self.body_height)
        self.body_rect =    (0, self.header_height, self.body_width, self.body_height + self.header_height)

        #-body margin thickness
        margin_size = margins.get("body_left", margins.get("body", {}).get("left", 0.15))
        if margin_size < 0 or margin_size > self.body_width:
            raise ValueError("Value exceeds boundary! Body width = {}, given value = {}".format(self.body_width, margin_size))
        elif margin_size < 1:
            self.body_margin_left_thickness_factor = margin_size
            self.body_margin_left_thickness = int(self.body_width * self.body_margin_left_thickness_factor)
        else:
            self.body_margin_left_thickness = int(margin_size)
            self.body_margin_left_thickness_factor = self.body_margin_left_thickness / self.body_width

        margin_size = margins.get("body_right", margins.get("body", {}).get("right", 0.15))
        if margin_size < 0 or margin_size > self.body_width:
            raise ValueError("Value exceeds boundary! Body width = {}, given value = {}".format(self.body_width, margin_size))
        elif margin_size < 1:
            self.body_margin_right_thickness_factor = margin_size
            self.body_margin_right_thickness = int(self.body_width * self.body_margin_right_thickness_factor)
        else:
            self.body_margin_right_thickness = int(margin_size)
            self.body_margin_right_thickness_factor = self.body_margin_right_thickness / self.body_width

        margin_size = margins.get("body_top", margins.get("body", {}).get("top", 0.1))
        if margin_size < 0 or margin_size > self.body_width:
            raise ValueError("Value exceeds boundary! Body height = {}, given value = {}".format(self.body_height, margin_size))
        elif margin_size < 1:
            self.body_margin_top_thickness_factor = margin_size
            self.body_margin_top_thickness = int(self.body_height * self.body_margin_top_thickness_factor)
        else:
            self.body_margin_top_thickness = int(margin_size)
            self.body_margin_top_thickness_factor = self.body_margin_top_thickness / self.body_height

        margin_size = margins.get("body_bottom", margins.get("body", {}).get("bottom", 0.1))
        if margin_size < 0 or margin_size > self.body_width:
            raise ValueError("Value exceeds boundary! Body height = {}, given value = {}".format(self.body_height, margin_size))
        elif margin_size < 1:
            self.body_margin_bottom_thickness_factor = margin_size
            self.body_margin_bottom_thickness = int(self.body_height * self.body_margin_bottom_thickness_factor)
        else:
            self.body_margin_bottom_thickness = int(margin_size)
            self.body_margin_bottom_thickness_factor = self.body_margin_bottom_thickness / self.body_height


        # HEADER
        #-header content area
        self.header_cont_rect = (
                self.header_margin_left_thickness,
                self.header_margin_top_thickness,
                self.header_width - self.header_margin_right_thickness,
                self.header_height - self.header_margin_bottom_thickness
        )
        #self.header_cont_width =  self.header_width - (self.header_margin_left_thickness + self.header_margin_right_thickness)
        self.header_cont_width =  delta_x(self.header_cont_rect)
        self.header_cont_height = self.header_height - (self.header_margin_top_thickness + self.header_margin_bottom_thickness)
        #self.header_cont_size =   (self.header_cont_width, self.header_cont_height)
        self.header_cont_size =   boxsize(self.header_cont_rect)

        #~header margins (inclusive)
        self.header_margin_left_inclusive = (
                0,
                0,
                self.header_margin_left_thickness,
                self.header_height
                )
        self.header_margin_right_inclusive = (
                self.header_width - self.header_margin_right_thickness,
                0,
                self.header_width,
                self.header_height
                )
        self.header_margin_top_inclusive = (
                0,
                0,
                self.header_width,
                self.header_margin_top_thickness
                )
        self.header_margin_bottom_inclusive = (
                0,
                self.header_margin_top_thickness + self.header_cont_height,
                self.header_width,
                self.header_height
                )
        #~header margins (exclusive)
        self.header_margin_left_exclusive = (
                0,
                self.header_margin_top_thickness,
                self.header_margin_left_thickness,
                self.header_height - self.header_margin_bottom_thickness
                )
        self.header_margin_right_exclusive = (
                self.header_width - self.header_margin_right_thickness,
                self.header_margin_top_thickness,
                self.header_width,
                self.header_height - self.header_margin_bottom_thickness
                )
        self.header_margin_top_exclusive = (
                self.header_margin_left_thickness,
                0,
                self.header_width - self.header_margin_right_thickness,
                self.header_margin_top_thickness
                )
        self.header_margin_bottom_exclusive = (
                self.header_margin_left_thickness,
                self.header_height - self.header_margin_bottom_thickness,
                self.header_width - self.header_margin_right_thickness,
                self.header_height
                )
        #~header margin sizes
        # for i in ['inclusive', 'exclusive']:
        #     for region in ['left', 'right', 'top', 'bottom']:
        #         exec("self.header_margin_{0}_{1}_size = boxsize(self.header_margin_{0}_{1})".format(region,i))
        self.header_margin_left_inclusive_size =    (self.header_margin_left_thickness, self.header_height)
        self.header_margin_right_inclusive_size =   (self.header_margin_right_thickness, self.header_height)
        self.header_margin_top_inclusive_size =     (self.header_width, self.header_margin_top_thickness)
        self.header_margin_bottom_inclusive_size =  (self.header_width, self.header_margin_bottom_thickness)

        self.header_margin_left_exclusive_size =    boxsize(self.header_margin_left_exclusive)
        self.header_margin_right_exclusive_size =   boxsize(self.header_margin_right_exclusive)
        self.header_margin_top_exclusive_size =     boxsize(self.header_margin_top_exclusive)
        self.header_margin_bottom_exclusive_size =  boxsize(self.header_margin_bottom_exclusive)

        # BODY
        #-body content area
        self.body_cont_rect = (
                self.body_margin_left_thickness,
                self.header_height + self.body_margin_top_thickness,
                self.body_width - self.body_margin_right_thickness,
                self.height - self.body_margin_bottom_thickness
                )
        self.body_cont_width =  self.body_width - (self.body_margin_left_thickness + self.body_margin_right_thickness)
        self.body_cont_height = self.body_height - (self.body_margin_top_thickness + self.body_margin_bottom_thickness)
        self.body_cont_size =   (self.body_cont_width, self.body_cont_height)

        #~body margin areas (inclusive)
        self.body_margin_left_inclusive = (
                0,
                self.header_height,
                self.body_margin_left_thickness,
                self.height
                )
        self.body_margin_right_inclusive = (
                self.body_width - self.body_margin_right_thickness,
                self.header_height,
                self.body_width,
                self.height
                )
        self.body_margin_top_inclusive = (
                0,
                self.header_height,
                self.body_width,
                self.header_height + self.body_margin_top_thickness
                )
        self.body_margin_bottom_inclusive = (
                0,
                self.height - self.body_margin_bottom_thickness,
                self.body_width,
                self.height
                )

        #~body margin areas (exclusive)
        self.body_margin_left_exclusive = (
                0,
                self.header_height + self.body_margin_top_thickness,
                self.body_margin_left_thickness,
                self.height - self.body_margin_bottom_thickness
                )
        self.body_margin_right_exclusive = (
                self.body_width - self.body_margin_right_thickness,
                self.header_height + self.body_margin_top_thickness,
                self.body_width,
                self.height - self.body_margin_bottom_thickness
                )
        self.body_margin_top_exclusive = (
                self.body_margin_left_thickness,
                self.header_height,
                self.body_width - self.body_margin_right_thickness,
                self.header_height + self.body_margin_top_thickness
                )
        self.body_margin_bottom_exclusive = (
                self.body_margin_left_thickness,
                self.height - self.body_margin_bottom_thickness,
                self.body_width - self.body_margin_right_thickness,
                self.height
                )

        #~body margin sizes
        # for i in ['inclusive', 'exclusive']:
        #     for region in ['left', 'right', 'top', 'bottom']:
        #         exec("self.body_margin_{0}_{1}_size = boxsize(self.body_margin_{0}_{1})".format(region, i))
        self.body_margin_left_inclusive_size =    boxsize(self.body_margin_left_inclusive)
        self.body_margin_right_inclusive_size =   boxsize(self.body_margin_right_inclusive)
        self.body_margin_top_inclusive_size =     boxsize(self.body_margin_top_inclusive)
        self.body_margin_bottom_inclusive_size =  boxsize(self.body_margin_bottom_inclusive)

        self.body_margin_left_exclusive_size =    boxsize(self.body_margin_left_exclusive)
        self.body_margin_right_exclusive_size =   boxsize(self.body_margin_right_exclusive)
        self.body_margin_top_exclusive_size =     boxsize(self.body_margin_top_exclusive)
        self.body_margin_bottom_exclusive_size =  boxsize(self.body_margin_bottom_exclusive)

        self.__area = {
            # 'part':
            'full': {
                # 'region':     ((size tuple), (top left corner location tuple), (4 tuple area rectangle))
                'full':         (self.size,         (0,0),                (0,0,self.width,self.height)),
                'inner':        ((20,20),           (20,20)),
                'top-incl':     (self.header_size,  self.header_rect[:2], self.header_rect),                 # self.__area['header']['full']
                'top-excl':     (self.header_cont_size,  self.header_cont_rect[:2],  self.header_cont_rect), # self.__area['header']['inner']
                'bottom-incl':  (self.body_size,    self.body_rect[:2],   self.body_rect),                   # self.__area['body']['full']
                'bottom-excl':  (self.body_cont_size,  self.body_cont_rect[:2],  self.body_cont_rect),       # self.__area['body']['inner']
                'left-incl':    ((20,20),           (10,10)), #,               (10,10,30,30)),       # undefined?
                'left-excl':    ((20,20),           (10,10)), #,               (10,10,30,30)),       # undefined?
                'right-incl':   ((20,20),           (10,10)), #,               (10,10,30,30)),       # undefined?
                'right-excl':   ((20,20),           (10,10)), #,               (10,10,30,30)),       # undefined?
                },
            'header': {
                'full':         (self.header_size,       self.header_rect[:2],       self.header_rect),
                'inner':        (self.header_cont_size,  self.header_cont_rect[:2],  self.header_cont_rect),
                'left-incl':    (self.header_margin_left_inclusive_size,    self.header_margin_left_inclusive[:2],    self.header_margin_left_inclusive),
                'left-excl':    (self.header_margin_left_exclusive_size,    self.header_margin_left_exclusive[:2],    self.header_margin_left_exclusive),
                'right-incl':   (self.header_margin_right_inclusive_size,   self.header_margin_right_inclusive[:2],   self.header_margin_right_inclusive),
                'right-excl':   (self.header_margin_right_exclusive_size,   self.header_margin_right_exclusive[:2],   self.header_margin_right_exclusive),
                'top-incl':     (self.header_margin_top_inclusive_size,     self.header_margin_top_inclusive[:2],     self.header_margin_top_inclusive),
                'top-excl':     (self.header_margin_top_exclusive_size,     self.header_margin_top_exclusive[:2],     self.header_margin_top_exclusive),
                'bottom-incl':  (self.header_margin_bottom_inclusive_size,  self.header_margin_bottom_inclusive[:2],  self.header_margin_bottom_inclusive),
                'bottom-excl':  (self.header_margin_bottom_exclusive_size,  self.header_margin_bottom_exclusive[:2],  self.header_margin_bottom_exclusive),
                },
            'body': {
                'full':         (self.body_size,       self.body_rect[:2],       self.body_rect),
                'inner':        (self.body_cont_size,  self.body_cont_rect[:2],  self.body_cont_rect),
                'left-incl':    (self.body_margin_left_inclusive_size,    self.body_margin_left_inclusive[:2],    self.body_margin_left_inclusive),
                'left-excl':    (self.body_margin_left_exclusive_size,    self.body_margin_left_exclusive[:2],    self.body_margin_left_exclusive),
                'right-incl':   (self.body_margin_right_inclusive_size,   self.body_margin_right_inclusive[:2],   self.body_margin_right_inclusive),
                'right-excl':   (self.body_margin_right_exclusive_size,   self.body_margin_right_exclusive[:2],   self.body_margin_right_exclusive),
                'top-incl':     (self.body_margin_top_inclusive_size,     self.body_margin_top_inclusive[:2],     self.body_margin_top_inclusive),
                'top-excl':     (self.body_margin_top_exclusive_size,     self.body_margin_top_exclusive[:2],     self.body_margin_top_exclusive),
                'bottom-incl':  (self.body_margin_bottom_inclusive_size,  self.body_margin_bottom_inclusive[:2],  self.body_margin_bottom_inclusive),
                'bottom-excl':  (self.body_margin_bottom_exclusive_size,  self.body_margin_bottom_exclusive[:2],  self.body_margin_bottom_exclusive),
                },
            '__EMERGENCY': {},
        }

        # generate the above commented dictionnary entries
        #for part in ['header','body']:
        #    for region in ['left','right','top','bottom']:
        #        for i in [('incl', 'inclusive'), ('excl', 'exclusive')]:
        #            exec("self.__area['{0}']['{1}-{2}'] = (self.{0}_margin_{1}_{3}_size, self.{0}_margin_{1}_{3}[:2], self.{0}_margin_{1}_{3})".format(
        #                part, region, i[0], i[1],
        #                ))
        # Initially the __area attribute was created using the property decorator as such:
        #       @property
        #       def __area(self):
        #           a = { ... }
        #           return a
        # I did it that way because I simply didn't know better. As I digged deeper into deocrators I restructured my code
        # a bit in order to do this more properly. The goal was to dynamically update the dictionnary without doing it
        # manually, simply by changing the value of the 'include_margins' attribute. As you can see, now the 'include_margins'
        # attribute is created using the property decorator and the __area attribute is created within the __init__() method.
        # For some reason though, after making this change, I will get an error while doing the 'exec("self.__area...)'
        # instructions. Here is the error message:
        #       AttributeError: 'Background' object has no attribute '__area'
        # Strangely enough, it works just fine when I type out the code and don't try to genereate it that way. I am aware of
        # the fact that generating code this way isn't advised but I was just having fun with it and trying stuff out ;)


    # set this attribute to determine whether margins
    # are included or not
    @property
    def include_margins(self):
        return self._include_margins
    @include_margins.setter
    def include_margins(self, switch):
        def message(mes):
            if self.__silent_include is False:
                print(mes)
            return None

        self._include_margins = switch
        in_or_ex = ''
        if switch is True:
            in_or_ex = 'incl'
            message("Including margins === '{}'".format(self.image_name))
        else:
            in_or_ex = 'excl'
            message("Excluding margins === '{}'".format(self.image_name))

        # generate and execute the below commented code
        #for part in ['full','header','body']:
        #    for region in ['left','right','top','bottom']:
        #        exec("self.__area['{0}']['{1}'] = self.__area['{0}']['{1}-{2}']".format(part, region, in_or_ex))
        self.__area['full']['left']     = self.__area['full']['left-'+in_or_ex]
        self.__area['full']['right']    = self.__area['full']['right-'+in_or_ex]
        self.__area['full']['top']      = self.__area['full']['top-'+in_or_ex]
        self.__area['full']['bottom']   = self.__area['full']['bottom-'+in_or_ex]
        self.__area['header']['left']   = self.__area['header']['left-'+in_or_ex]
        self.__area['header']['right']  = self.__area['header']['right-'+in_or_ex]
        self.__area['header']['top']    = self.__area['header']['top-'+in_or_ex]
        self.__area['header']['bottom'] = self.__area['header']['bottom-'+in_or_ex]
        self.__area['body']['left']     = self.__area['body']['left-'+in_or_ex]
        self.__area['body']['right']    = self.__area['body']['right-'+in_or_ex]
        self.__area['body']['top']      = self.__area['body']['top-'+in_or_ex]
        self.__area['body']['bottom']   = self.__area['body']['bottom-'+in_or_ex]


    @classmethod
    def save_to(cls, *location):
        cls.save_location = eval('os.path.join({})'.format(str(location)[1:-1]))
        print("Save location for all further images: {}".format(cls.save_location))


    def __area_check(self, part, region):
        """Verify whether input is valid."""
        self.__silent_include = True
        self.margins()  # make sure 'left', 'right', etc. works.
        self.margins()  # There was a bug where it didn't work properly
        self.__silent_include = False

        area_check = self.__area.copy()
        del area_check['__EMERGENCY']
        if part not in area_check.keys():
            print("Undefined part of the image specified:", part)
            part = 'full'
        if region not in area_check['full'].keys():
            print("Undefined region of the image part specified:", region)
            region = 'full'
        del area_check
        return part, region

    def __message(self, operator, operation, part, region):
        """Output message on what is being done."""
        print("{:7} applied: {:11} on {:9} {:14} === {} ".format(operator, "'"+operation+"'", "'"+part+"'", "'"+region+"'" , self.image_name))

    def __try_open_image(self, image, part, region):
        """Try to open a given image."""
        try:
            image = Image.open(image) # open given file
            operation = 'image'
        except (FileNotFoundError, AttributeError) as e:
            image = Image.new('RGBA', self.__area[part][region][0], (255,0,255,230))
            operation = '??image??'
        return image, operation

    def __paste_image(self, canvas, image, part='full', region='full', coords=None):
        """paste a given image onto the canvas."""
        paste_im =       lambda im, coord: im.paste(image, coord)        # paste w/o transparency
        paste_im_alpha = lambda im, coord: im.paste(image, coord, image) # paste w/ transparency
        if image.mode == 'RGB':
            if coords is not None:
                paste_im(canvas, coords)
            else:
                paste_im(canvas, self.__area[part][region][1])
        elif image.mode == 'RGBA':
            if coords is not None:
                paste_im_alpha(canvas, coords)
            else:
                paste_im_alpha(canvas, self.__area[part][region][1])
        else:
            print("Undefined situation. Image mode: ", image.mode)
        return None


    def filter(self, operation='blur', part='full', region='full',  value=6):
        """Do some fancy stuff with your images.

        If you want to add multiple filters, you will have to use this
        method multiple times in a row.
        """

        Filter_options = {
                None:        lambda image: image.filter(ImageFilter.GaussianBlur(0)),
                'raw':       lambda image: image.filter(ImageFilter.GaussianBlur(0)),
                'blur':      lambda image: image.filter(ImageFilter.GaussianBlur(int(value))),
                'maxFilter': lambda image: image.filter(ImageFilter.MaxFilter(3)),
                'minFilter': lambda image: image.filter(ImageFilter.MinFilter(3)),
        }

        part, region = self.__area_check(part,region)

        if operation not in Filter_options:
            print("INVALID operation:  %s. Setting to 'None'." % operation)
            operation = None

        if operation == 'raw':
            cropped = self.__imco.crop(self.__area[part][region][2])
        else:
            cropped = self.im_obj.crop(self.__area[part][region][2])
        filtered = Filter_options[operation](cropped)
        self.im_obj.paste(filtered, self.__area[part][region][1])

        if operation is None:
            operation = 'None'

        self.__message('Filter',operation, part, region)
        return None

    def overlay(self, ov_image='blank', part='full', region='full'):
        """Overlay to lower the contrast or make the image more interesting.

        If you want to add multiple overlays, you will have to use
        this method multiple times in a row.

        You can either give an image as input or a tuple with RGB or
        RGBA values to overlay a evenly colored image.
        """

        part, region = self.__area_check(part,region)

        if ov_image == 'blank':
            ov_image = Image.new('RGBA', self.__area[part][region][0], (150,150,150,150))
            operation = 'blank'
        elif type(ov_image) is tuple:
            if len(ov_image) < 3 or len(ov_image) > 4:
                # check whehter tuble is valid
                print("INVALID tuple given: ", ov_image)
                ov_image = Image.new('RGBA', self.__area[part][region][0], (220,255,120,230))
                operation = 'ERROR'
            else:
                ov_image = Image.new('RGBA', self.__area[part][region][0], ov_image)
                operation = 'color'
        else:
            ov_image, operation = self.__try_open_image(ov_image, part, region)

        self.__paste_image(self.im_obj, ov_image, part, region)
        self.__message('Overlay', operation, part, region)
        return None

    def image(self, picture=None, part='full', region='full', borders=True, anchor=None, transparency=255):
        """This method provides a few more options for overlaying images.

        You can very well overlay images with the 'overlay' method, but there the images
        are simply being put ontop of the image. If the image you give as input is larger
        than the desired area, then the image will exceed the boundarys.

        Here you don't have to hand tailor your image to fit into the area, instead this
        method crops the image for you if you like. You can also set an anchor for the
        image's upper left corner. This way you can 'move the image around' inside your
        area, but ONLY if 'borders' is set to 'True'.

        BE AWARE that if the upper left corner is inside your area then the area will
        not be filled completely, but instead there might be space to the left or to the
        top of the area. The extrem case would be if you move the anchor farther than the
        right or bottom side of the area. In this case, the image will not even be
        visible at all.
        """

        part ,region = self.__area_check(part, region)
        empty_alpha = Image.new('L', (self.width, self.height), (0,0,0,0))

        if picture is None:
            print("No image specified.")
            picture = empty_alpha
        else:
            picture, operation = self.__try_open_image(picture, part, region)

        image_copy = self.im_obj.copy()  # make a copy to work on

        if transparency < 255 and picture.mode != 'RGBA':
            # make the image transparent
            picture.putalpha(empty_alpha)
            empty_alpha = empty_alpha.convert(mode='RGBA')
            picture = Image.blend(picture, empty_alpha, 0.5)

        if borders == True:
            if anchor is None:
                self.__paste_image(image_copy, picture, part, region)
                operation = 'crop'
            else:
                self.__paste_image(image_copy, picture, coords=anchor)  # paste picture onto copy
                operation = 'anchor'
            cropped = image_copy.crop(self.__area[part][region][2])  # crop copy at desired area
            self.__paste_image(self.im_obj, cropped, part, region)   # put everything together
        elif borders == False:
            self.__paste_image(self.im_obj, picture, part, region)
            operation = 'paste'
        else:
            print("INVALID borders specification: ", borders)

        self.__message('Image', operation, part, region)
        return None

    def margins(self, switch=None):
        """Toggle whether margins are included or excluded.

        By default margins are included. Use this method to toggle between
        including and excluding margins. Alternatively you could also set
        the 'include_margins' attribute to 'True' or 'False' which would
        have the same effect. Though 'include_margins' is probalby harder
        to remember and dirtier than 'marings'.
        """

        if switch is True:
            self.include_margins = True
        elif switch is False:
            self.include_margins = False
        elif switch == 'return':
            return self.include_margins
        elif switch is None:
            if self.include_margins is True:
                self.include_margins = False
            else:
                self.include_margins = True
        else:
            print("INVALID input for margins: ", switch)
        return None


    def dimensions(self, part='full', region='full'):
        """Return the size of the specified area."""

        part, region = self.__area_check(part, region)
        return self.__area[part][region][:2]

    def show(self):
        "Get a preview of the image."
        self.im_obj.show()
        return None

    def save(self, name=None, *location):
        "Save the image."

        if Background.save_location == '':
            im_path = os.path.split(name)[0]  # retrieved from 'name' argument
        else:
            im_path = Background.save_location
        im_name = os.path.split(name)[1]  # retrieved from 'name' argument
        im_format = im_name.split('.')[-1]
        cwd = os.getcwd()

        # verify path input
        if len(location) != 0 and im_path != '':
            # location and im_path are given
            print("TOO MANY paths were given:\n {}, {}".format(im_path, eval('os.path.join({})'.format(str(location)[1:-1]))))
            print("Skipping save. '{}' has NOT been saved.".format(self.image_name))
            return
        elif len(location) == 0 and im_path == '':
            # no location given and no im_path given
            path = os.getcwd()
        elif len(location) != 0 and im_path == '':
            # location is given but no im_path
            path = eval('os.path.join({})'.format(str(location)[1:-1]))  # is there a work around?
            #path_loc = str(location)[1:-1]                              # because this doesn't seem to work ...
            #print('path_loc: ', path_loc)
            #path = os.path.join(path_loc)
            #print('path: ', path)
            if os.path.exists(path):
                os.chdir(path)
            else:
                print("INVALID location: ", path)
                print("Skipping save. '{}' has NOT been saved.".format(self.image_name))
                return
        elif len(location) == 0 and im_path != '':
            # im_path is given but no location
            path = im_path
            if os.path.exists(path):
                os.chdir(path)
            else:
                print("INVALID path: ", path)
                print("Skipping save. '{}' has NOT been saved.".format(self.image_name))
                return

        # verify image_format input
        if im_format == 'jpg':
            im_format = 'jpeg'

        # prepend processed tag
        if name is None:
            im_name = "pbc-{}".format(self.image_name)
        else:
            im_name = "pbc-{}".format(im_name)

        # save image
        if im_format is None:
            self.im_obj.save(im_name)
        else:
            self.im_obj.save(im_name, im_format)

        os.chdir(cwd)
        print("'{}' saved as '{}' to '{}'".format(self.image_name, im_name, path))

        return None
