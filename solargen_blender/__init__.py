bl_info = {
    "name": "SolarGen",
    "author": "Jaswinder Singh",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "3D Viewport > Sidebar > SolarGen",
    "description": "Procedural solar array generator",
    "category": "Object",
}

import bpy
import os


# ============================================================
# Constants
# ============================================================

CONTROLLER_NAME = "SolarGen_Controller"
NODE_GROUP_NAME = "SolarGen_Generator"
MODIFIER_NAME = "SolarGen"
INTERNAL_COLLECTION_NAME = "SolarGen_Internal"

ADDON_VERSION = "1.0.0"


# ============================================================
# Utility
# ============================================================

def get_asset_file_path():
    addon_folder = os.path.dirname(__file__)

    return os.path.join(
        addon_folder,
        "assets",
        "solargen_assets.blend",
    )


def is_solargen_controller(obj):
    if obj is None:
        return False

    for modifier in obj.modifiers:

        if modifier.type != "NODES":
            continue

        if modifier.node_group is None:
            continue

        if modifier.node_group.name.startswith(NODE_GROUP_NAME):
            return True

    return False


def find_solargen_modifier(obj):
    if obj is None:
        return None

    for modifier in obj.modifiers:

        if modifier.type != "NODES":
            continue

        if modifier.node_group is None:
            continue

        if modifier.node_group.name.startswith(NODE_GROUP_NAME):
            return modifier

    return None


def find_existing_controller(context):
    for obj in context.scene.objects:

        if is_solargen_controller(obj):
            return obj

    return None


def get_internal_collection():
    return bpy.data.collections.get(
        INTERNAL_COLLECTION_NAME
    )


def get_target_collection(context):
    """
    Put new generators in the user's active collection.

    Falls back to the scene's main collection if necessary.
    """

    collection = context.collection

    if collection is None:
        collection = context.scene.collection

    return collection


# ============================================================
# Internal Assets
# ============================================================

def organize_internal_objects(context, objects):

    internal = get_internal_collection()

    if internal is None:

        internal = bpy.data.collections.new(
            INTERNAL_COLLECTION_NAME
        )

        context.scene.collection.children.link(
            internal
        )

    for obj in objects:

        if obj is None:
            continue

        # Never move an actual generator into Internal.
        if is_solargen_controller(obj):
            continue

        if internal not in obj.users_collection:
            internal.objects.link(obj)

        for collection in list(obj.users_collection):

            if collection != internal:
                collection.objects.unlink(obj)

    internal.hide_viewport = True
    internal.hide_render = True

    return internal


def set_internal_visibility(show):

    internal = get_internal_collection()

    if internal is None:
        return False

    internal.hide_viewport = not show
    internal.hide_render = not show

    return True


# ============================================================
# Add Generator
# ============================================================

class SOLARGEN_OT_add_generator(bpy.types.Operator):

    bl_idname = "object.solargen_add_generator"
    bl_label = "Add SolarGen"
    bl_description = "Create a new procedural SolarGen array"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        asset_file = get_asset_file_path()

        if not os.path.exists(asset_file):

            self.report(
                {"ERROR"},
                "SolarGen asset file could not be found.",
            )

            return {"CANCELLED"}

        try:

            # --------------------------------------------------
            # Remember current state
            # --------------------------------------------------

            objects_before = set(bpy.data.objects)

            target_collection = get_target_collection(context)

            # --------------------------------------------------
            # Append a FRESH controller object from the asset
            #
            # Blender may reuse the already-loaded node group,
            # materials and source meshes.
            #
            # We intentionally do NOT Python-copy an existing
            # controller.
            # --------------------------------------------------

            object_directory = os.path.join(
                asset_file,
                "Object",
            )

            bpy.ops.wm.append(
                directory=object_directory,
                filename=CONTROLLER_NAME,
                link=False,
                do_reuse_local_id=True,
                clear_asset_data=True,
                autoselect=False,
            )

            # --------------------------------------------------
            # Determine exactly which objects were imported
            # --------------------------------------------------

            objects_after = set(bpy.data.objects)

            imported_objects = list(
                objects_after - objects_before
            )

            if not imported_objects:

                raise RuntimeError(
                    "SolarGen could not import its controller."
                )

            # --------------------------------------------------
            # Identify the NEW controller
            #
            # First use the Geometry Nodes modifier.
            # If Blender has renamed the node group, startswith()
            # still identifies it.
            # --------------------------------------------------

            controller = None

            for obj in imported_objects:

                if is_solargen_controller(obj):
                    controller = obj
                    break

            # --------------------------------------------------
            # Fallback:
            # find the newly imported object whose name begins
            # with SolarGen_Controller.
            # --------------------------------------------------

            if controller is None:

                for obj in imported_objects:

                    if obj.name.startswith(CONTROLLER_NAME):
                        controller = obj
                        break

            if controller is None:

                raise RuntimeError(
                    "SolarGen controller could not be identified."
                )

            # --------------------------------------------------
            # Organize newly imported dependency objects
            # --------------------------------------------------

            internal_objects = [
                obj
                for obj in imported_objects
                if obj != controller
                and not is_solargen_controller(obj)
            ]

            organize_internal_objects(
                context,
                internal_objects,
            )

            # --------------------------------------------------
            # Absolutely prevent controller from living in
            # SolarGen_Internal
            # --------------------------------------------------

            internal = get_internal_collection()

            if internal is not None:

                if internal in controller.users_collection:
                    internal.objects.unlink(controller)

            # --------------------------------------------------
            # Put controller in the collection where the user
            # invoked SolarGen.
            # --------------------------------------------------

            if target_collection not in controller.users_collection:

                target_collection.objects.link(
                    controller
                )

            # Remove it from any accidental collection created
            # during append, while preserving target collection.
            for collection in list(controller.users_collection):

                if collection != target_collection:
                    collection.objects.unlink(controller)

            # --------------------------------------------------
            # Position
            # --------------------------------------------------

            controller.location = (
                context.scene.cursor.location.copy()
            )

            # --------------------------------------------------
            # Selection
            # --------------------------------------------------

            bpy.ops.object.select_all(
                action="DESELECT"
            )

            controller.hide_set(False)
            controller.hide_viewport = False
            controller.hide_render = False

            controller.select_set(True)

            context.view_layer.objects.active = controller

            self.report(
                {"INFO"},
                "SolarGen generator created.",
            )

            return {"FINISHED"}

        except Exception as error:

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# Select Generator
# ============================================================

class SOLARGEN_OT_select_generator(bpy.types.Operator):

    bl_idname = "object.solargen_select_generator"
    bl_label = "Select Generator"
    bl_description = "Select a SolarGen controller"

    def execute(self, context):

        controller = find_existing_controller(
            context
        )

        if controller is None:

            self.report(
                {"WARNING"},
                "No SolarGen generator exists in this scene.",
            )

            return {"CANCELLED"}

        bpy.ops.object.select_all(
            action="DESELECT"
        )

        controller.hide_set(False)
        controller.select_set(True)

        context.view_layer.objects.active = controller

        return {"FINISHED"}


# ============================================================
# Remove Generator
# ============================================================

class SOLARGEN_OT_remove_generator(bpy.types.Operator):

    bl_idname = "object.solargen_remove_generator"
    bl_label = "Remove Generator"
    bl_description = "Remove the selected SolarGen controller"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):

        return is_solargen_controller(
            context.active_object
        )

    def execute(self, context):

        obj = context.active_object

        if not is_solargen_controller(obj):
            return {"CANCELLED"}

        name = obj.name

        bpy.data.objects.remove(
            obj,
            do_unlink=True,
        )

        self.report(
            {"INFO"},
            f"{name} removed.",
        )

        return {"FINISHED"}


# ============================================================
# Source Asset Visibility
# ============================================================

class SOLARGEN_OT_show_sources(bpy.types.Operator):

    bl_idname = "object.solargen_show_sources"
    bl_label = "Show Source Assets"
    bl_description = (
        "Show the panel and support source meshes for editing"
    )

    def execute(self, context):

        if not set_internal_visibility(True):

            self.report(
                {"WARNING"},
                "SolarGen source assets are not loaded.",
            )

            return {"CANCELLED"}

        self.report(
            {"INFO"},
            "SolarGen source assets are now visible.",
        )

        return {"FINISHED"}


class SOLARGEN_OT_hide_sources(bpy.types.Operator):

    bl_idname = "object.solargen_hide_sources"
    bl_label = "Hide Source Assets"
    bl_description = (
        "Hide SolarGen's panel and support source meshes"
    )

    def execute(self, context):

        if not set_internal_visibility(False):

            self.report(
                {"WARNING"},
                "SolarGen source assets are not loaded.",
            )

            return {"CANCELLED"}

        return {"FINISHED"}


# ============================================================
# Sidebar
# ============================================================

class SOLARGEN_PT_main_panel(bpy.types.Panel):

    bl_label = "SolarGen"
    bl_idname = "SOLARGEN_PT_main_panel"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SolarGen"

    def draw(self, context):

        layout = self.layout
        obj = context.active_object

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        column = layout.column(
            align=True
        )

        column.label(
            text="Procedural Solar Array",
            icon="LIGHT_SUN",
        )

        column.label(
            text="Geometry Nodes Generator"
        )

        layout.separator()

        # ----------------------------------------------------
        # Generator
        # ----------------------------------------------------

        box = layout.box()

        box.label(
            text="Generator",
            icon="OUTLINER_OB_MESH",
        )

        row = box.row()

        row.scale_y = 1.4

        row.operator(
            "object.solargen_add_generator",
            text="Add Generator",
            icon="ADD",
        )

        # ----------------------------------------------------
        # Selected generator
        # ----------------------------------------------------

        if is_solargen_controller(obj):

            box.separator()

            box.label(
                text="Generator Selected",
                icon="CHECKMARK",
            )

            box.label(
                text="Edit parameters in the Modifiers tab."
            )

            row = box.row(
                align=True
            )

            row.operator(
                "object.solargen_remove_generator",
                text="Remove",
                icon="TRASH",
            )

        else:

            existing = find_existing_controller(
                context
            )

            if existing is not None:

                box.separator()

                box.label(
                    text="SolarGen exists in this scene.",
                    icon="INFO",
                )

                box.operator(
                    "object.solargen_select_generator",
                    text="Select Generator",
                    icon="RESTRICT_SELECT_OFF",
                )

            else:

                box.separator()

                box.label(
                    text="No generator in scene.",
                    icon="INFO",
                )

        # ----------------------------------------------------
        # Source Assets
        # ----------------------------------------------------

        internal = get_internal_collection()

        if internal is not None:

            layout.separator()

            box = layout.box()

            box.label(
                text="Source Assets",
                icon="MESH_GRID",
            )

            box.label(
                text="Advanced mesh customization"
            )

            if internal.hide_viewport:

                box.operator(
                    "object.solargen_show_sources",
                    text="Show Source Assets",
                    icon="HIDE_OFF",
                )

            else:

                box.operator(
                    "object.solargen_hide_sources",
                    text="Hide Source Assets",
                    icon="HIDE_ON",
                )

            box.label(
                text="Changes affect all generators.",
                icon="INFO",
            )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        layout.separator()

        row = layout.row()

        row.alignment = "CENTER"

        row.label(
            text=f"SolarGen v{ADDON_VERSION}"
        )


# ============================================================
# Right Click Menu
# ============================================================

def solargen_context_menu(self, context):

    layout = self.layout

    layout.separator()

    layout.operator(
        "object.solargen_add_generator",
        text="Add SolarGen Generator",
        icon="LIGHT_SUN",
    )


# ============================================================
# Registration
# ============================================================

classes = (
    SOLARGEN_OT_add_generator,
    SOLARGEN_OT_select_generator,
    SOLARGEN_OT_remove_generator,
    SOLARGEN_OT_show_sources,
    SOLARGEN_OT_hide_sources,
    SOLARGEN_PT_main_panel,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(
        solargen_context_menu
    )


def unregister():

    bpy.types.VIEW3D_MT_object_context_menu.remove(
        solargen_context_menu
    )

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()