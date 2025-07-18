'''Find location of Leo if possible.

Search common locations for python environments,
test if Leo is present.
    - pipx
    - mamba
    - conda
    - cpython
'''
import os
import tempfile

# LeoPyRref.leo >> LeoApp: global directories>>
leo_global_dirs = '''
self.extensionsDir: str = None  # The leo/extensions directory
self.globalConfigDir: str = None  # leo/config directory
self.globalOpenDir: str = None  # The directory last used to open a file.
self.homeDir: str = None  # The user's home directory.
self.homeLeoDir: str = None  # The user's home/.leo directory.
self.leoEditorDir: str = None  # The leo-editor directory.
self.loadDir: str = None  # The leo/core directory.
self.machineDir: str = None  # The machine-specific directory.
self.theme_directory: str = None  # The directory from which the theme file was loaded, if any.
'''

# is Leo in path? if yes it should supercede all other possibles
if 'file_name' not in locals() or file_name is None:
    file_name = 'leo'

def is_in_path(file_name):
    for folder in os.environ["PATH"].split(os.pathsep):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path) or os.access(file_path, os.X_OK):
            return file_path
    return None

# Usage
location = is_in_path('file_name')
if location:
    print("Location of 'file_name':", location)
    get_leo_config(location)
else:
    print(f"'{file_name}' not found in PATH.")


def write_leo_test_script():
    f = tempfile.NamedTemporaryFile(prefix='leo_', mode='w+t')
    f.write("g.es_print('LeoDir:\t',g.app.loadManager.computeLeoDir())")
    f.close()
    return f

def get_leo_config(location)
    # run Leo launcher and use to return it's internal config info
    # run `leo --script={fname}` and capture stdout results:


## Scenario 1: Leo cmd is in PATH. Use it to report it's location
echo g.es_print('LeoDir:\t',g.app.loadManager.computeLeoDir()) > tmp_locate_leo_dir.leox
leo-messages --script=tmp_locate_leo_dir.leox

## Scenario 2: Python is in PATH and Leo has been installed to it


