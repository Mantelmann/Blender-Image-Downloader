bl_info = {
    "name": "Image Downloader",
    "description": "Downloads Images from Links and Packs them into your .blend",
    "author": "Mantelmann",
    "version": (0, 0, 1),
    "blender": (2, 91, 0),
    "location": "3D View > Tool",
    "category": "Import-Export",
    "internet": "https://github.com/Mantelmann"
}


import bpy

from bpy.props import (StringProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
import requests
import shutil
import tempfile

#PRAISE BE
#https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c

def download_and_pack(url):

    file_name = url.split("?")[0].split("/")[-1]

    try:
        r = requests.get(url, stream = True)
    except:
        print(f"Image Downloader: Unable to open URL")
        return None, None
        
    if r.status_code == 200:
        r.raw.decode_content = True
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            
            #Very disgusting, probably stupid.
            slash_type = "/"
            if tmpdirname[0] != "/":
                slash_type = "\\"
                
            file_path = tmpdirname + slash_type + file_name
            
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            
            img = bpy.data.images.load(file_path)
            img.pack()
        
        print(f"Image Downloader: Successfully Downloaded {file_name}")
        
        
        return img, file_name

    else:
        
        print(f"Image Downloader: Unable to Download {file_name}: requests gives Error code {r.status_code}")
        
        return None, None
    
    
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

def create_image_material(obj, image, name):
    #PRAISE BE
    #https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8
    
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    
    bsdf = material.node_tree.nodes["Principled BSDF"]
    texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = image
    texImage.location = (-250,250)
    material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    
    obj.data.materials.append(material)


def main(context, url):
    
    image, name = download_and_pack(url)
    
    if image == None or name == None:
        return {'ERROR'}

    obj = create_image_plane(context, image)
    obj.name = name

    create_image_material(obj, image, name)
    
    return {'FINISHED'}
    

class nbProperties(PropertyGroup):
    
    image_link: bpy.props.StringProperty(
        name = "Image Link",
        description = "Direct Link to Image"
    )

class WM_OT_download_image(Operator):
    bl_label = "Download Image"
    bl_description = "Download Image from the given Link"
    bl_info = "Download"
    bl_idname = "wm.download_image"

    def execute(self, context):
        scene = context.scene
        imdo = scene.image_download

        # print the values to the console
        if imdo.image_link != "":
            returned = main(context, imdo.image_link)

        if returned == {'FINISHED'}:
            imdo.image_link = ""

        return {'FINISHED'}


class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Download Image"
    bl_idname = "OBJECT_PT_image_download_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tool"
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
        layout.operator("wm.download_image")


#https://theglorioblog.files.wordpress.com/2019/10/ascendanceofabookworm2.jpg?w=700&h=394


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
    del bpy.types.Scene.imdo


if __name__ == "__main__":
    register()