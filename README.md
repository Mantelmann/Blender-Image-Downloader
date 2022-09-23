# Blender-Image-Downloader
An Addon which downloads images from links directly into .blend files, no external saving required!

![Reference Images](https://i.imgur.com/h4RnlKR.png)

## Well, that's easy enough.

When you have found a nice image in the internet which you would like to have in your .blend file, copy it's URL and paste it into the `Image Link` input. Give the image a name if you want to, and decide whether to use the images alpha channel (enabling Eevee Blend modes is included!), and you get your image downloaded without any extra saving steps inbetween.

The downloaded image is packed directly into your file, so it won't get lost when you move the file. You also don't need to keep up directories of random downloaded images. No clutter!

## One Technical Detail

Only images are supported for now. The MIME-type of the request is checked to be an image, otherwise no object or material will get created. Videos or image sequences aren't downloadable.
