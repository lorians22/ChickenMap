@echo off
attrib +h .options.json
attrib +h .requirements.txt
attrib +h .readme_imgs
attrib +h .3D_matrices
pip3 install -r .requirements.txt && echo: && echo: && echo: && echo INSTALLATION COMPLETE. YOU MAY NOW CLOSE THIS WINDOW
pause