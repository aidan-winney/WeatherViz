# WeatherViz

A desktop application for displaying historical weather data on an interactive map.

## Repository

https://github.com/SplatMudkip/WeatherViz

## Setup

1. WeatherViz has only been tested on WSL with Ubuntu. In addition to the Python and Rust toolchains, WeatherViz requires several system packages to be installed:

	```
	sudo apt-get update
	sudo apt install gcc make g++ pkg-config libfontconfig-dev libssl-dev libgl1 x11-xserver-utils libnss3 libxcomposite1 libxdamage1 libxtst6 libxkbcommon0 libasound2 libxcb-icccm4 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0
	sudo snap install cmake --classic
	```

3. Create a Python 3.8 virtual environment.

4. Activate the environment, clone the repository, and install the package:

	```
	git clone https://github.com/SplatMudkip/WeatherViz
    cd WeatherViz
	pip install .
 	```

Now the application can be run as `weatherviz`.

WeatherViz looks for a `config.toml` file in the current directory, falling back on default values without one. To get a starter configuration file including comments explaining each option, copy `config_example.toml` to the directory that WeatherViz will be executed from, for example:

	cp config_example.toml config.toml
