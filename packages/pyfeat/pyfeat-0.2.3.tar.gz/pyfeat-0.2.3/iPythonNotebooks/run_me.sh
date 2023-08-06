#!/bin/bash

echo "Running simulated tempering simulations..."
echo "   [Symmetric double well potential]"
python generators/gen_st_sdwp.py
echo "   [Asymmetric double well potential]"
python generators/gen_st_adwp.py
echo "   [Folding potential]"
python generators/gen_st_fp.py
echo "...done!"

echo "Running umbrella sampling simulations..."
echo "   [Symmetric double well potential]"
python generators/gen_us_sdwp.py
echo "   [Folding potential]"
python generators/gen_us_fp.py
echo "...done!"
