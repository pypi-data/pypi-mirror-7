import os, importlib
import inspect


def scan_folder_recursive(folder, excl_names=['__']):
    """ Recursive search for PY files in given folder """
    all_files = []                                                                                                                                                                      
    for root, d, files in os.walk(folder):                                              #@UnusedVariable
        filelist = [os.path.join(root, fi) for fi in files if fi.endswith('.py')
                    and not any(fi.startswith(prefix) for prefix in excl_names)]
        all_files += filelist
    return all_files


def scan_package(p):
    for x in dir(p):
        if not x.startswith("_"):
            o = getattr(p, x)
            if inspect.isclass(o) and o.__module__.startswith(p.__name__) and getattr(o, "METAROUTE_CONTROLLER_PATH", None) is not None: 
                    yield o


def attach_controllers(app, pkg):
    pkg_path = pkg.__path__[0]
    pkg_name = pkg.__name__
    
    all_files = scan_folder_recursive(pkg_path)
    for f in all_files:
        pkg = f[len(pkg_path):]
        pkg = pkg.strip("/\\")[:-3]
        
        if len(pkg):
            pkg = pkg_name + "." + pkg
        
        attach_controller(app, importlib.import_module(pkg))


def attach_controller(app, mdl):
    for cls in scan_package(mdl):
        if cls.__module__.startswith(mdl.__name__):
            cpath = getattr(cls, "METAROUTE_CONTROLLER_PATH", None)
            if cpath is not None:
                ctrl    = cls()
                methods = dir(ctrl)
                for meth in methods:
                    m  = getattr(cls, meth, None)
                    
                    for path, args, opts in getattr(m, "METAROUTE_ACTION_PATHS", []):
                        xf = cls.__dict__[m.__name__].__get__(ctrl, cls)
                        opts['endpoint'] = cls.__module__ + "." + cls.__name__ + "." + xf.__name__
                        app.route(cpath + path, **opts)(cls.__dict__[m.__name__].__get__(ctrl, cls))
    
                    for ex in getattr(m, "METAROUTE_ERROR_EXCEPTIONS", []):
                        app._register_error_handler(None, ex, cls.__dict__[m.__name__].__get__(ctrl, cls))
