

import os

import PyInstaller.__main__

try:
    install_dir=(os.path.dirname(os.path.realpath(__file__)))
    main_script=install_dir+'/../src/main.py'

    PyInstaller.__main__.run([
        main_script,
        '--onefile',
        '--specpath', install_dir,
        '--distpath', os.path.join(install_dir,"dist"),
        '--workpath', os.path.join(install_dir,"build"),
        '--windowed',
        '--name', 'wall-simulator'
    ])
except Exception:
    print("Failed install")
    

