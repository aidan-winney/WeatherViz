mod config;
mod consts;
mod geo;
mod renderer;

use pyo3::prelude::*;

// TODO: refactor signatures for bound functions

#[pymodule]
#[pyo3(name = "renderer")]
fn weatherviz_backend(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(geo::coords, m)?)?;
    m.add_class::<renderer::Renderer>()?;
    Ok(())
}
