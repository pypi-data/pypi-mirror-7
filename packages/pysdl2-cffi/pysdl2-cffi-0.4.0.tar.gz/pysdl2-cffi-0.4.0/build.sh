#!/bin/sh
# Generate automatic wrapper helpers.
(cd builder ; python dox.py ~/prog/SDL2-2.0.3/include/xml/)
python -m builder.build_sdl
python -m builder.build_ttf
python -m builder.build_mixer
python -m builder.build_image
# Sphinx and doc extraction don't work in Python 3 yet.
echo "Sphinx"
(cd docs; make clean; make html)
