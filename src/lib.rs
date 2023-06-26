// TODO: modularize and lint this library!!!!!!!!!!

use pyo3::{prelude::*, exceptions::PyRuntimeError, types::PyBytes};
use raqote::*;
use std::collections::HashMap;
use reqwest;

const PI: f64 = std::f64::consts::PI;
const DEG_TO_RAD: f64 = PI / 180.0;
const MAX_LAT: f64 = 85.0511287798; // arctan(sinh(pi))
const TRN_SCALE: f64 = 0.5 / PI;
const RADIUS: f32 = 40.0;
const BLUR: f32 = 0.85;

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

fn get_point_template(radius: f32, blur_factor: f32) -> Vec<u32> {
    let size = 2.0 * radius;
    let mut dt = DrawTarget::new(size as i32, size as i32);
    if blur_factor == 1.0 {
        let mut pb = PathBuilder::new();
        pb.arc(radius, radius, radius, 0.0, 2.0 * PI as f32);
        pb.close();
        let path = pb.finish();
        dt.fill(
            &path,
            &Source::Solid(SolidSource {
                r: 0x0,
                g: 0x0,
                b: 0x0,
                a: 0xFF
            }),
            &DrawOptions::new()
        );
    } else {
        let gradient = Source::new_two_circle_radial_gradient(
            Gradient {
                stops: vec![
                    GradientStop {
                        position: 0.0,
                        color: Color::new(0xFF, 0x00, 0x00, 0x00)
                    },
                    GradientStop {
                        position: 1.0,
                        color: Color::new(0x00, 0x00, 0x00, 0x00)
                    }
                ],
            },
            Point::new(radius, radius),
            radius * blur_factor,
            Point::new(radius, radius),
            radius,
            Spread::Pad
        );
        dt.fill_rect(0.0, 0.0, size, size, &gradient, &DrawOptions::new());
    }
    dt.into_vec()
}

#[pyclass]
struct Renderer {
    data: HashMap<(String, String), Vec<Option<f32>>>,
    templates: HashMap<String, Vec<u32>>,
    gradient: Vec<u32>
}

#[pymethods]
impl Renderer {
    #[new]
    fn new() -> Self {
        let mut dt = DrawTarget::new(256, 1);
        dt.fill_rect(
            0.0,
            0.0,
            256.0,
            1.0,
            &Source::new_linear_gradient(
                Gradient {
                    stops: vec![
                        GradientStop {
                            position: 0.25,
                            color: Color::new(0xFF, 0x00, 0x00, 0xFF)
                        },
                        GradientStop {
                            position: 0.55,
                            color: Color::new(0xFF, 0x00, 0xFF, 0x00)
                        },
                        GradientStop {
                            position: 0.85,
                            color: Color::new(0xFF, 0xFF, 0xFF, 0x00)
                        },
                        GradientStop {
                            position: 1.0,
                            color: Color::new(0xFF, 0xFF, 0x00, 0x00)
                        }
                    ],
                },
                Point::new(0.0, 0.0),
                Point::new(256.0, 1.0),
                Spread::Pad
            ),
            &DrawOptions::new()
        );
        Self {
            data: HashMap::new(),
            templates: HashMap::new(),
            gradient: dt.into_vec()
        }
    }
    fn set_data(&mut self, data: HashMap<(String, String), Vec<Option<f32>>>) {
        self.data = data;
    }
    fn render(
        &mut self,
        py: Python,
        time: usize,
        center_lat: f64,
        center_lon: f64,
        zoom: i32,
        width: i32,
        height: i32
    ) -> PyResult<Py<PyBytes>> {
        let mut dt = DrawTarget::new(width, height);
        let mut values = HashMap::new();
        let mut max = None;
        let mut min = None;
        let blur = 1.0 - BLUR;
        let (center_x, center_y) = project(center_lat, center_lon, zoom);
        let corner_x = (center_x as f32) - (width as f32) / 2.0;
        let corner_y = (center_y as f32) - (height as f32) / 2.0;
        for ((lat, lon), values_over_time) in &self.data {
            if let Some(opt_value) = values_over_time.get(time) {
                values.insert((lat, lon), opt_value);
                if let Some(value) = opt_value {
                    if max.is_none() || value > max.unwrap() {
                        max = Some(value);
                    }
                    if min.is_none() || value < min.unwrap() {
                        min = Some(value);
                    }
                }
            } else {
                return Err(PyRuntimeError::new_err(format!("Invalid time {time} for coord \
                                                           ({lat}, {lon})")))
            }
        }
        for ((lat, lon), opt_value) in values {
            let value;
            if opt_value.is_none() {
                continue;
            } else {
                value = opt_value.unwrap();
            }
            let rs = format!("{RADIUS}");
            let tpl = self.templates.entry(rs).or_insert_with(|| get_point_template(RADIUS, blur));
            let size = 2.0 * RADIUS;
            let min = min.expect("How did we get here?");
            let max = max.expect("How did we get here?");
            let template_alpha = (value - min) / (max - min);
            let lat = lat.parse::<f64>().map_err(|err| PyRuntimeError::new_err(format!("{err}")))?;
            let lon = lon.parse::<f64>().map_err(|err| PyRuntimeError::new_err(format!("{err}")))?;
            let (x, y) = project(lat, lon, zoom);
            dt.draw_image_at(
                (x as f32) - corner_x - RADIUS,
                (y as f32) - corner_y - RADIUS,
                &Image {
                    width: size as i32,
                    height: size as i32,
                    data: tpl.as_slice()
                },
                &DrawOptions {
                    alpha: if template_alpha < 0.01 { 0.01 } else { template_alpha },
                    ..DrawOptions::new()
                }
            );
        }
        let mut img = dt.into_vec();
        let mut result = Vec::new();
        for pixel in &mut img {
            let alpha = (*pixel >> 24) as u8;
            if alpha == 0 {
                result.push((*pixel >> 16) as u8);
                result.push((*pixel >> 8) as u8);
                result.push(*pixel as u8);
            } else {
                let color = self.gradient[alpha as usize];
                result.push((color >> 16) as u8);
                result.push((color >> 8) as u8);
                result.push(color as u8);
            }
            result.push(alpha);
        }
        Ok(PyBytes::new(py, &result).into())
    }
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
    m.add_class::<Renderer>()?;
    Ok(())
}
