use pyo3::prelude::*;

#[pyfunction]
fn add(left: usize, right: usize) -> usize {
    left + right
}

#[pymodule]
#[pyo3(name="renderer")]
fn renderer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add, m)?)?;
    Ok(())
}
