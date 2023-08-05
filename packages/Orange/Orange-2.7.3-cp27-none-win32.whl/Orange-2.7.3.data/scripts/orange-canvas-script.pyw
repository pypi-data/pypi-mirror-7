#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'Orange==2.7.3','gui_scripts','orange-canvas'
__requires__ = 'Orange==2.7.3'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('Orange==2.7.3', 'gui_scripts', 'orange-canvas')()
    )
