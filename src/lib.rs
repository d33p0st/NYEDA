
use pyo3::prelude::*;

mod securedelete;
mod structure;
mod repack;
mod macos;
mod meta;

#[pymodule]
#[pyo3(name="sharedobject")]
fn sharedobject(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    let validation = PyModule::new_bound(py, "validation")?;
    validation.add_class::<repack::Validation>()?;
    m.add_submodule(&validation)?;

    let bundle = PyModule::new_bound(py, "bundle")?;
    bundle.add_class::<repack::Bundle>()?;
    bundle.add_class::<repack::Dismantle>()?;
    bundle.add_class::<structure::Structure>()?;
    m.add_submodule(&bundle)?;

    let secure_delete = PyModule::new_bound(py, "secure_delete")?;
    secure_delete.add_class::<securedelete::SecureDelete>()?;
    m.add_submodule(&secure_delete)?;

    let macos = PyModule::new_bound(py, "macos")?;
    macos.add_class::<macos::MacosSRCD>()?;
    m.add_submodule(&macos)?;

    Ok(())
}