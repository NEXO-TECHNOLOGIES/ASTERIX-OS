//! ASTERIX OS — Hardware Topology, GPU Detection & Multi-OS Reconnaissance

use std::process::Command;
use crate::c_kernel_bindings;

#[derive(Debug, Clone)]
pub struct GpuDevice {
    pub name: String,
    pub vram_mb: u64,
    pub device_type: String,
}

#[derive(Debug, Clone)]
pub struct NetworkInterface {
    pub ip: String,
    pub is_direct_cable: bool,
    pub description: String,
}

#[derive(Debug, Clone)]
pub struct LocalHardwareProfile {
    pub node_id: String,
    pub hostname: String,
    pub os_name: String,
    pub os_family: String, // "Windows" or "Linux" or "macOS"
    pub cpu_arch: String,
    pub cpu_cores: usize,
    pub has_avx2: bool,
    pub total_ram_mb: u64,
    pub free_ram_mb: u64,
    pub gpus: Vec<GpuDevice>,
    pub interfaces: Vec<NetworkInterface>,
    pub primary_ip: String,
    pub estimated_tflops: f64,
}

pub fn detect_os_details() -> (String, String) {
    if cfg!(windows) {
        let mut ver_str = "Windows 10/11".to_string();
        if let Ok(out) = Command::new("cmd").args(&["/c", "ver"]).output() {
            let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
            if !s.is_empty() {
                ver_str = s;
            }
        }
        (ver_str, "Windows".to_string())
    } else if cfg!(target_os = "macos") {
        ("macOS".to_string(), "macOS".to_string())
    } else {
        // Linux
        let mut distro = "Linux Generic".to_string();
        if let Ok(content) = std::fs::read_to_string("/etc/os-release") {
            for line in content.lines() {
                if line.starts_with("PRETTY_NAME=") {
                    distro = line
                        .trim_start_matches("PRETTY_NAME=")
                        .trim_matches('"')
                        .to_string();
                    break;
                }
            }
        }
        (distro, "Linux".to_string())
    }
}

pub fn detect_gpus() -> Vec<GpuDevice> {
    let mut gpus = Vec::new();

    // 1. Check NVIDIA SMI (CUDA)
    if let Ok(out) = Command::new("nvidia-smi")
        .args(&["--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
        .output()
    {
        if out.status.success() {
            let text = String::from_utf8_lossy(&out.stdout);
            for line in text.lines() {
                let parts: Vec<&str> = line.split(',').map(|s| s.trim()).collect();
                if !parts.is_empty() && !parts[0].is_empty() {
                    let name = format!("NVIDIA {}", parts[0]);
                    let vram = parts.get(1).and_then(|v| v.parse::<u64>().ok()).unwrap_or(0);
                    gpus.push(GpuDevice {
                        name,
                        vram_mb: vram,
                        device_type: "NVIDIA CUDA Hardware Accelerator".to_string(),
                    });
                }
            }
        }
    }

    // 2. Windows Video Controller via PowerShell if no NVIDIA or supplemental
    if cfg!(windows) && gpus.is_empty() {
        if let Ok(out) = Command::new("powershell")
            .args(&[
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
            ])
            .output()
        {
            let text = String::from_utf8_lossy(&out.stdout);
            for line in text.lines() {
                let name = line.trim();
                if !name.is_empty() {
                    gpus.push(GpuDevice {
                        name: name.to_string(),
                        vram_mb: 1024,
                        device_type: "DirectX / Win32 VideoController".to_string(),
                    });
                }
            }
        }
    }

    // 3. AMD ROCm on Linux
    if std::path::Path::new("/dev/kfd").exists() {
        gpus.push(GpuDevice {
            name: "AMD ROCm OpenCL Accelerator".to_string(),
            vram_mb: 4096,
            device_type: "AMD ROCm / HIP".to_string(),
        });
    }

    // 4. Default fallback: CPU SIMD vector accelerator
    if gpus.is_empty() {
        gpus.push(GpuDevice {
            name: "x86_64 AVX2/SSE SIMD Vector Unit".to_string(),
            vram_mb: 2048,
            device_type: "CPU Vector Accelerator".to_string(),
        });
    }

    gpus
}

pub fn detect_network_interfaces() -> Vec<NetworkInterface> {
    let mut list = Vec::new();

    #[cfg(windows)]
    {
        if let Ok(out) = Command::new("powershell")
            .args(&[
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_NetworkAdapterConfiguration -Filter 'IPEnabled=True' | Select-Object -ExpandProperty IPAddress",
            ])
            .output()
        {
            let text = String::from_utf8_lossy(&out.stdout);
            for line in text.lines() {
                let ip = line.trim();
                if !ip.is_empty() && !ip.contains(':') && !ip.starts_with("127.") {
                    let is_cable = ip.starts_with("169.254.");
                    let desc = if is_cable {
                        "Direct Link-Local (Plugged Cable)"
                    } else {
                        "LAN / Network Adapter"
                    };
                    list.push(NetworkInterface {
                        ip: ip.to_string(),
                        is_direct_cable: is_cable,
                        description: desc.to_string(),
                    });
                }
            }
        }
    }

    if list.is_empty() {
        list.push(NetworkInterface {
            ip: "127.0.0.1".to_string(),
            is_direct_cable: false,
            description: "Loopback Interface".to_string(),
        });
    }

    list
}

pub fn profile_local_hardware() -> LocalHardwareProfile {
    let (os_name, os_family) = detect_os_details();
    let hostname = match std::env::var("COMPUTERNAME").or_else(|_| std::env::var("HOSTNAME")) {
        Ok(h) => h,
        Err(_) => "ASTERIX-HOST".to_string(),
    };

    let node_id = format!(
        "ax-{}-{}",
        os_family.to_lowercase(),
        (hostname.len() * 31 + 1047) % 90000 + 10000
    );

    let cpu_cores = std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(4);

    let (total_ram_mb, free_ram_mb) = c_kernel_bindings::get_kernel_memory_mb();
    let gpus = detect_gpus();
    let interfaces = detect_network_interfaces();
    let primary_ip = interfaces[0].ip.clone();

    #[cfg(target_arch = "x86_64")]
    let has_avx2 = is_x86_feature_detected!("avx2");
    #[cfg(not(target_arch = "x86_64"))]
    let has_avx2 = false;

    // Theoretical TFLOPS estimate
    let cpu_tflops = (cpu_cores as f64) * (if has_avx2 { 0.065 } else { 0.035 });
    let gpu_tflops = gpus.iter().map(|g| {
        if g.name.to_lowercase().contains("rtx") || g.name.to_lowercase().contains("nvidia") {
            6.5
        } else if g.name.to_lowercase().contains("radeon") {
            4.0
        } else {
            1.5
        }
    }).sum::<f64>();
    let estimated_tflops = ((cpu_tflops + gpu_tflops) * 100.0).round() / 100.0;

    LocalHardwareProfile {
        node_id,
        hostname,
        os_name,
        os_family,
        cpu_arch: std::env::consts::ARCH.to_string(),
        cpu_cores,
        has_avx2,
        total_ram_mb,
        free_ram_mb,
        gpus,
        interfaces,
        primary_ip,
        estimated_tflops,
    }
}
