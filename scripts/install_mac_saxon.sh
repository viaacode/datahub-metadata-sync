source python_env/bin/activate

saxon='libsaxon-HEC-mac-setup-v1.2.1'

# Download saxon mac version
#curl https://www.saxonica.com/saxon-c/${saxon}.zip --output saxon.zip

unzip saxon.zip -d saxon &&\
    sudo cp saxon/libsaxonhec.dylib /usr/local/lib/.
    sudo cp -r saxon/rt /usr/local/lib/.

# Build the saxon python module and add it to pythonpath.
cd saxon/Saxon.C.API/python-saxon
python3 saxon-setup.py build_ext -if

export PYTHONPATH=$PYTHONPATH:$(pwd)
cd ../../../



