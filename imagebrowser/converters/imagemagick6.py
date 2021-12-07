#
# Conversion: ImageMagick
#

def run(tp, size):

    import os
    from subprocess import Popen, PIPE

    convert_cmd = 'convert "%s" -background transparent -layers merge -resize %sx%s -depth 8 -format %s "%s"' % (tp.sourcePath, size, size, tp.thumbnailExt, tp.thumbnailPath)
    
    # Assume EXR Linear
    if tp.sourceExt == 'exr':
        convert_cmd = 'convert "%s" -colorspace RGB -background transparent -layers merge -resize %sx%s -depth 8 -format %s -colorspace sRGB "%s"' % (tp.sourcePath, size, size, tp.thumbnailExt, tp.thumbnailPath)
    
    convert_proc = Popen(convert_cmd, universal_newlines=True, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = convert_proc.communicate()

    if os.path.exists(tp.thumbnailPath):
        return True
    else:
        return False