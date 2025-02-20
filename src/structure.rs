use std::collections::HashMap;
use std::io::{Cursor, Read};
use flate2::bufread::GzDecoder;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

#[pyclass]
pub struct Structure {}

#[pymethods]
impl Structure {
    #[staticmethod]
    fn get<'py>(data: Vec<u8>, py: Python<'py>) -> PyResult<pyo3::Bound<'py, PyDict>> {
        let dict = PyDict::new_bound(py);

        let cursor = Cursor::new(data);
        let tar = GzDecoder::new(cursor);
        let mut archive = tar::Archive::new(tar);

        let mut dir_contents: HashMap<String, Vec<String>> = HashMap::new();

        for entry in archive.entries()? {
            let mut entry = entry?;
            let path = entry.path()?;
            let path_str = path.to_string_lossy().into_owned();

            if !path_str.starts_with('.') {
                // Handle dirs
                if entry.header().entry_type().is_dir() {
                    dir_contents.insert(path_str.clone(), Vec::new());

                    // Add this directory to its parent's contents
                    if let Some(parent) = path.parent() {
                        if let Some(parent_str) = parent.to_str() {
                            if !parent_str.is_empty() {
                                dir_contents
                                    .entry(parent_str.to_string())
                                    .or_insert_with(Vec::new)
                                    .push(path_str.clone());
                            }
                        }
                    }

                    dict.set_item(&path_str, Vec::<String>::new())?;
                } else {
                    // Handle Files
                    // Add file to parent directory's contents
                    if let Some(parent) = path.parent() {
                        if let Some(parent_str) = parent.to_str() {
                            if !parent_str.is_empty() {
                                dir_contents
                                    .entry(parent_str.to_string())
                                    .or_insert_with(Vec::new)
                                    .push(path_str.clone());
                            }
                        }
                    }

                    // Read file contents
                    let mut buffer = Vec::new();
                    entry.read_to_end(&mut buffer)?;
                    
                    // Add file contents as PyBytes to dictionary
                    dict.set_item(&path_str, PyBytes::new_bound(py, &buffer))?;
                }
            }
        }

        // update directory entries with their contents
        for (dir_path, contents)  in dir_contents {
            if dict.contains(&dir_path)? {
                dict.set_item(&dir_path, contents)?;
            }
        }

        Ok(dict)
    }
}