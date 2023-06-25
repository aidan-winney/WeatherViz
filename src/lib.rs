use pyo3::prelude::*;
use reqwest;
use pyo3::exceptions::PyRuntimeError;
use pyo3::types::IntoPyDict;

#[pyfunction]
fn get_data(py: Python) -> PyResult<PyObject> {
    let url = "https://archive-api.open-meteo.com/v1/archive?latitude=29.68&longitude=-82.34&start_date=2023-05-26&end_date=2023-06-09&hourly=temperature_2m&min=2023-05-26&max=2023-06-09";

    let client = reqwest::blocking::Client::new();
    let response = client.get(url).send().map_err(|err| PyRuntimeError::new_err(format!("{}", err)))?;

    if response.status().is_success() {
        let text = response.text().map_err(|err| PyRuntimeError::new_err(format!("{}", err)))?;
        let data: serde_json::Value = serde_json::from_str(&text).map_err(|err| PyRuntimeError::new_err(format!("{}", err)))?;
        
        let locals = [("data", data.to_string())].into_py_dict(py);
        py.run("import json; result = json.loads(data)", Some(locals), None)?;

        let python_data = locals.get_item("result").ok_or_else(|| PyRuntimeError::new_err("Failed to get 'result'"))?.to_object(py);

        Ok(python_data)
    } else {
        Err(PyRuntimeError::new_err(format!("It didn't work. Status code: {}", response.status())))
    }
}

#[pymodule]
#[pyo3(name = "renderer")]
fn renderer(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_data, m)?)?;
    Ok(())
}
