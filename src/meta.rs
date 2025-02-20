use std::error::Error;
use mac_address::get_mac_address;
use sysinfo::{System, Disks};
use md5;
use whoami;
use serde::{Serialize, Deserialize};
use pyo3::prelude::*;

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct MetaData {
    pub version: u8,
    username: String,
    mac_addresses: Vec<String>,
    machine_id: Option<String>,
    disk_serials: Vec<String>,
    cpu_info: String,
    motherboard_serial: Option<String>,
    pub collective_hash: String,
}

impl<'a> FromPyObject<'a> for MetaData {
    fn extract_bound(ob: &Bound<'a, PyAny>) -> PyResult<Self> {
        let version: u8 = ob.getattr("version")?.extract()?;
        let username: String = ob.getattr("username")?.extract()?;
        let mac_addresses: Vec<String> = ob.getattr("mac_addresses")?.extract()?;
        let machine_id: Option<String> = ob.getattr("machine_id")?.extract()?;
        let disk_serials: Vec<String> = ob.getattr("disk_serials")?.extract()?;
        let cpu_info: String = ob.getattr("cpu_info")?.extract()?;
        let motherboard_serial: Option<String> = ob.getattr("motherboard_serial")?.extract()?;
        let collective_hash: String = ob.getattr("collective_hash")?.extract()?;
        Ok(MetaData{version, username, mac_addresses, machine_id, disk_serials, cpu_info, motherboard_serial, collective_hash})
    }
}

impl MetaData {
    fn get_mac_address() -> Result<Vec<String>, Box<dyn Error>> {
        let mac = get_mac_address()?;
        let addresses = match mac {
            Some(addr) => vec![addr.to_string()],
            None => Vec::new(),
        };
        Ok(addresses)
    }

    fn get_machine_id() -> Option<String> {
        #[cfg(target_os = "linux")]
        {
            std::fs::read_to_string("/etc/machine-id")
                .or_else(|_| std::fs::read_to_string("/var/lib/dbus/machine-id"))
                .ok()
                .map(|s| s.trim().to_string())
        }

        #[cfg(target_os = "windows")]
        {
            use winreg::enums::*;
            use winreg::RegKey;

            let hklm = RegKey::predef(HKEY_LOCAL_MACHINE);
            let key = hklm.open_subkey("SOFTWARE\\Microsoft\\Cryptography").ok()?;
            key.get_value("MachineGuid").ok()

        }

        #[cfg(target_os = "macos")]
        {
            let output = std::process::Command::new("ioreg")
                .args(["-rd1", "-c", "IOPlatformExpertDevice"])
                .output()
                .ok()?;

            let output = String::from_utf8_lossy(&output.stdout);
            output
                .lines()
                .find(|line| line.contains("IOPlatformUUID"))
                .and_then(|line| {
                    line.split('=')
                        .nth(1)
                        .map(|s| s.trim().trim_matches('"').to_string())
                })
        }
    }

    fn get_disk_serials() -> Vec<String> {
        let disks = Disks::new_with_refreshed_list();
        disks
            .iter()
            .filter_map(|disk| {
                let name = disk.name().to_str()?;
                if !name.is_empty() {
                    Some(name.to_string())
                } else {
                    None
                }
            })
            .collect()
    }

    fn get_cpu_info() -> Result<String, Box<dyn Error>> {
        let mut system = System::new();
        system.refresh_cpu_all();
        
        let cpu_vendor = system.cpus().first()
            .map(|cpu| cpu.vendor_id().to_string())
            .unwrap_or_else(|| "unknown".to_string());

        let cpu_brand = system.cpus().first()
            .map(|cpu| cpu.brand().to_string())
            .unwrap_or_else(|| "unknown".to_string());

        let cpu_count = system.cpus().len();

        let cpu_info = format!(
            "{}_{}_{:?}cores",
            cpu_brand,
            cpu_vendor,
            cpu_count
        );

        Ok(cpu_info)
    }

    fn get_motherboard_serial() -> Option<String> {
        #[cfg(target_os = "linux")]
        {
            std::process::Command::new("dmidecode")
                .args(["-s", "system-serial-number"])
                .output()
                .ok()
                .and_then(|ouput| String::from_utf8(output.stdout).ok())
                .map(|s| s.trim().to_string())
        }

        #[cfg(target_os = "windows")]
        {
            std::process::Command::new("wmic")
                .args(["baseboard", "get", "serialnumber"])
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .map(|s| s.trim().to_string())
        }

        #[cfg(target_os = "macos")]
        {
            std::process::Command::new("system_profiler")
                .args(["SPHardwareDataType"])
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .and_then(|output| {
                    output
                        .lines()
                        .find(|line| line.contains("Serial Number"))
                        .map(|line| line.split(':').nth(1).unwrap_or("").trim().to_string())
                })
        }
    }

    fn generate_unique_hash(&self) -> String {
        let mut combined = String::new();
        combined.push_str(&self.version.to_string());
        combined.push_str(&self.mac_addresses.join("_"));
        if let Some(id) = &self.machine_id {
            combined.push_str(id);
        }
        combined.push_str(&self.disk_serials.join("_"));
        combined.push_str(&self.cpu_info);
        if let Some(serial) = &self.motherboard_serial {
            combined.push_str(serial);
        }

        format!("{:?}", md5::compute(combined))
    }

    fn get_username() -> String {
        whoami::username()
    }

    pub fn new(version: u8) -> Self {
        let mut metadata = Self {
            version,
            username: Self::get_username(),
            mac_addresses: Self::get_mac_address().unwrap(),
            machine_id: Self::get_machine_id(),
            disk_serials: Self::get_disk_serials(),
            cpu_info: Self::get_cpu_info().unwrap(),
            motherboard_serial: Self::get_motherboard_serial(),
            collective_hash: String::new(),
        };

        metadata.collective_hash = metadata.generate_unique_hash();
        metadata
    }

    pub fn check(metadata: MetaData) -> bool {
        // check current system data with provided metadata
        MetaData::new(metadata.version) == metadata
    }

    pub fn check_hash(hash: &str, version: u8) -> bool {
        MetaData::new(version).collective_hash == hash
    }
}

