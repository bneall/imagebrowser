#
# Conversion: GraphicsMagick
#

def run(tp, size):

    import os
    from subprocess import Popen, PIPE

    convert_cmd = 'gm convert "%s" -background transparent -flatten -resize %sx%s -depth 8 -format %s "%s"' % (tp.sourcePath, size, size, tp.thumbnailExt, tp.thumbnailPath)
    convert_proc = Popen(convert_cmd, universal_newlines=True, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = convert_proc.communicate()

    if os.path.exists(tp.thumbnailPath):
        return True
    else:
        return False