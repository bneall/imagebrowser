# Image Browser
## About
Image Browser is a simple QT based image browser that provides some basic features.

>Author: Ben Neall<br>
>Contact: bneall@gmail.com

## Installation & Requirements
---
***Image Browser requires Qt5, but can run in Qt4 when refactored (replace PySide2 imports with Qt) to use the Qt.py shim.***<br>
***Because PySide2 is not readily available for Python2.7, it is recommened to use Qt.py shim for maximum compatibility (also required to use in standalone mode)***<br>

>Installation varies for each application:
>
>1. Copy the contents of the package to application's script directory.
>2. Find and view the python file in the revelant application install directory: /imagebrowser/install/$application and follow the instructions.
>
>**Mari Quick Install Guide**
>>Copy the contents of the plugin to mari scripts folder: "\~/Mari/Scripts/imagebrowser"<br>
>>Then copy the init file into the same mari scripts folder: "\~/Mari/Scripts/mari_imagebrowser_init.py"<br>
>
>Alternatively, you can install the imagebrowser module in an arbitrary location and add path to the PYTHONPATH and build your own init solution.

 <br>

## Thumbnail files
---
> Thumbnails are stored in **\~/imagebrowsercache** by default, so Windows or Linux you will find it in your "Home" user directory.<br>
> If you wish to move your thumbnail cache, simply copy paste the thumbcache folder to a new location, and in the plugin's preferences, change the cache location to the new path.
>
>> It is **HIGHLY** recommended that you download and install the **imagemagick** library to greatly increase the file fomrat support for thumbnails, see below for converter information.
>
> If you have multiple users, you can create a network path for this cache and have all users point to it, this will speed up thumbnail creation and allow for faster browsing.

 <br>

## Usage
---
>Walkthrough Video:<br>
>https://vimeo.com/350288220

 <br>

## Features
---
>### Collections
>
>* To add images to a collection, drag them onto the collection item in the presets list.
>* You can drag images from any location, as long as they are using standard MIME type.
>* Import and export collections as json file format using the export/import buttons on the toolbar.
>> **Tips:**
>> * The "Delete" key prompts removal of selected items from collection.
>> * To return to the directory you are currently in after activating a collection view, simply doubleclick the collection item a second time.
>
>### Bookmarks
>
>* The add bookmark button bookmarks the current directory.
>* The home bookmark is persistant and always points to your users home area.
>
>### Browsing
>* The path field supports auto complete for file browser.
>
>### Importing
>* Import images by dragging them wherever the application supports drag and drop. For example you can drag into the Mari image manager, or a node's image input slot.
>* Additionally, for Mari you can drag and drop images directly into the node graph.
>* Drag and Drop behavior is expandable, and can be extended to any application's implementation by creating custom inits.

 <br>

## Settings
---
>Settings (including collections and bookmarks) are stored in a config file stored here:
> **\~/ib.conf**<br>
>If you wish to move your config (which stores all your bookmarks and collections), simply copy paste the config file.<br>
>>**NOTE** If you used the previous version of image browser for Mari, make a copy your old config and move it, like this: \~/Mari/Scripts/mib.conf --> \~/ib.conf 
>
>### Converters
>The image browser supports concept of primary and secondary thumbnail converter.
>When the primary fails, the secondary (if set) will try. If all converters fail, an error image is used.
>
>The following covert presets are provided:
>>* **qt** : default and the fastest, should always be set as primary.
>>* **imagemagick** : supports imagemagick 6 and 7, install required (https://imagemagick.org)
>>* **gragphicsmagick:** supports graphicsmagick syntax, install required (http://www.graphicsmagick.org)
>>* **oiio**: supports oiiotool syntax, install required (http://www.openimageio.org)

