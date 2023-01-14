# CSSALT_LAB_FFT Python-Version

## Default setup
1. Clone repository from github into working directory
    git clone https://github.com/VSai2314108/FFT.git
2. Create a virtual enviorment and install the requirements file
    Given no errors the .fftproj virtual enviorment will autmatically be available
    Otherwise
    create a virtual environment python3 -m venv --system-site-packages
    source [path] - /Users/vsai23/Workspace/FFT/fftproj/bin/activate]
    pip install -r requirements.txt
3. If there is a pyaudio installation error due to homebrew run the below command 
    pip3 install --global-option='build_ext' --global-option="-I$(brew --prefix)/include" --global-option="-L$(brew --prefix)/lib" pyaudio
    python3 -m pip install pyaudio --global-option="build_ext" --global-option="-I/opt/homebrew/include" --global-option="-L/opt/homebrew/lib"
4. Reach out to me at somasundaramv@ufl.edu if there is any further challenges

## About
The project above is an attempt at automating of a year's worth of research pertaining to the impact of air embolisms on the frequency and volume of the heart beat. Feel free to dive into the code and explore!
