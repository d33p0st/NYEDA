
use std::collections::HashSet;
use std::process::Command;
use pyo3::prelude::*;


#[pyclass]
#[derive(Debug)]
pub struct WindowsSRCD {
    sus: HashSet<String>,
    alr: HashSet<String>,
}


#[pymethods]
impl WindowsSRCD {
    #[new]
    fn new() -> Self {
        Self {
            sus: [
                "OBS Studio",
                "obs64",
                "obs32",
                "Bandicam",
                "bdcam",
                "Camtasia",
                "CamtasiaStudio",
                "ScreenRec",
                "ShareX",
                "XSplit",
                "FlashBack",
                "ScreenToGif",
                "Loom",
                "Xbox Game Bar",
                "GameBar",
                "SnippingTool",
                "ScreenClip",
                "Windows.Screen",
            ].iter().map(|s| s.to_string()).collect(),
            alr: HashSet::new(),
        }
    }

    fn _get_alr_processes(&self) -> HashSet<String> {
        let output = Command::new("tasklist")
            .arg("/FO")
            .arg("CSV")
            .arg("/NH")
            .output()
            .unwrap_or_else(|e| {
                eprintln!("💣🖥️ tasklist command failed! - {}", e);
                std::process::exit(1);
            });

        let out_str = String::from_utf8_lossy(&output.stdout);
        let processes: HashSet<String> = out_str
            .lines()
            .filter_map(|line| {
                let parts: Vec<&str> = line.split(',').collect();
                if parts.len() > 0 {
                    // Remove quotes from process name
                    Some(parts[0].trim_matches('"').to_string())
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
                let _ = Command::new("taskkill")
                    .arg("/F")
                    .arg("/IM")
                    .arg(&app)
                    .output()
                    .unwrap_or_else(|e| {
                        eprintln!("💣🖥️ taskkill command failure: {}", e);
                        std::process::exit(1);
                    });
            }
        }
        Ok(())
    }
}