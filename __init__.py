from .download_images import register, unregister, classes

bl_info = {
    "name": "Image Downloader",
    "description": "Downloads Images from Links and Packs them into your .blend",
    "author": "Mantelmann",
    "version": (0, 1, 0),
    "blender": (3, 3, 0),
    "location": "3D View > Create",
    "category": "Object",
}


if __name__ == "__main__":
    register()
