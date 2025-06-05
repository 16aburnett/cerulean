#! /bin/bash

# Build script for CeruleanIR Compiler
# Author: Amy Burnett

# build 
echo "Building CeruleanIR Compiler"
pyinstaller cerulean_ir_compiler.py --noconfirm -n ceruleanirc --clean
echo "Finished Build"

# add built-in library
echo "Adding builtin libraries to dist"
# cp AmyScriptBuiltinLib.amy.assembly dist/ceruleanirc/

# install
export INSTALL_DIR="$HOME/bin"
echo "Installing into $INSTALL_DIR"
mkdir -p $INSTALL_DIR
# delete previous
rm -f $INSTALL_DIR/ceruleanirc
ln -s `pwd`/dist/ceruleanirc/ceruleanirc "$INSTALL_DIR/ceruleanirc"

# ensure it is in the path
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo "Warning: You need to add $HOME/bin to your path"
    echo "   you can do this by adding the following line to your ~/.bashrc"
    echo 'export PATH="$HOME/bin:$PATH"'
fi

echo "Install finished"