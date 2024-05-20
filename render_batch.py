import os
import sys
import time
from joblib import Parallel, delayed
import argparse

#python -u render_batch.py --model_root_dir model_dir --render_root_dir /tmp --filelist_dir filelists --blender_location blender.exe --shapenetversion v2 --debug False

parser = argparse.ArgumentParser()
parser.add_argument('--model_root_dir', type=str, default="model_dir")
parser.add_argument('--render_root_dir', type=str, default="/tmp")
parser.add_argument('--filelist_dir', type=str, default="filelists")
parser.add_argument('--blender_location', type=str, default="blender.exe")
parser.add_argument('--num_thread', type=int, default=10, help='1/3 of the CPU number')
parser.add_argument('--shapenetversion', type=str, default="v2", help='v1 or v2')
parser.add_argument('--debug', type=bool, default=False)
FLAGS = parser.parse_args()

model_root_dir = FLAGS.model_root_dir
render_root_dir = FLAGS.render_root_dir
filelist_dir = FLAGS.filelist_dir

def gen_obj(model_root_dir, cat_id, obj_id):
    if FLAGS.shapenetversion == "v2":
        objpath = os.path.join(model_root_dir, cat_id, obj_id, "models", "model_normalized")
        # Append the '.obj' extension
        # objpath += ".obj"
        print("###################")
        print("objpath:::", objpath)
    else:
        objpath = os.path.join(model_root_dir, cat_id, obj_id, "model.obj")  # Assuming the file extension is ".obj" for v1

    obj_image_easy_dir = os.path.join(render_root_dir, "image", cat_id, obj_id, "easy")
    obj_albedo_easy_dir = os.path.join(render_root_dir, "albedo", cat_id, obj_id, "easy")
    obj_depth_easy_dir = os.path.join(render_root_dir, "depth", cat_id, obj_id, "easy")
    obj_normal_easy_dir = os.path.join(render_root_dir, "normal", cat_id, obj_id, "easy")
    obj_image_hard_dir = os.path.join(render_root_dir, "image", cat_id, obj_id, "hard")
    obj_albedo_hard_dir = os.path.join(render_root_dir, "albedo", cat_id, obj_id, "hard")
    obj_depth_hard_dir = os.path.join(render_root_dir, "depth", cat_id, obj_id, "hard")
    obj_normal_hard_dir = os.path.join(render_root_dir, "normal", cat_id, obj_id, "hard")
    
    os.makedirs(obj_image_easy_dir, exist_ok=True)
    os.makedirs(obj_albedo_easy_dir, exist_ok=True)
    os.makedirs(obj_depth_easy_dir, exist_ok=True)
    os.makedirs(obj_normal_easy_dir, exist_ok=True)
    os.makedirs(obj_image_hard_dir, exist_ok=True)
    os.makedirs(obj_albedo_hard_dir, exist_ok=True)
    os.makedirs(obj_depth_hard_dir, exist_ok=True)
    os.makedirs(obj_normal_hard_dir, exist_ok=True)
    
    if os.path.exists(os.path.join(obj_normal_hard_dir, "rendering_metadata.txt")):
        print("Exist!!!, skip %s %s" % (cat_id, obj_id))
    else:
        print("Start %s %s" % (cat_id, obj_id))
        if FLAGS.debug:
            os.system(FLAGS.blender_location + ' --background --python render_blender.py -- --views %d --obj_image_easy_dir %s --obj_albedo_easy_dir %s --obj_depth_easy_dir %s --obj_normal_easy_dir %s --obj_image_hard_dir %s --obj_albedo_hard_dir %s --obj_depth_hard_dir %s --obj_normal_hard_dir %s %s ' % (36, obj_image_easy_dir, obj_albedo_easy_dir, obj_depth_easy_dir, obj_normal_easy_dir, obj_image_hard_dir, obj_albedo_hard_dir, obj_depth_hard_dir, obj_normal_hard_dir, objpath))
        else:
            os.system(FLAGS.blender_location + ' --background --python render_blender.py -- --views %d --obj_image_easy_dir %s --obj_albedo_easy_dir %s --obj_depth_easy_dir %s --obj_normal_easy_dir %s --obj_image_hard_dir %s --obj_albedo_hard_dir %s --obj_depth_hard_dir %s --obj_normal_hard_dir %s %s > /dev/null 2>&1' % (36, obj_image_easy_dir, obj_albedo_easy_dir, obj_depth_easy_dir, obj_normal_easy_dir, obj_image_hard_dir, obj_albedo_hard_dir, obj_depth_hard_dir, obj_normal_hard_dir, objpath))

        print("Finished %s %s"%(cat_id, obj_id))

def read_obj_ids_from_lst(file):
    with open(file) as f:
        return f.read().splitlines()

for filename in os.listdir(filelist_dir):
    if filename.endswith(".lst"):
        cat_id = filename.split(".")[0]
        file = os.path.join(filelist_dir, filename)
        obj_ids = read_obj_ids_from_lst(file)
        model_root_dir_lst = [model_root_dir for _ in range(len(obj_ids))]
        cat_id_lst = [cat_id for _ in range(len(obj_ids))]
        with Parallel(n_jobs=5) as parallel:
            parallel(delayed(gen_obj)(model_root_dir, cat_id, obj_id) for
                     model_root_dir, cat_id, obj_id in
                     zip(model_root_dir_lst, cat_id_lst, obj_ids))
    print("Finished %s" % cat_id)
