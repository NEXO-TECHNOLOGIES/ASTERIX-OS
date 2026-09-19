//! ASTERIX OS — Native C / Win32 & POSIX Kernel Bindings
//! Enforces active desktop priority governance (BELOW_NORMAL_PRIORITY_CLASS)
//! and fires native OS notifications when a new laptop/PC is detected.

#[cfg(windows)]
mod win32 {
    use std::ffi::c_void;
    use std::os::raw::{c_int, c_uint};

    pub const BELOW_NORMAL_PRIORITY_CLASS: u32 = 0x00004000;
    pub const MB_YESNO: c_uint = 0x00000004;
    pub const MB_ICONQUESTION: c_uint = 0x00000020;
    pub const MB_TOPMOST: c_uint = 0x00040000;
    pub const IDYES: c_int = 6;

    #[repr(C)]
    pub struct MemoryStatusEx {
        pub dw_length: u32,
        pub dw_memory_load: u32,
        pub ull_total_phys: u64,
        pub ull_avail_phys: u64,
        pub ull_total_page_file: u64,
        pub ull_avail_page_file: u64,
        pub ull_total_virtual: u64,
        pub ull_avail_virtual: u64,
        pub ull_avail_extended_virtual: u64,
    }

    #[link(name = "kernel32")]
    extern "system" {
        pub fn GetCurrentProcess() -> *mut c_void;
        pub fn SetPriorityClass(h_process: *mut c_void, dw_priority_class: u32) -> i32;
        pub fn GlobalMemoryStatusEx(lp_buffer: *mut MemoryStatusEx) -> i32;
    }

    #[link(name = "user32")]
    extern "system" {
        pub fn MessageBoxW(
            h_wnd: *mut c_void,
            lp_text: *const u16,
            lp_caption: *const u16,
            u_type: c_uint,
        ) -> c_int;
    }
}

/// Sets process priority to Below-Normal so active Windows gaming/apps are 100% smooth
pub fn engage_desktop_governor() -> bool {
    #[cfg(windows)]
    unsafe {
        let handle = win32::GetCurrentProcess();
        let ok = win32::SetPriorityClass(handle, win32::BELOW_NORMAL_PRIORITY_CLASS);
        ok != 0
    }
    #[cfg(not(windows))]
    unsafe {
        // POSIX nice(10)
        let _ = libc_nice(10);
        true
    }
}

#[cfg(not(windows))]
extern "C" {
    fn nice(inc: i32) -> i32;
}

#[cfg(not(windows))]
fn libc_nice(inc: i32) -> i32 {
    unsafe { nice(inc) }
}

/// Retrieves real-time kernel memory telemetry via Win32 or /proc/meminfo
pub fn get_kernel_memory_mb() -> (u64, u64) {
    #[cfg(windows)]
    unsafe {
        let mut status = win32::MemoryStatusEx {
            dw_length: std::mem::size_of::<win32::MemoryStatusEx>() as u32,
            dw_memory_load: 0,
            ull_total_phys: 0,
            ull_avail_phys: 0,
            ull_total_page_file: 0,
            ull_avail_page_file: 0,
            ull_total_virtual: 0,
            ull_avail_virtual: 0,
            ull_avail_extended_virtual: 0,
        };
        if win32::GlobalMemoryStatusEx(&mut status) != 0 {
            let total = status.ull_total_phys / (1024 * 1024);
            let free = status.ull_avail_phys / (1024 * 1024);
            return (total, free);
        }
    }
    #[cfg(not(windows))]
    {
        if let Ok(content) = std::fs::read_to_string("/proc/meminfo") {
            let mut total = 0;
            let mut free = 0;
            for line in content.lines() {
                if line.starts_with("MemTotal:") {
                    if let Some(val) = line.split_whitespace().nth(1) {
                        total = val.parse::<u64>().unwrap_or(0) / 1024;
                    }
                } else if line.starts_with("MemAvailable:") {
                    if let Some(val) = line.split_whitespace().nth(1) {
                        free = val.parse::<u64>().unwrap_or(0) / 1024;
                    }
                }
            }
            if total > 0 {
                return (total, free);
            }
        }
    }
    (8192, 4096)
}

/// Converts string to UTF-16 wide string for Win32 API
#[cfg(windows)]
fn to_wide_null(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

/// Presents a native OS prompt asking user if they want to cluster the newly detected OS
pub fn prompt_cluster_os(
    peer_hostname: &str,
    peer_ip: &str,
    detected_os: &str,
    interactive: bool,
) -> bool {
    // If running in headless / automated mode, auto-accept
    if !interactive {
        return true;
    }

    #[cfg(windows)]
    {
        let caption = to_wide_null("ASTERIX CLUSTER MESH — NEW OS DETECTED");
        let message = format!(
            "[CLUSTER] ASTERIX CLUSTER ENGINE DETECTED A COMPANION MACHINE!\n\n\
            • Remote Machine: {}\n\
            • Network Link:   {}\n\
            • Detected OS:    {}\n\n\
            Do you want to cluster the two operating systems together to pool\n\
            CPU cores, GPUs, and RAM into a single supercomputer?",
            peer_hostname, peer_ip, detected_os
        );
        let wide_msg = to_wide_null(&message);

        unsafe {
            let res = win32::MessageBoxW(
                std::ptr::null_mut(),
                wide_msg.as_ptr(),
                caption.as_ptr(),
                win32::MB_YESNO | win32::MB_ICONQUESTION | win32::MB_TOPMOST,
            );
            return res == win32::IDYES;
        }
    }

    #[cfg(not(windows))]
    {
        // Try Zenity on Linux if available
        let title = "ASTERIX CLUSTER MESH — NEW OS DETECTED";
        let text = format!(
            "Detected companion machine {} ({})\nDetected OS: {}\n\nDo you want to cluster the two operating systems?",
            peer_hostname, peer_ip, detected_os
        );

        let zenity_res = std::process::Command::new("zenity")
            .args(&["--question", "--title", title, "--text", &text, "--timeout", "10"])
            .status();

        if let Ok(st) = zenity_res {
            return st.success();
        }

        // Fallback to notify-send and auto-accept
        let _ = std::process::Command::new("notify-send")
            .args(&[
                title,
                &format!("Connected with {} ({}). Clustering engaged.", peer_hostname, detected_os),
            ])
            .status();
        true
    }
}
