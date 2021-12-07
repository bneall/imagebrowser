#
# Conversion: OIIO
#

def run(tp, size):

    import os
    from subprocess import Popen, PIPE

    convert_cmd = 'oiiotool "%s" --resize %sx0 -o "%s"' % (tp.sourcePath, size, tp.thumbnailPath)

    # Assume EXR Linear
    if tp.sourceExt == 'exr':
        convert_cmd = 'oiiotool "%s" --colorconvert linear sRGB --resize %sx0 -o "%s"' % (tp.sourcePath, size, tp.thumbnailPath)
    
    convert_proc = Popen(convert_cmd, universal_newlines=True, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = convert_proc.communicate()
    
    if os.path.exists(tp.thumbnailPath):
        return True
    else:
        return False