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
	pip install ./WeatherViz
 	```

Now the application can be run as `weatherviz`. **Currently, this script only works in the parent directory of the repository**--i.e. the current directory after executing the above commands.

Additionally, it looks for a `config.toml` file in the current directory. Copy `config_example.toml` to get a starter configuration file:

	cp WeatherViz/config_example.toml config.toml
