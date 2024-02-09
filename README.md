# MappingUtilities
A collection of small add-ons that make it easier to use Blender as an old-school level editor.
## Rescale All Grids
Decrease/increase grid scale manually and simultaneously for all viewports, using Numpad -/+. 
When you change the grid scale it will be output to the bottom header. 
You can set a custom grid scale multiplier and a custom unit name in the add-on preferences.
To-do: Add an option to draw the grid scale to the viewport.

**Note**: Remember to set Blender to use the "None" unit system.

![ResaleAllGrids](https://user-images.githubusercontent.com/36510916/188155972-9758adb4-74b8-4b39-82b8-eb69b945a56e.gif)

## Extrude Into Closed Mesh
Extrudes a selection of faces into a split and closed mesh, using Ctr+Alt+E. Replaces Extrude Into Object.

![selection_to_closed_mesh](https://github.com/gildedhipbone/MappingUtilities/assets/36510916/a6d852c2-f35f-46f1-a3a2-f8b369cc278c)

## Assign Material Asset to Selection
Assigns the selected material in the Asset Browser to your selection. Re-uses materials and material slots when possible. 
It's currently not possible to hook into the Asset Browser's drag and drop functionality, hence the button.

![assign_mat_to_selection](https://github.com/gildedhipbone/MappingUtilities/assets/36510916/2364f60f-4c76-47ca-a687-3271b610b823)

## Assign Per-Face Materials
Assigns a separate material to every face in the object. 
Keep in mind that this add-on creates a material slot for each face.

![AssignMatsPerFace](https://user-images.githubusercontent.com/36510916/188155558-6b2807c5-305a-4475-8f04-9b1340eb5be7.gif)

## ExtrudeIntoObject (NOT compatible with Blender 4.0+)
Extrudes a selection of faces into a new and closed object, using Ctrl+Alt+E. Supports multi-object editing.
To-do: select the new top faces and activate fatten/shrinken.

![ExtrudeIntoObject](https://user-images.githubusercontent.com/36510916/188155936-a62b03a4-df7c-428a-9a6e-cb45be1d9d4c.gif)

## Useful add-ons
Jason van Gumster's **Lockview** script that exposes the lock view rotation that Blender's Quad View uses. 
This lets you set up and lock custom orto viewports.

https://gist.github.com/Fweeb/bb61c15139bff338cb17
  
  
Bram Eulaers' wonderful **DreamUV** that lets you do a lot of UV related stuff in the 3D viewport.

https://github.com/leukbaars/DreamUV


This add-on gives you a toggle to double-click to link select.

https://onlinerender.gumroad.com/l/doubleclick
