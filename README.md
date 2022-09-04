# MappingUtilities
A collection of small add-ons that make it easier to use Blender as an old-school level editor.
## Rescale All Grids
Decrease/increase grid scale manually and simultaneously for all viewports, using Numpad -/+. 
When you change the grid scale it will be output to the bottom header. 
You can set a custom grid scale multiplier and a custom unit name in the add-on preferences.
To-do: Add an option to draw the grid scale to the viewport.

**Note**: Remember to set Blender to use the "None" unit system.

![ResaleAllGrids](https://user-images.githubusercontent.com/36510916/188155972-9758adb4-74b8-4b39-82b8-eb69b945a56e.gif)

## ExtrudeIntoObject
Extrudes a selection of faces into a new and closed object, using Ctrl+Alt+E. Supports multi-object editing.
To-do: select the new top faces and activate fatten/shrinken.

![ExtrudeIntoObject](https://user-images.githubusercontent.com/36510916/188155936-a62b03a4-df7c-428a-9a6e-cb45be1d9d4c.gif)

## Assign Per-Face Materials
Assigns a separate material to every face in the object. 
Keep in mind that this add-on creates a material slot for each face.

![AssignMatsPerFace](https://user-images.githubusercontent.com/36510916/188155558-6b2807c5-305a-4475-8f04-9b1340eb5be7.gif)

## Useful add-ons
Jason van Gumster's **Lockview** script that exposes the lock view rotation that Blender's Quad View uses. 
This lets you set up and lock custom orto viewports.

https://gist.github.com/Fweeb/bb61c15139bff338cb17
  
  
Bram Eulaers' wonderful **DreamUV** that lets you do a lot of UV related stuff in the 3D viewport.

https://github.com/leukbaars/DreamUV
