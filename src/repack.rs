use std::fs::{self, File};
use std::io::{self, Read, Write, Cursor};
use flate2::bufread::GzDecoder;
use rustypath::RPath;
use flate2::write::GzEncoder;
use flate2::Compression;
use tar::Builder;
use serde::{Serialize, Deserialize};
use bincode::{serialize, deserialize};
use pyo3::prelude::*;
use crate::meta::MetaData;

const MAGIC: &[u8] = b"CODENAME-NT";

// helper functions
fn add_dir_to_archive<W: Write>(builder: &mut Builder<W>, source: RPath, base: RPath) -> io::Result<()> {
    let _base = base.clone();
    for entry in source.read_dir().expect("Failed to read source directory!") {
        let entry = entry?;
        let path = entry.path();
        let relative = path.strip_prefix(_base.clone().convert_to_pathbuf())
            .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "Invalid Path"))?;

        if path.is_dir() {
            add_dir_to_archive(builder, RPath::from(path), _base.clone())?;
        } else {
            let mut file = File::open(&path)?;
            let mut contents = Vec::new();
            file.read_to_end(&mut contents)?;

            let mut header = tar::Header::new_gnu();
            header.set_size(contents.len() as u64);
            
            header.set_mode(0o644);

            builder.append_data(&mut header, relative, Cursor::new(contents))?;
        }
    }

    Ok(())
}


#[pyclass]
#[derive(Serialize, Deserialize)]
pub struct Bundle {
    metadata: MetaData,
    data: Vec<u8>,
}

impl<'a> FromPyObject<'a> for Bundle {
    fn extract_bound(ob: &Bound<'a, PyAny>) -> PyResult<Self> {
        let metadata: MetaData = ob.getattr("metadata")?.extract()?;
        let data: Vec<u8> = ob.getattr("data")?.extract()?;
        Ok(Bundle{metadata, data})
    }
}

#[pymethods]
impl Bundle {
    #[new]
    fn new() -> Self {
        Bundle {
            metadata: MetaData::new(1),
            data: Vec::new()
        }
    }

    fn _create_archive_data(&mut self, source: &str) -> PyResult<Vec<u8>> {
        let mut buffer = Vec::new();
        
        {   
            let gz_encoder = GzEncoder::new(&mut buffer, Compression::best());
            let mut builder = Builder::new(gz_encoder);
            add_dir_to_archive(&mut builder, RPath::from(source).expand(), RPath::from(source).expand())?;
            builder.finish()?;
        }

        Ok(buffer)
    }

    fn create(&mut self, source: &str, version: u8) -> PyResult<Vec<u8>> {
        // script path must be relative here. (/script => script)
        // where / represents the source dir.
        // check if the script exists inside the dir

        // create archive data
        let archive = self._create_archive_data(source)?;

        // create package
        let package = Bundle {
            metadata: self.metadata.clone(),
            data: archive.clone(),
        };

        // Serialize the package
        let mut output = Vec::new();
        output.extend_from_slice(MAGIC);
        output.push(version);

        let serialized = serialize(&package)
            .map_err(|e| pyo3::exceptions::PyException::new_err(format!("Failed to serialize the package and metadata: {}", e)))?;

        output.extend_from_slice(&(serialized.len() as u64).to_le_bytes());
        output.extend_from_slice(&serialized);

        Ok(output)

    }
}


#[pyclass]
pub struct Dismantle {
    data: Vec<u8>,
    #[allow(dead_code)]
    metadata: MetaData
}

#[pymethods]
impl Dismantle {
    #[new]
    fn new(data: Vec<u8>) -> PyResult<Self> {
        if data.len() < MAGIC.len() + 1 + 8 {
            return Err(pyo3::exceptions::PyUserWarning::new_err(format!("No Content Found.")))
        }

        if &data[..MAGIC.len()] != MAGIC {
            return Err(pyo3::exceptions::PyUserWarning::new_err(format!("Content is not compatible with system.")))
        }

        let _version: u8 = data[MAGIC.len()];

        let size_start: usize = MAGIC.len() + 1;
        let size_end: usize = size_start + 8;
        let _package_size = u64::from_le_bytes(data[size_start..size_end].try_into().unwrap()) as usize;

        let package: Bundle = deserialize(&data[size_end..])
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid Data Found: Cannot separate metadata: {}", e)))?;


        if _version != package.metadata.version {
            return Err(pyo3::exceptions::PyUserWarning::new_err(format!("Content is not compatible with system. Version mismatch.")))
        }

        Ok(Self{
            data: package.data.clone(),
            metadata: package.metadata.clone(),
        })
    }

    fn export(&self, output: &str) -> PyResult<bool> {
        fs::create_dir_all(output)?;

        let cursor = Cursor::new(self.data.clone());
        let tar = GzDecoder::new(cursor);
        let mut archive = tar::Archive::new(tar);
        archive.set_preserve_permissions(true);
        archive.set_unpack_xattrs(true);
        archive.unpack(output)?;
        Ok(true)
    }

    fn get(&self) -> PyResult<Vec<u8>> {
        Ok(self.data.clone())
    }

    fn get_meta(&self) -> PyResult<String> {
        Ok(self.metadata.collective_hash.clone())
    }
}

#[pyclass]
pub struct Validation {}

#[pymethods]
impl Validation {
    #[new]
    fn new() -> Self{
        Self{}
    }

    #[staticmethod]
    pub fn validate_meta(data: Vec<u8>) -> PyResult<bool> {
        if data.len() < MAGIC.len() + 1 + 8 {
            return Err(pyo3::exceptions::PyUserWarning::new_err(format!("No Content Found.")))
        }

        if &data[..MAGIC.len()] != MAGIC {
            return Err(pyo3::exceptions::PyUserWarning::new_err(format!("Content is not compatible with system.")))
        }

        let _version: u8 = data[MAGIC.len()];

        let size_start: usize = MAGIC.len() + 1;
        let size_end: usize = size_start + 8;
        let package_size: usize = u64::from_le_bytes(data[size_start..size_end].try_into().unwrap()) as usize;

        let package: Bundle = deserialize(&data[size_end..size_end + package_size])
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid Data Found: Cannot separate metadata: {}", e)))?;

        if _version != package.metadata.version {
            return Err(pyo3::exceptions::PyUserWarning::new_err(format!("Content is not compatible with system. Version mismatch.")))
        }

        Ok(MetaData::check(package.metadata))
    }

    #[staticmethod]
    pub fn validate_meta_hash(version: u8, hash: &str) -> PyResult<bool> {
        Ok(MetaData::check_hash(hash, version))
    }
}