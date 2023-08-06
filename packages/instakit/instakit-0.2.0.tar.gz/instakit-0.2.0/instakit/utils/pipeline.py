
from collections import defaultdict
from PIL import Image
from PIL import ImageMode

class Pipe(list):
    """ A linear pipeline of processors to be applied en masse.
        Derived from an ImageKit class:
        imagekit.processors.base.ProcessorPipeline
    """
    def process(self, img):
        for p in self:
            img = p.process(img)
        return img

class NOOp(object):
    """ A no-op processor. """
    def process(self, img):
        return img

class ChannelFork(defaultdict):
    """ A processor wrapper that, for each image channel:
        - applies a channel-specific processor, or
        - applies a default processor.
        
        * Ex. 1: apply the Atkinson ditherer to each of an images' channels:
        >>> from instakit.utils.pipeline import ChannelFork
        >>> from instakit.processors.halftone import Atkinson
        >>> ChannelFork(Atkinson).process(my_image)
        
        * Ex. 2: apply the Atkinson ditherer to only one channel:
        >>> from instakit.utils.pipeline import ChannelFork
        >>> from instakit.processors.halftone import Atkinson
        >>> cfork = ChannelFork(None)
        >>> cfork['G'] = Atkinson()
        >>> cfork.process(my_image)
    """
    
    default_mode = 'RGB'
    
    def __init__(self, default_factory, *args, **kwargs):
        if default_factory is None:
            default_factory = NOOp
        if not callable(default_factory):
            raise AttributeError(
                "ChannelFork() requires a callable default_factory.")
        
        self.channels = ImageMode.getmode(
            kwargs.pop('mode', self.default_mode))
        
        super(ChannelFork, self).__init__(default_factory, *args, **kwargs)
    
    def __setitem__(self, idx, value):
        if value in (None, NOOp):
            value = NOOp()
        super(ChannelFork, self).__setitem__(idx, value)
    
    @property
    def mode(self):
        return self.channels.mode
    
    @mode.setter
    def mode(self, mode_string):
        self._set_mode(mode_string)
    
    def _set_mode(self, mode_string):
        self.channels = ImageMode.getmode(mode_string)
    
    def compose(self, *channels):
        return Image.merge(
            self.channels.mode,
            channels)
    
    def process(self, img):
        if img.mode != self.channels.mode:
            img = img.convert(self.channels.mode)
        
        processed_channels = []
        for idx, channel in enumerate(img.split()):
            processed_channels.append(
                self[self.channels.bands[idx]].process(channel))
        
        return self.compose(*processed_channels)

class CMYKInk(object):
    """ Renders an input L-mode image,
        by simulating a CMYK primary ink color.
    """
    
    WHITE =     (255,   255,    255)
    CYAN =      (0,     250,    250)
    MAGENTA =   (250,   0,      250)
    YELLOW =    (250,   250,    0)
    KEY =       (0,     0,      0)
    CMYK =      (CYAN, MAGENTA, YELLOW, KEY)
    
    def __init__(self, ink_value=None):
        if ink_value is None:
            ink_value = self.KEY
        self.ink_value = ink_value
    
    def process(self, img):
        from PIL import ImageOps
        return ImageOps.colorize(
            img.convert('L'),
            self.WHITE,
            self.ink_value)


class ChannelOverprinter(ChannelFork):
    """ A ChannelFork subclass that rebuilds its output image using
        multiply-mode to simulate CMYK overprinting effects.
    """
    default_mode = 'CMYK'
    
    def _set_mode(self, mode_string):
        if mode_string != self.default_mode:
            raise AttributeError(
                "ChannelOverprinter can operate in %s mode only" %
                    self.default_mode)
    
    def compose(self, *channels):
        from PIL import ImageChops
        return reduce(ImageChops.multiply, channels)
    
    def process(self, img):
        inks = zip(self.default_mode,
            [CMYKInk(ink_label) \
                for ink_label in CMYKInk.CMYK])
        
        clone = ChannelOverprinter(
            self.default_factory,
            mode=self.channels.mode)
        
        for channel_name, ink in inks:
            clone[channel_name] = Pipe([
                self[channel_name], ink])
        
        return super(ChannelOverprinter, clone).process(img)




if __name__ == '__main__':
    from instakit.utils import static
    from instakit.processors.halftone import Atkinson
    
    image_paths = map(
        lambda image_file: static.path('img', image_file),
            static.listfiles('img'))
    image_inputs = map(
        lambda image_path: Image.open(image_path).convert('RGB'),
            image_paths)
    
    for image_input in image_inputs[:2]:
        #ChannelOverprinter(Atkinson).process(image_input).show()
        
        print 'Creating ChannelOverprinter and ChannelFork with Atkinson ditherer...'
        overatkins = ChannelOverprinter(Atkinson)
        forkatkins = ChannelFork(Atkinson)
        '''
        print 'Processing image with ChannelForked Atkinson in default (RGB) mode...'
        forkatkins.process(image_input).show()
        forkatkins.mode = 'CMYK'
        print 'Processing image with ChannelForked Atkinson in CMYK mode...'
        forkatkins.process(image_input).show()
        forkatkins.mode = 'RGB'
        print 'Processing image with ChannelForked Atkinson in RGB mode...'
        forkatkins.process(image_input).show()
        '''
        overatkins.mode = 'CMYK'
        print 'Processing image with ChannelOverprinter-ized Atkinson in CMYK mode...'
        overatkins.process(image_input).show()
        
        print 'Attempting to reset ChannelOverprinter to RGB mode...'
        import traceback, sys
        try:
            overatkins.mode = 'RGB'
            overatkins.process(image_input).show()
        except:
            print ">>>>>>>>>>>>>>>>>>>>> TRACEBACK <<<<<<<<<<<<<<<<<<<<<"
            traceback.print_exc(file=sys.stdout)
            print "<<<<<<<<<<<<<<<<<<<<< KCABECART >>>>>>>>>>>>>>>>>>>>>"
            print ''
    
    print image_paths
    
