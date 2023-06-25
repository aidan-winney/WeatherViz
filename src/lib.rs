use pyo3::prelude::*;
use reqwest;
use pyo3::exceptions::PyRuntimeError;

#[pyfunction]
fn get_data(py: Python) -> PyResult<()> {
    let url = "https://archive-api.open-meteo.com/v1/archive?latitude=29.68&longitude=-82.34&start_date=2023-05-26&end_date=2023-06-09&hourly=temperature_2m&min=2023-05-26&max=2023-06-09";

    let client = reqwest::blocking::Client::new();
    let response = client.get(url).send().map_err(|err| PyRuntimeError::new_err(format!("{}", err)))?;

    if response.status().is_success() {
        println!("It worked");
        let text = response.text().map_err(|err| PyRuntimeError::new_err(format!("{}", err)))?;
        let data: serde_json::Value = serde_json::from_str(&text).map_err(|err| PyRuntimeError::new_err(format!("{}", err)))?;
        if let Some(hourly) = data.get("hourly") {
            println!("{}", hourly);
        } else {
            println!("'hourly' data not found");
        }
    } else {
        println!("It didn't work. Status code: {}", response.status());
    }

    Ok(())
}

#[pymodule]
#[pyo3(name = "renderer")]
fn renderer(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_data, m)?)?;
    Ok(())
}
