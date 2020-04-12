echo "Starting $0 for folder : $1"

python3 /home/henri/Documents/blender_projects/Github/BlenderAddons/batch_resize_images.py -- $1

/home/henri/Téléchargements/blender-2.83-85de07e64c96-linux64/blender -b --python /home/henri/Documents/blender_projects/Github/BlenderAddons/import_megascan.py -- $1

echo "Done"
