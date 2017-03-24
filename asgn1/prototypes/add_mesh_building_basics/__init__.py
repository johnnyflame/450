################################################################################
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This is free software; you may redistribute it, and/or modify it,
# under the terms of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#  http://www.gnu.org/licenses/
#
# ***** END GPL LICENSE BLOCK *****
'''
Create various architectural/interior design objects for use in a Blender scene.
'''
#
# This collection of scripts has been contributed to by many authors,
#  see documentation "Credits" for details.
#
# @todo: check "Object" mode in scripts that fail in "Edit" Mode; else allow.
#  fails so far: Block Wall, Column.
#   Note: when in "Edit" mode new object is "merged" with selected object,
#    joined as singular object - cool bug/feature...
#
################################################################################

bl_info = {
    "name": "Building Basics",
    "description": "Create various Architectural constructs.",
    "author": "See documentation Credits.",
    "version": (0, 1, 6),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > Building Basics",
#    "warning": "WIP - Frequent changes for known issues and enhancements.",
    "support": "COMMUNITY", # OFFICIAL, COMMUNITY, TESTING.
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Add_Mesh/BuildingBasics",
    "tracker_url": "https://developer.blender.org/T44022",
    "category": "Add Mesh"
    }

# in AlphaBetical order by script name...
if "bpy" in locals():
    import imp
    imp.reload(Balcony)
    imp.reload(Beams)
    imp.reload(Blockwall)
    imp.reload(Column)
    imp.reload(Counter)
    imp.reload(Doorway)
else:
    from . import Balcony
    from . import Beams
    from . import Blockwall
    from . import Column
    from . import Doorway

import bpy


# Define the "Building Basics" menu
class buildingbasicsMenu(bpy.types.Menu):
    bl_idname = "buildingbasicsMenu"
    bl_label = "Building Basics"

    # in AlphaBetical order by script name...
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.add_balcony",text="Balcony",icon="COLLAPSEMENU")
        layout.operator("mesh.add_beam",text="Beams",icon="MESH_CUBE")
        layout.operator("mesh.add_wall",text="Block Wall",icon="MOD_BUILD")
        layout.operator("mesh.add_column",text="Column",icon="MESH_CYLINDER")
        layout.operator("mesh.add_doorway",text="Doorway",icon="MOD_LATTICE")

# Handle (menu) operators and panels
def menu_func(self, context):
    self.layout.menu("buildingbasicsMenu",icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
