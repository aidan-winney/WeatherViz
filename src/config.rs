use std::{fs, convert::TryFrom};
use pyo3::{prelude::*, exceptions::PyRuntimeError};
use toml::{Table, Value};
use raqote::*;

fn i64_to_u8(int: &i64) -> Result<u8, PyErr> {
    u8::try_from(*int).map_err(|_| PyRuntimeError::new_err(format!("Invalid color component \
                                                                        {int}")))
}

#[pyclass]
pub struct Config {
    pub opacity: f32,
    pub max_opacity: f32,
    pub min_opacity: f32,
    pub gradient: Vec<u32>
}

#[pymethods]
impl Config {
    #[new]
    pub fn new() -> PyResult<Self> {
        let opt_table = if let Ok(fstr) = fs::read_to_string("config.toml") {
            Some(fstr.parse::<Table>().map_err(|err| PyRuntimeError::new_err(format!("{err}")))?)
        } else {
            None
        };
        Ok(Self {
            opacity: match opt_table.as_ref().map(|t| t.get("opacity")) {
                Some(Some(Value::Float(float))) => *float as f32,
                _ => 0.0
            },
            max_opacity: match opt_table.as_ref().map(|t| t.get("max_opacity")) {
                Some(Some(Value::Float(float))) => *float as f32,
                _ => 1.0
            },
            min_opacity: match opt_table.as_ref().map(|t| t.get("min_opacity")) {
                Some(Some(Value::Float(float))) => *float as f32,
                _ => 0.0
            },
            gradient: {
                let mut dt = DrawTarget::new(256, 1);
                let grad = Source::new_linear_gradient(
                    Gradient {
                        stops: 'stops: {
                            let default = vec![
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
                            ];
                            match opt_table.as_ref().map(|t| t.get("gradient")) {
                                Some(Some(Value::Table(table))) => {
                                    let mut result = Vec::new();
                                    for (int, ivalue) in table {
                                        if !ivalue.is_table() {
                                            break 'stops default
                                        }
                                        for (frac, fvalue) in ivalue.as_table().unwrap() {
                                            let parse_res = format!("{int}.{frac}").parse::<f32>();
                                            let position = match parse_res {
                                                Ok(pos) => pos,
                                                _ => break 'stops default
                                            };
                                            match fvalue.as_table() {
                                                Some(ftable) => {
                                                    let r = match ftable.get("r") {
                                                        Some(Value::Integer(i)) => i64_to_u8(i)?,
                                                        _ => break 'stops default
                                                    };
                                                    let g = match ftable.get("g") {
                                                        Some(Value::Integer(i)) => i64_to_u8(i)?,
                                                        _ => break 'stops default
                                                    };
                                                    let b = match ftable.get("b") {
                                                        Some(Value::Integer(i)) => i64_to_u8(i)?,
                                                        _ => break 'stops default
                                                    };
                                                    result.push(
                                                        GradientStop {
                                                            position,
                                                            color: Color::new(0xFF, r, g, b)
                                                        }
                                                    );
                                                }
                                                _ => break 'stops default
                                            }
                                        }
                                    }
                                    result
                                }
                                _ => default
                            }
                        }
                    },
                    Point::new(0.0, 0.0),
                    Point::new(256.0, 1.0),
                    Spread::Pad
                );
                dt.fill_rect(
                    0.0,
                    0.0,
                    256.0,
                    1.0,
                    &grad,
                    &DrawOptions::new()
                );
                dt.into_vec()
            }
        })
    }
}
