use crate::{config::Config, geo};
use std::collections::HashMap;
use pyo3::{prelude::*, exceptions::PyRuntimeError, types::PyBytes};

// TODO: implement bilinear interpolation as a temporary fix
// we assume that weather is a Gaussian process because we are cool like that
use friedrich::gaussian_process::GaussianProcess;

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
        //let grid_vec = Vec::new();
        //let xs = Vec::new();
        //let ys = Vec::new();
        let mut training_inputs = Vec::new();
        let mut training_outputs = Vec::new();
        let (center_x, center_y) = geo::project(center_lat, center_lon, zoom);
        let corner_x = center_x - (width as f64) / 2.0;
        let corner_y = center_y - (height as f64) / 2.0;
        for ((lat, lon), values_over_time) in &self.data {
            if let Some(Some(value)) = values_over_time.get(time) {
                let lat = lat.parse::<f64>()
                    .map_err(|_| PyRuntimeError::new_err(format!("Invalid latitude {lat}")))?;
                let lon = lon.parse::<f64>()
                    .map_err(|_| PyRuntimeError::new_err(format!("Invalid longitude {lon}")))?;
                let (x, y) = geo::project(lat, lon, zoom);
                //xs.push(x - corner_x);
                //ys.push(y - corner_y);
                //grid_vec.push(*value);
                training_inputs.push(vec![x - corner_x, y - corner_y]);
                training_outputs.push(*value);
            } else {
                return Err(PyRuntimeError::new_err(format!("Invalid time {time} for coord \
                                                           ({lat}, {lon})")))
            }
        }
        //let res = (self.data.len() as f64).sqrt() as i32;
        //let grid = ndarray::Array::from_shape_vec((res, res), grid_vec);
        let gp = GaussianProcess::default(training_inputs, training_outputs);
        let mut inputs = Vec::new();
        for j in 0..height {
            let j = j as f64;
            for i in 0..width {
                let i = i as f64;
                inputs.push(vec![i, j]);
            }
        }
        let outputs = gp.predict(&inputs);
        let min = outputs.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max = outputs.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
        let mut result = Vec::new();
        for output in outputs {
            let alpha_f = (output - min) / (max - min);
            let alpha = if alpha_f < 0.01 { 3 } else { (alpha_f * 255.0).round() as usize };
            let color = self.config.gradient[alpha];
            result.push((color >> 16) as u8);
            result.push((color >> 8) as u8);
            result.push(color as u8);
            result.push(alpha as u8);
        }
        Ok(PyBytes::new(py, &result).into())
    }
}
