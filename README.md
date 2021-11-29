# Mari Image Browser
## About
A simple QT based image browser that allows basic interaction with Mari drag and drop.

>Author: Ben Neall\
>Contact: bneall@gmail.com

## Installation & Requirements
---
Copy package contents to $USER/Mari/Scripts directory.

>Example:
> * ~/Mari/Scripts/mariImageBrowser
> * ~/Mari/Scripts/mariImageBrowser.py

Mari Image Browser has been tested on following:

>* Windows 10
>* Linux CentOS 7

***Note: Mari Image Browser requires Mari 4, however it can be refactored to use the Qt.py shim and work in Mari 3.***



## Usage
---
>Walkthrough Video:\
>https://vimeo.com/350288220

## Features
---
>### Collections
>
>* To add image to collection, drag images onto the collection item in the presets list.
>* You can drag images from mari image manager, mari image browser, or from OS, as long as they exist on disk.
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
>* Import images by dragging them wherever Mari supports drag and drop. For example you can drag into the image manager, or a node's image input slot.

## Settings
---
The mari image browser supports concept of primary and secondary thumbnail converter.
When the primary fails, the secondary (if set) will try. If all converters fail, an error image is used.

>The following covert presets are provided:
>* **qt** : default and the fastest, should always be set as primary.
>* **imagemagick** : supports imagemagick 7, install required (https://imagemagick.org)
>* **gragphicsmagick:** supports graphicsmagick syntax, install required (http://www.graphicsmagick.org)
>* **oiio**: supports oiiotool syntax, install required (http://www.openimageio.org)

Settings (including collections and bookmarks) are stored in a config file stored here:
> ~/Mari/mib.conf