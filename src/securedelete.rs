
use rand::{distr::Alphanumeric, Rng};
use pyo3::prelude::*;
use rustypath::RPath;
use std::path::Path;

// Self Destruct Code
struct SelfDestructUtils {}

impl SelfDestructUtils {
    #[allow(dead_code)]
    fn get_random_name(len: usize) -> String {
        use rand::rng;
        rng()
            .sample_iter(&Alphanumeric)
            .take(len)
            .map(char::from)
            .collect()
    }

    #[allow(dead_code)]
    fn get_temp_dir() -> RPath {
        if cfg!(windows) {
            std::env::var("TEMP")
                .or_else(|_| std::env::var("TMP"))
                .map(RPath::from)
                .unwrap_or_else(|_| RPath::from("C:\\Windows\\Temp"))
        } else {
            RPath::from("/tmp")
        }
    }

    fn secure_delete<P: AsRef<Path>>(path: P, overwrites: usize) -> std::io::Result<()> {
        use std::io::{Write, Seek, SeekFrom};
        
        // If it's a directory, handle it recursively
        if path.as_ref().is_dir() {
            return Self::secure_delete_dir(path, overwrites);
        }

        let file_size = path.as_ref().metadata()?.len();
        // open the file for overwriting
        let mut file = std::fs::OpenOptions::new()
            .write(true)
            .open(&path)?;

        // Multiple writing patterns for security
        let patterns: Vec<u8> = vec![0x00, 0xFF, 0xAA, 0x55];
        
        // perform multiple overwrites
        for i in 0..overwrites {
            let index = i % patterns.len();
            let pattern = patterns[index];
            file.seek(SeekFrom::Start(0))?;
            let buffer = vec![pattern; 4096];
            let mut remaining = file_size;
            
            while remaining > 0 {
                let write_size = std::cmp::min(remaining, 4096) as usize;
                file.write_all(&buffer[..write_size])?;
                remaining -= write_size as u64;
            }
            file.flush()?;
            #[cfg(unix)]
            file.sync_all()?;
        }
        
        drop(file);
        std::fs::remove_file(path)?;
        Ok(())
    }

    fn secure_delete_dir<P: AsRef<Path>>(path: P, overwrites: usize) -> std::io::Result<()> {
        let path = path.as_ref();
        
        // Ensure the path exists and is a directory
        if !path.is_dir() {
            return Ok(());
        }

        // First, recursively process all contents
        for entry in std::fs::read_dir(path)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_dir() {
                Self::secure_delete_dir(&path, overwrites)?;
            } else {
                Self::secure_delete(&path, overwrites)?;
            }
        }

        // After all contents are securely deleted, remove the empty directory
        std::fs::remove_dir(path)?;
        Ok(())
    }
}

#[pyclass]
pub struct SecureDelete {}

#[pymethods]
impl SecureDelete {
    #[new]
    fn new(path: &str, overwrites: usize) -> PyResult<Self> {
        let path = RPath::from(path).convert_to_pathbuf();
        SelfDestructUtils::secure_delete(path, overwrites).unwrap_or_else(|_e|{
            eprintln!("{}", _e);
        });
        Ok(Self {})
    }
}