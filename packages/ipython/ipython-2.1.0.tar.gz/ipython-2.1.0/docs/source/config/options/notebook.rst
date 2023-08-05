IPython notebook options
========================

Any of the :doc:`kernel` can also be used.

NotebookNotary.algorithm : 'md5'|'sha1'|'sha224'|'sha256'|'sha384'|'sha512'
    Default: 'sha256'

    The hashing algorithm used to sign notebooks.

NotebookNotary.secret : Bytes
    Default: ''

    The secret key with which notebooks are signed.

NotebookNotary.secret_file : Unicode
    Default: u''

    The file where the secret key is stored.

FileNotebookManager.checkpoint_dir : Unicode
    Default: '.ipynb_checkpoints'

    The directory name in which to keep notebook checkpoints
    
    This is a path relative to the notebook's own directory.
    
    By default, it is .ipynb_checkpoints

FileNotebookManager.hide_globs : List
    Default: [u'__pycache__']

    Glob patterns to hide in file and directory listings.

FileNotebookManager.notebook_dir : Unicode
    Default: u'/private/tmp/ipython/docs'

    No description

FileNotebookManager.save_script : Bool
    Default: False

    Automatically create a Python script when saving the notebook.
    
    For easier use of import, %run and %load across notebooks, a <notebook-
    name>.py script will be created next to any <notebook-name>.ipynb on each
    save.  This can also be set with the short `--script` flag.

NotebookManager.hide_globs : List
    Default: [u'__pycache__']

    Glob patterns to hide in file and directory listings.

NotebookApp.base_project_url : Unicode
    Default: '/'

    DEPRECATED use base_url

NotebookApp.base_url : Unicode
    Default: '/'

    The base URL for the notebook server.
    
    Leading and trailing slashes can be omitted, and will automatically be
    added.

NotebookApp.browser : Unicode
    Default: u''

    Specify what command to use to invoke a web browser when opening the
    notebook. If not specified, the default browser will be determined by the
    `webbrowser` standard library module, which allows setting of the BROWSER
    environment variable to override it.

NotebookApp.certfile : Unicode
    Default: u''

    The full path to an SSL/TLS certificate file.

NotebookApp.cookie_secret : Bytes
    Default: ''

    The random bytes used to secure cookies. By default this is a new random
    number every time you start the Notebook. Set it to a value in a config file
    to enable logins to persist across server sessions.
    
    Note: Cookie secrets should be kept private, do not share config files with
    cookie_secret stored in plaintext (you can read the value from a file).

NotebookApp.copy_config_files : Bool
    Default: False

    Whether to install the default config files into the profile dir. If a new
    profile is being created, and IPython contains config files for that
    profile, then they will be staged into the new directory.  Otherwise,
    default config files will be automatically generated.

NotebookApp.enable_mathjax : Bool
    Default: True

    Whether to enable MathJax for typesetting math/TeX
    
    MathJax is the javascript library IPython uses to render math/LaTeX. It is
    very large, so you may want to disable it if you have a slow internet
    connection, or for offline use of the notebook.
    
    When disabled, equations etc. will appear as their untransformed TeX source.

NotebookApp.extra_config_file : Unicode
    Default: u''

    Path to an extra config file to load.
    
    If specified, load this config file in addition to any other IPython config.

NotebookApp.extra_static_paths : List
    Default: []

    Extra paths to search for serving static files.
    
    This allows adding javascript/css to be available from the notebook server
    machine, or overriding individual files in the IPython

NotebookApp.file_to_run : Unicode
    Default: ''

    No description

NotebookApp.ip : Unicode
    Default: 'localhost'

    The IP address the notebook server will listen on.

NotebookApp.ipython_dir : Unicode
    Default: u''

    The name of the IPython directory. This directory is used for logging
    configuration (through profiles), history storage, etc. The default is
    usually $HOME/.ipython. This options can also be specified through the
    environment variable IPYTHONDIR.

NotebookApp.jinja_environment_options : Dict
    Default: {}

    Supply extra arguments that will be passed to Jinja environment.

NotebookApp.keyfile : Unicode
    Default: u''

    The full path to a private key file for usage with SSL/TLS.

NotebookApp.log_datefmt : Unicode
    Default: '%Y-%m-%d %H:%M:%S'

    The date format used by logging formatters for %(asctime)s

NotebookApp.log_format : Unicode
    Default: '[%(name)s]%(highlevel)s %(message)s'

    The Logging format template

NotebookApp.log_level : 0|10|20|30|40|50|'DEBUG'|'INFO'|'WARN'|'ERROR'|'CRITICAL'
    Default: 30

    Set the log level by value or name.

NotebookApp.mathjax_url : Unicode
    Default: ''

    The url for MathJax.js.

NotebookApp.nbextensions_path : List
    Default: []

    paths for Javascript extensions. By default, this is just
    IPYTHONDIR/nbextensions

NotebookApp.notebook_dir : Unicode
    Default: u'/private/tmp/ipython/docs'

    The directory to use for notebooks and kernels.

NotebookApp.notebook_manager_class : DottedObjectName
    Default: 'IPython.html.services.notebooks.filenbmanager.FileNotebookMa...

    The notebook manager class to use.

NotebookApp.open_browser : Bool
    Default: True

    Whether to open in a browser after starting. The specific browser used is
    platform dependent and determined by the python standard library
    `webbrowser` module, unless it is overridden using the --browser
    (NotebookApp.browser) configuration option.

NotebookApp.overwrite : Bool
    Default: False

    Whether to overwrite existing config files when copying

NotebookApp.password : Unicode
    Default: u''

    Hashed password to use for web authentication.
    
    To generate, type in a python/IPython shell:
    
      from IPython.lib import passwd; passwd()
    
    The string should be of the form type:salt:hashed-password.

NotebookApp.port : Integer
    Default: 8888

    The port the notebook server will listen on.

NotebookApp.port_retries : Integer
    Default: 50

    The number of additional ports to try if the specified port is not
    available.

NotebookApp.profile : Unicode
    Default: u'default'

    The IPython profile to use.

NotebookApp.trust_xheaders : Bool
    Default: False

    Whether to trust or not X-Scheme/X-Forwarded-Proto and X-Real-Ip/X
    -Forwarded-For headerssent by the upstream reverse proxy. Necessary if the
    proxy handles SSL

NotebookApp.verbose_crash : Bool
    Default: False

    Create a massive crash report when IPython encounters what may be an
    internal error.  The default is to append a short message to the usual
    traceback

NotebookApp.webapp_settings : Dict
    Default: {}

    Supply overrides for the tornado.web.Application that the IPython notebook
    uses.

MappingKernelManager.kernel_manager_class : DottedObjectName
    Default: 'IPython.kernel.ioloop.IOLoopKernelManager'

    The kernel manager class.  This is configurable to allow subclassing of the
    KernelManager for customized behavior.

MappingKernelManager.root_dir : Unicode
    Default: u'/private/tmp/ipython/docs'

    No description

KernelManager.autorestart : Bool
    Default: False

    Should we autorestart the kernel if it dies.

KernelManager.ip : Unicode
    Default: u''

    Set the kernel's IP address [default localhost]. If the IP address is
    something other than localhost, then Consoles on other machines will be able
    to connect to the Kernel, so be careful!

KernelManager.kernel_cmd : List
    Default: []

    The Popen Command to launch the kernel. Override this if you have a custom
    kernel. If kernel_cmd is specified in a configuration file, IPython does not
    pass any arguments to the kernel, because it cannot make any assumptions
    about the  arguments that the kernel understands. In particular, this means
    that the kernel does not receive the option --debug if it given on the
    IPython command line.

KernelManager.transport : 'tcp'|'ipc'
    Default: 'tcp'

    No description

InlineBackend.close_figures : Bool
    Default: True

    Close all figures at the end of each cell.
    
    When True, ensures that each cell starts with no active figures, but it also
    means that one must keep track of references in order to edit or redraw
    figures in subsequent cells. This mode is ideal for the notebook, where
    residual plots from other cells might be surprising.
    
    When False, one must call figure() to create new figures. This means that
    gcf() and getfigs() can reference figures created in other cells, and the
    active figure can continue to be edited with pylab/pyplot methods that
    reference the current active figure. This mode facilitates iterative editing
    of figures, and behaves most consistently with other matplotlib backends,
    but figure barriers between cells must be explicit.

InlineBackend.figure_format : Unicode
    Default: u''

    The figure format to enable (deprecated use `figure_formats` instead)

InlineBackend.figure_formats : Set
    Default: set(['png'])

    A set of figure formats to enable: 'png',  'retina', 'jpeg', 'svg', 'pdf'.

InlineBackend.print_figure_kwargs : Dict
    Default: {'bbox_inches': 'tight'}

    Extra kwargs to be passed to fig.canvas.print_figure.
    
    Logical examples include: bbox_inches, quality (for jpeg figures), etc.

InlineBackend.rc : Dict
    Default: {'font.size': 10, 'figure.figsize': (6.0, 4.0), 'figure.facec...

    Subset of matplotlib rcParams that should be different for the inline
    backend.
