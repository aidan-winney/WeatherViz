# WeatherViz

A desktop application for displaying historical weather data on an interactive map.

![WeatherViz](https://raw.githubusercontent.com/aidan-winney/WeatherViz/main/weatherviz.png "application launch")

## Major Features

<p>
<img src="https://raw.githubusercontent.com/aidan-winney/WeatherViz/main/demo.gif" width="317" height="214" align="right">

### Heatmap interpolation
### Smooth timelapse
1. Ability to select time frame and parameters (temp, rain, wind) and query/render data in real time
2. Adjustable playback feature allows the user to view the weather trend for their selection
### Custom UI
- Reworked, more intuitive UI, that scales according to the window size, required no external tools in its creation
### Caching
- Queries save in local database
- Will load up the saved queries when the program is opened
- Can add and delete from the saved queries

Example: Hurricane Irma Timelapse
</p>

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
