# Beynim3D Multi-Camera Manager
# Copyright (c) 2025 beynim3d
# Licensed under the MIT License - see LICENSE file for details.

import bpy

# === KAMERA GEÇİŞİ ===
def set_camera_by_index(index):
    cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
    if not cams:
        print("No cameras in scene.")
        return
    index = index % len(cams)
    bpy.context.scene.camera = cams[index]
    bpy.context.view_layer.objects.active = cams[index]
    print(f"Switched to camera: {cams[index].name}")

def get_camera_index(cam):
    cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
    return cams.index(cam) if cam in cams else 0

# === OPERATORS ===
class CAMERA_OT_add(bpy.types.Operator):
    """Yeni kamera oluştur"""
    bl_idname = "camera.add_custom"
    bl_label = "Yeni Kamera Ekle"

    def execute(self, context):
        bpy.ops.object.camera_add(align='VIEW')
        cam = context.active_object
        cam.name = f"Camera_{len([c for c in bpy.data.objects if c.type == 'CAMERA'])}"
        context.scene.camera = cam
        return {'FINISHED'}

class CAMERA_OT_remove(bpy.types.Operator):
    """Seçili kamerayı sil"""
    bl_idname = "camera.remove_custom"
    bl_label = "Kamerayı Sil"

    def execute(self, context):
        cam = context.scene.camera
        if cam and cam.type == 'CAMERA':
            bpy.data.objects.remove(cam, do_unlink=True)
        return {'FINISHED'}

class CAMERA_OT_next(bpy.types.Operator):
    """Bir sonraki kameraya geç"""
    bl_idname = "camera.next"
    bl_label = "Sonraki Kamera"

    def execute(self, context):
        cam = context.scene.camera
        cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        if not cams:
            return {'CANCELLED'}
        i = get_camera_index(cam)
        set_camera_by_index(i + 1)
        return {'FINISHED'}

class CAMERA_OT_prev(bpy.types.Operator):
    """Bir önceki kameraya geç"""
    bl_idname = "camera.prev"
    bl_label = "Önceki Kamera"

    def execute(self, context):
        cam = context.scene.camera
        cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        if not cams:
            return {'CANCELLED'}
        i = get_camera_index(cam)
        set_camera_by_index(i - 1)
        return {'FINISHED'}

# === PANEL ===
class VIEW3D_PT_camera_manager(bpy.types.Panel):
    bl_label = "Multi-Camera Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']

        row = layout.row()
        row.operator("camera.add_custom", icon='ADD')
        row.operator("camera.remove_custom", icon='TRASH')

        layout.separator()
        layout.label(text="Kameralar:")

        for i, cam in enumerate(cams):
            box = layout.box()
            row = box.row()
            row.prop(cam, "name", text=f"{i+1}.")
            op = row.operator("camera.switch_to", text="Aktif Yap")
            op.index = i

            col = box.column(align=True)
            col.prop(cam, "location")
            col.prop(cam, "rotation_euler", text="Rotation")
            col.prop(cam.data, "lens", text="Lens (mm)")

class CAMERA_OT_switch_to(bpy.types.Operator):
    bl_idname = "camera.switch_to"
    bl_label = "Kameraya Geç"
    index: bpy.props.IntProperty()

    def execute(self, context):
        set_camera_by_index(self.index)
        return {'FINISHED'}

# === KISAYOLLAR ===
addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')

        # Kamera geçişi
        km.keymap_items.new("camera.prev", 'LEFT_ARROW', 'PRESS', ctrl=True, shift=True)
        km.keymap_items.new("camera.next", 'RIGHT_ARROW', 'PRESS', ctrl=True, shift=True)
        # Yeni kamera
        km.keymap_items.new("camera.add_custom", 'N', 'PRESS', ctrl=True, shift=True)
        # Kamera sil
        km.keymap_items.new("camera.remove_custom", 'W', 'PRESS', ctrl=True, shift=True)

        # 1-9 arasında doğrudan geçiş
        key_names = ["ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","ZERO"]
        for i, key in enumerate(key_names):
            kmi = km.keymap_items.new("camera.switch_to", key, 'PRESS', ctrl=True, shift=True)
            kmi.properties.index = i
            addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()

# === REGISTER ===
classes = (
    CAMERA_OT_add,
    CAMERA_OT_remove,
    CAMERA_OT_next,
    CAMERA_OT_prev,
    CAMERA_OT_switch_to,
    VIEW3D_PT_camera_manager,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()

def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass

if __name__ == "__main__":
    unregister()
    register()
