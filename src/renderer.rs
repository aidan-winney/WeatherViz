use crate::{config::Config, geo, interp::{Interpolator}};
use std::collections::{HashMap};
use pyo3::{prelude::*, exceptions::PyRuntimeError, types::PyBytes};

fn f32_to_usize(float: f32) -> usize {
    (float * 255.0).round() as usize
}

#[pyclass]
pub struct Renderer {
    pub data: HashMap<(String, String), Vec<Option<f64>>>,
    pub config: Config
}

#[pymethods]
impl Renderer {
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(Self {
            data: HashMap::new(),
            config: Config::new()?
        })
    }
    pub fn set_data(&mut self, data: HashMap<(String, String), Vec<Option<f64>>>) {
        self.data = data;
    }
    pub fn render(
        &mut self,
        py: Python,
        time: usize,
        center_lat: f64,
        center_lon: f64,
        zoom: i32,
        width: i32,
        height: i32
    ) -> PyResult<Py<PyBytes>> {
        let mut grid_map = HashMap::new();
        let mut xs = Vec::new();
        let mut ys = Vec::new();
        let (center_x, center_y) = geo::project(center_lat, center_lon, zoom);
        let corner_x = center_x - (width as f64) / 2.0;
        let corner_y = center_y - (height as f64) / 2.0;
        for ((lat, lon), values_over_time) in &self.data {
            if let Some(Some(value)) = values_over_time.get(time) {
                let lat = lat.parse::<f64>()
                    .map_err(|_| PyRuntimeError::new_err(format!("Invalid latitude {lat}")))?;
                let lon = lon.parse::<f64>()
                    .map_err(|_| PyRuntimeError::new_err(format!("Invalid longitude {lon}")))?;
                let (mut x, mut y) = geo::project(lat, lon, zoom);
                x -= corner_x;
                y -= corner_y;
                xs.push(x);
                ys.push(y);
                grid_map.insert((format!("{x}"), format!("{y}")), *value);
            } else {
                return Err(PyRuntimeError::new_err(format!("Invalid time {time} for coord \
                                                           ({lat}, {lon})")))
            }
        }
        xs.sort_by(|a, b| a.partial_cmp(b).unwrap());
        ys.sort_by(|a, b| a.partial_cmp(b).unwrap());
        xs.dedup();
        ys.dedup();
        let mut grid_vec = Vec::new();
        for x in &xs {
            for y in &ys {
                match grid_map.get(&(format!("{x}"), format!("{y}"))) {
                    Some(value) => grid_vec.push(*value),
                    _ => return Err(PyRuntimeError::new_err(format!("Invalid key ({x}, {y})")))
                }
            }
        }
        let x_len = xs.len();
        let y_len = ys.len();
        let grid = ndarray::Array::from_shape_vec((x_len, y_len), grid_vec)
            .map_err(|err| PyRuntimeError::new_err(format!("{err}")))?;
        if x_len == 0 || y_len == 0 {
            return Ok(PyBytes::new(py, &vec![0; (width * height * 4) as usize]).into())
        }
        let interpolator = Interpolator::new(xs, ys, grid);
        let mut outputs = Vec::new();
        for j in 0..height {
            let j = j as f64;
            let closest_y_is = interpolator.closest_y_indices(j);
            for i in 0..width {
                if interpolator.within_y_bounds(j) {
                    let i = i as f64;
                    let closest_x_is = interpolator.closest_x_indices(i);
                    if interpolator.within_x_bounds(i) {
                        outputs.push(Some(interpolator.interp(i, j, closest_x_is, closest_y_is)));
                    } else {
                        outputs.push(None);
                    }
                } else {
                    outputs.push(None);
                }
            }
        }
        let min = outputs.iter().fold(Some(f64::INFINITY), |a, &b| {
            match a {
                Some(a_val) => {
                    match b {
                        Some(b_val) => {
                            Some(a_val.min(b_val))
                        }
                        None => a
                    }
                }
                None => b
            }
        }).expect("How did we get here?");
        let max = outputs.iter().fold(Some(f64::NEG_INFINITY), |a, &b| {
            match a {
                Some(a_val) => {
                    match b {
                        Some(b_val) => {
                            Some(a_val.max(b_val))
                        }
                        None => a
                    }
                }
                None => b
            }
        }).expect("How did we get here?");
        let mut result = Vec::new();
        for output in &outputs {
            match output {
                Some(value) => {
                    let scaled = (value - min) / (max - min);
                    let alpha = if scaled < 0.01 { 3 } else { f32_to_usize(scaled as f32) };
                    let color = self.config.gradient[alpha];
                    result.push((color >> 16) as u8);
                    result.push((color >> 8) as u8);
                    result.push(color as u8);
                    let opacity = f32_to_usize(self.config.opacity);
                    let final_alpha = if opacity > 0 {
                        opacity
                    } else {
                        let max_opacity = f32_to_usize(self.config.max_opacity);
                        let min_opacity = f32_to_usize(self.config.min_opacity);
                        if alpha < max_opacity {
                            if alpha < min_opacity {
                                min_opacity
                            } else {
                                alpha
                            }
                        } else {
                            max_opacity
                        }
                    };
                    result.push(final_alpha as u8);
                }
                None => {
                    result.push(0);
                    result.push(0);
                    result.push(0);
                    result.push(0);
                }
            }    
        }
        Ok(PyBytes::new(py, &result).into())
    }
}
