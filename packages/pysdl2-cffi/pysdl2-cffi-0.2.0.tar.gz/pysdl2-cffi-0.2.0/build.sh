#!/bin/sh
# Generate automatic wrapper helpers.
python -m builder.build_sdl
python -m builder.build_ttf
python -m builder.build_mixer
python -m builder.build_image
