@echo off
pip3 install -r .requirements.txt
attrib +h .options.json
attrib +h .requirements.txt
echo: && echo: && echo: && echo INSTALLATION COMPLETE. YOU MAY NOW CLOSE THIS WINDOW
pause