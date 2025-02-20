
#[cfg(target_os = "macos")]
use std::collections::HashSet;
#[cfg(target_os = "macos")]
use std::process::Command;
#[cfg(target_os = "macos")]
use pyo3::prelude::*;

#[cfg(target_os = "macos")]
#[pyclass]
#[derive(Debug)]
pub struct MacosSRCD {
    sus: HashSet<String>,
    alr: HashSet<String>,
}

#[cfg(target_os = "macos")]
#[pymethods]
impl MacosSRCD {
    #[new]
    fn new() -> Self {
        Self {
            sus: [
                "QuickTime Player",
                "QuickTimePlayer",
                "screencapture",
                "ScreenFlow",
                "Snip",
                "obs",
                "OBS",
                "Camtasia",
                "Loom",
                "Screen Recording",
                "Screenshot",
                "com.apple.screencapture",
                "com.apple.QuickTimePlayerX",
            ].iter().map(|s| s.to_string()).collect(),
            alr: HashSet::new(),
        }
    }

    fn _get_alr_processes(&self) -> HashSet<String> {
        let output = Command::new("ps")
            .arg("aux")
            .output()
            .unwrap_or_else(|e| {
                eprintln!("💣🖥️ ps command not found! - {}", e);
                std::process::exit(1);
            });

        let out_str = String::from_utf8_lossy(&output.stdout);
        let processes: HashSet<String> = out_str
            .lines()
            .filter_map(|line| {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() > 10 {
                    Some(parts[10].to_string()) // process name
                } else {
                    None
                }
            }).collect();
        
        processes
    }

    fn _detect_new(&mut self) -> bool {
        let current_apps = self._get_alr_processes();

        let new_sus_apps: Vec<String> = current_apps
            .difference(&self.alr)
            .filter(|app| self.sus.iter().any(|sus| app.contains(sus)))
            .cloned()
            .collect();
        self.alr = current_apps;

        if !new_sus_apps.is_empty() {
            for app in &new_sus_apps {
                println!("⚠️ Warning: New screen recording app detected -> {}", app);
                return true;
            }
        }

        false
    }

    fn detect(&mut self) -> PyResult<bool> {
        self.alr = self._get_alr_processes();
        Ok(self._detect_new())
    }

    fn kill(&mut self) -> PyResult<()> {
        let running_apps = self._get_alr_processes();

        for app in running_apps {
            if self.sus.iter().any(|sus| app.contains(sus)) {
                println!("❌ Terminating suspicious app: {}", app);
                let _ = Command::new("pkill")
                    .arg("-f")
                    .arg(&app)
                    .output()
                    .unwrap_or_else(|e| {
                        eprintln!("💣🖥️ pkill command failure: {}", e);
                        std::process::exit(1);
                    });
            }
        }
        Ok(())
    }
}