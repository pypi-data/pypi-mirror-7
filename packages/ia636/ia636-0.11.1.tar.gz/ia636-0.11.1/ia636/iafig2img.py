# -*- encoding: utf-8 -*-
# Module iafig2img

def iafig2img(figure):
    import numpy

    # draw the renderer
    figure.canvas.draw ( )

    # Get the RGB buffer from the figure
    w,h = figure.canvas.get_width_height()
    buf = numpy.fromstring ( figure.canvas.tostring_rgb(), dtype=numpy.uint8 )
    buf.shape = ( h, w, 3 )

    return buf.transpose((2,0,1))

