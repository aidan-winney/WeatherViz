// Adapted from https://libreda.org/doc/interp/interp2d/index.html

use std::cmp::Ordering;
use ndarray::Array2;

fn closest_indices(vec: &Vec<f64>, val: f64) -> (usize, usize) {
    let idx = match vec.binary_search_by(|a| {
        if *a < val {
            Ordering::Less
        } else if *a == val {
            Ordering::Equal
        } else {
            Ordering::Greater
        }
    }) {
        Ok(i) => i,
        Err(i) => i.max(1) - 1
    };
    if idx == vec.len() - 1 {
        (idx - 1, idx)
    } else {
        (idx, idx + 1)
    }
}

pub struct Interpolator {
    xs: Vec<f64>,
    ys: Vec<f64>,
    z: Array2<f64>,
    x_min: f64,
    x_max: f64,
    y_min: f64,
    y_max: f64
}

impl Interpolator {
    pub fn new(xs: Vec<f64>, ys: Vec<f64>, z: Array2<f64>) -> Self {
        let x_min = xs[0];
        let x_max = xs[xs.len() - 1];
        let y_min = ys[0];
        let y_max = ys[ys.len() - 1];
        Self { xs, ys, z, x_min, x_max, y_min, y_max }
    }
    pub fn closest_x_indices(&self, x: f64) -> (usize, usize) {
        closest_indices(&self.xs, x)
    }
    pub fn closest_y_indices(&self, y: f64) -> (usize, usize) {
        closest_indices(&self.ys, y)
    }
    pub fn within_x_bounds(&self, x: f64) -> bool {
        self.x_min <= x && x <= self.x_max
    }
    pub fn within_y_bounds(&self, y: f64) -> bool {
        self.y_min <= y && y <= self.y_max
    }
    pub fn interp(
        &self,
        x: f64,
        y: f64,
        (x0_index, x1_index): (usize, usize),
        (y0_index, y1_index): (usize, usize)
    ) -> f64 {
        let x0 = self.xs[x0_index];
        let x1 = self.xs[x1_index];
        let y0 = self.ys[y0_index];
        let y1 = self.ys[y1_index];
        let v00 = self.z[[x0_index, y0_index]];
        let v10 = self.z[[x1_index, y0_index]];
        let v01 = self.z[[x0_index, y1_index]];
        let v11 = self.z[[x1_index, y1_index]];
        let alpha = (x - x0) / (x1 - x0);
        let beta = (y - y0) / (y1 - y0);
        v00 + (v10 - v00) * alpha + (v01 - v00) * beta + (v00 + v11 - v10 - v01) * alpha * beta
    }
}
