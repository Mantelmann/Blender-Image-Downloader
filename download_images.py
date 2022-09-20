bl_info = {
    "name": "Image Downloader",
    "description": "Downloads Images from Links and Packs them into your .blend",
    "author": "Mantelmann",
    "version": (0, 1, 0),
    "blender": (3, 3, 0),
    "location": "3D View > Create",
    "category": "Import-Export",
    "internet": "https://github.com/Mantelmann"
}


import bpy

from bpy.props import StringProperty, BoolProperty, PointerProperty

from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
import os
import requests
import shutil
import tempfile

#PRAISE BE
#https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c

def download_and_pack(url, custom_name=None):

    file_name = url.split("?")[0].split("/")[-1]

    try:
        r = requests.get(url.strip(), stream = True)
    except:
        return None, None, f"Image Downloader: Unable to open URL '{url}'"
        
    if r.status_code != 200:
        return None, None, f"Image Downloader: Unable to Download {file_name}: requests gives Error code {r.status_code}"

    if not r.headers["Content-Type"].startswith("image"):
        return None, None, f"Image Downloader: URL with Mimetype '{r.headers['Content-Type']}' doesn't appear to be an image"


    r.raw.decode_content = True
    
    tmpfile = tempfile.NamedTemporaryFile(prefix="blender_image_downloader_", suffix="_" + file_name)
    
    with open(tmpfile.name, "wb") as f:
        shutil.copyfileobj(r.raw, f)
        
    img = bpy.data.images.load(tmpfile.name)
    img.name = custom_name or file_name
    img.pack()
    
    return img, img.name, f"Image Downloader: Successfully Downloaded {file_name}"

    
    
def create_image_plane(context, image):
    
    width, height = image.size
    
    if width == height:
        scale = (1,1,1)
    elif width < height:
        scale = (width/height, 1,1)
    elif width > height:
        scale = (1, height/width, 1)

    bpy.ops.mesh.primitive_plane_add()
    obj = context.active_object
    
    obj.scale = scale
    
    return obj

def create_image_material(obj, image, name, use_alpha):
    #PRAISE BE
    #https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8
    
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    
    bsdf = material.node_tree.nodes["Principled BSDF"]
    texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = image
    texImage.location = (-350,250)
    material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    
    if use_alpha:
        material.node_tree.links.new(bsdf.inputs['Alpha'], texImage.outputs['Alpha'])
        material.blend_method = "BLEND"
        material.shadow_method = "CLIP"
    
    obj.data.materials.append(material)


def main(context, url, use_alpha, custom_name=None):
    
    image, name, message = download_and_pack(url, custom_name=custom_name)
    
    if image == None or name == None:
        return {'ERROR'}, message

    obj = create_image_plane(context, image)
    obj.name = name

    create_image_material(obj, image, name, use_alpha)
    
    return {'INFO'}, message
    

class nbProperties(PropertyGroup):
    
    image_link: StringProperty(
        name = "Image Link",
        description = "Direct Link to Image"
    )
    custom_name: StringProperty(
        name = "Custom Name",
        description = "Custom Name for image instead of URL name. Optional."
    )
    use_alpha: BoolProperty(
        name = "Use Alpha",
        description = "Sets whether the Alpha Output of the Image shall be used in the generated Material."
    )

class WM_OT_download_image(Operator):
    bl_label = "Download Image"
    bl_description = "Download Image from the given Link"
    bl_info = "Download"
    bl_idname = "wm.download_image"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene
        imdo = scene.image_download
        
        if imdo.image_link == "":
            return {'FINISHED'}

        returned, message = main(context, imdo.image_link, imdo.use_alpha, custom_name=imdo.custom_name if imdo.custom_name!="" else None)
            
        self.report(returned, message)
        
        # No Errors, so clear Link and Name
        if returned == {'INFO'}:
            imdo.image_link = ""
            imdo.custom_name = ""

        return {'FINISHED'}


class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Download Image"
    bl_idname = "OBJECT_PT_image_download_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Create"
    bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        imdo = scene.image_download
        layout.separator()
        layout.prop(imdo, "image_link")
        layout.prop(imdo, "custom_name")
        layout.prop(imdo, "use_alpha")
        layout.separator()
        layout.operator("wm.download_image")


classes = (
    nbProperties,
    WM_OT_download_image,
    OBJECT_PT_CustomPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

    bpy.types.Scene.image_download = PointerProperty(type=nbProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.image_download


if __name__ == "__main__":
    register()
