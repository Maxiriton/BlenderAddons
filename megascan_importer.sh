echo "Starting $0 for folder : $1"

python3 /home/henri/Documents/blender_projects/Github/BlenderAddons/batch_resize_images.py -- $1

/home/henri/blender-git/build_linux/bin/blender -b --python /home/henri/Documents/blender_projects/Github/BlenderAddons/import_megascan.py -- $1

echo "Done"
