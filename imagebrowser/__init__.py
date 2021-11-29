#
# IBView Init
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

import os

import config
import utils

# Main Config Object
cfg = config.Config()

# Setup Constants
IB_CONVERTERMAP = utils.getConverterPlugins(cfg.converterPath)
IB_STYLESHEET = utils.getStyleSheet(cfg.resourcePath)
IB_FORMATS = ['png', 'jpg', 'jpeg', 'exr', 'tiff', 'tif']

# Force update configs converters
# to keep in step with converters available on disk.
cfg.set_converters(IB_CONVERTERMAP.keys())