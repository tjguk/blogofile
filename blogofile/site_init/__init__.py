import os
import pkgutil
import zipfile
import io
import logging
import shutil
import imp
import traceback
from .. import __version__ as bf_version

logger = logging.getLogger("blogofile.site_init")

from .. import util

available_sites = [
    # (name of site, description, module)
    ("bare", "A blank site with no blog", "bare"),
    ("simple_blog", "A (very) simple blog with no theme", "simple_blog"),
    ("simple_blog_html5", "A simple blog with HTML5 boilerplate", "simple_blog_html5"),
    ("jinja2_test", "A site based on jinja2 templates", "jinja2_test"),
    ("blog_unit_test", "Blog unit tests (not for end users)", "blog_unit_test")
    ]

#These are hidden site templates that are not shown in the list shown in help
hidden_sites = [
    ]

extra_features = {
    }

all_sites = list(available_sites)
all_sites.extend(hidden_sites)

site_modules = dict((x[0], x[2]) for x in all_sites)

def zip_site_init():
    """Zip up all of the subdirectories of site_init

    This function should only be called by setuptools
    """
    try:
        curdir = os.getcwdu()
        root = os.path.join(curdir, u"blogofile", u"site_init")
        for d in os.listdir(root):
            if d == u'__pycache__':
                continue
            d = os.path.join(root, d)
            if os.path.isdir(d):
                os.chdir(root)
                zf = d + u".zip"
                z = zipfile.ZipFile(zf, "w")
                os.chdir(d)
                for dirpath, dirnames, filenames in os.walk(unicode(os.curdir)):
                    if len(filenames) == 0:
                        #This is an empty directory, add it anyway:
                        z.writestr(zipfile.ZipInfo(dirpath+u"/"), '')
                    for fn in filenames:
                        z.write(os.path.join(dirpath, fn))
                z.close()
    finally:
        os.chdir(curdir)

def do_help(): #pragma: no cover
    print("For example, create a simple site with a blog and no theme:\n")
    print("   blogofile init simple_blog\n")

def import_site_init(feature):
    """Copy a site_init template to the build dir.

    site_init templates can be of four forms:
      1) A directory
      2) A zip file
      3) A .py file
      4) A function and args tuple
    Directories are usually used in development,
    whereas zip files are used in production.
    .py files and functions are special in that they control how to initialize a site,
    for example, pulling from a git repository."""
    #If the directory exists, just use that.
    if type(feature) == tuple:
        feature[0](**feature[1])
        return
    path = os.path.join(os.path.split(__file__)[0], feature)
    if os.path.isdir(path):
        logger.info("Initializing site from directory: " + path)
        for root, dirs, files in os.walk(path):
            for fn in files:
                if fn.startswith("."):
                    continue
                fn = os.path.join(root, fn)
                dst_fn = fn.replace(path + os.path.sep,"")
                dst_dir = os.path.split(dst_fn)[0]
                util.mkdir(dst_dir)
                shutil.copyfile(fn, dst_fn)
    #If a .py file exists, run with that:
    elif os.path.isfile(path) and path.endswith(".py"):
        mod = imp.load_source("mod", path)
        mod.do_init()
    #Otherwise, load it from the zip file
    else:
        try:
            zip_data = pkgutil.get_data("blogofile.site_init", feature + ".zip")
        except IOError:
            raise
        else:
            logger.info("Initializing feature from zip file: {0}".format(feature))
            zip_file = zipfile.ZipFile(io.BytesIO(zip_data))
            for name in zip_file.namelist():
                if name.endswith('/'):
                    util.mkdir(name)
                else:
                    util.mkdir(os.path.split(name)[0])
                    f = open(name, 'wb')
                    f.write(zip_file.read(name))
                    f.close()
    #Recursively import child features of this feature
    try:
        child_features = extra_features[feature]
    except KeyError:
        pass
    else:
        for child_feature in child_features:
            import_site_init(child_feature)

def do_init(args):
    if not args.SITE_TEMPLATE:
        do_help()
    else:
        if args.SITE_TEMPLATE not in [x[0] for x in all_sites]:
            do_help()
            return
        if len(os.listdir(args.src_dir)) > 0 :
            print(("This directory is not empty, will not attempt to " \
                    "initialize here : {0}".format(args.src_dir)))
            return

        print(("Initializing the {0} site template...".format(
                args.SITE_TEMPLATE)))
        template = site_modules[args.SITE_TEMPLATE]
        import_site_init(template)
