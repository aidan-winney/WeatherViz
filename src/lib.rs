use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use reqwest;

const PI: f64 = std::f64::consts::PI;
const DEG_TO_RAD: f64 = PI / 180.0;
const MAX_LAT: f64 = 85.0511287798; // arctan(sinh(pi))
const TRN_SCALE: f64 = 0.5 / PI;

fn scale(zoom: i32) -> f64 {
    256.0 * 2.0_f64.powf(zoom as f64)
}

// geocoords to coords on The Big Map in pixel space
fn project(lat: f64, lon: f64, zoom: i32) -> (f64, f64) {
    let sin = (MAX_LAT.min(lat).max(-MAX_LAT) * DEG_TO_RAD).sin();
    let zoom_scale = scale(zoom);
    let (x, y) = (lon * DEG_TO_RAD, ((1.0 + sin) / (1.0 - sin)).ln() / 2.0);
    (zoom_scale * (TRN_SCALE * x + 0.5), zoom_scale * (0.5 - TRN_SCALE * y))
}

// get geocoords of the points in a res x res lattice in pixel space
#[pyfunction]
fn geocoords(width: i32, height: i32, res: i32, lat: f64, lon: f64, zoom: i32) -> Vec<(f64, f64)> {
    let width = width as f64;
    let height = height as f64;
    let inverse = 1.0 / (res as f64);
    let offset = (inverse - 1.0) / 2.0;
    let zoom_scale = scale(zoom);
    let (x_i, y_i) = project(lat, lon, zoom);
    let mut coords = Vec::new();
    for i in 0..res {
        let i = i as f64;
        for j in 0..res {
            let j = j as f64;
            let x = ((x_i + width * (i * inverse + offset)) / zoom_scale - 0.5) / TRN_SCALE;
            let y = ((y_i + height * (j * inverse + offset)) / zoom_scale - 0.5) / -TRN_SCALE;
            coords.push(((2.0 * y.exp().atan() - PI / 2.0) / DEG_TO_RAD, x / DEG_TO_RAD));
        }
    }
    coords
}

#[pyfunction]
fn get_data(lat: f64, lon: f64, start_date: &str, end_date: &str, daily: bool, variable: &str,
            temp: &str, windspeed: &str, precipitation: &str, tz: &str) -> PyResult<String> {
    let mut url = format!("https://archive-api.open-meteo.com/v1/archive\
        ?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}\
        &temperature_unit={temp}&windspeed_unit={windspeed}&precipitation_unit={precipitation}\
        &timezone={tz}&models=best_match&cell_selection=nearest");
    if daily {
        url = format!("{url}&daily={variable}");
    } else {
        url = format!("{url}&hourly={variable}");
    }
    let client = reqwest::blocking::Client::new();
    let res = client.get(&url).send().map_err(|err| PyRuntimeError::new_err(format!("{err}")))?;
    let status = res.status();
    let text = res.text().map_err(|err| PyRuntimeError::new_err(format!("{err}")))?;
    if status.is_success() {    
        Ok(text)
    } else {
        Err(PyRuntimeError::new_err(format!("The request failed w/ code {status}, text {text}")))
    }
}

#[pymodule]
#[pyo3(name="renderer")]
fn renderer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(geocoords, m)?)?;
    m.add_function(wrap_pyfunction!(get_data, m)?)?;
    Ok(())
}
