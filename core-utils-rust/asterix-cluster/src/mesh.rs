//! ASTERIX OS — Ultra-Low-Latency Cluster Mesh, Discovery & RPC Engine
//! Detects plugged PCs over UDP broadcast, prompts user with native OS notifications,
//! and maintains high-speed TCP inter-node communication.

use std::collections::HashSet;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream, UdpSocket};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use crate::aggregator::{ClusterAggregator, ClusterNodeInfo};
use crate::assembly_kernel;
use crate::c_kernel_bindings;
use crate::hardware::{GpuDevice, LocalHardwareProfile};

pub const DEFAULT_BEACON_PORT: u16 = 38555;
pub const DEFAULT_MESH_PORT: u16 = 38556;

#[derive(Clone)]
pub struct ClusterMeshService {
    pub local_profile: LocalHardwareProfile,
    pub aggregator: ClusterAggregator,
    pub interactive: bool,
    pub mesh_port: u16,
    pub beacon_port: u16,
    pub running: Arc<AtomicBool>,
    prompted_nodes: Arc<Mutex<HashSet<String>>>,
}

impl ClusterMeshService {
    pub fn new(local_profile: LocalHardwareProfile, interactive: bool) -> Self {
        let aggregator = ClusterAggregator::new(&local_profile);
        ClusterMeshService {
            local_profile,
            aggregator,
            interactive,
            mesh_port: DEFAULT_MESH_PORT,
            beacon_port: DEFAULT_BEACON_PORT,
            running: Arc::new(AtomicBool::new(false)),
            prompted_nodes: Arc::new(Mutex::new(HashSet::new())),
        }
    }

    /// Serializes a beacon packet
    fn build_beacon_packet(&self) -> String {
        format!(
            "{{\"magic\":\"AX_CLUSTER_V4\",\"node_id\":\"{}\",\"hostname\":\"{}\",\"os_name\":\"{}\",\"os_family\":\"{}\",\"cpu_cores\":{},\"ram_mb\":{},\"free_ram\":{},\"tflops\":{},\"mesh_port\":{}}}",
            self.local_profile.node_id,
            self.local_profile.hostname,
            self.local_profile.os_name.replace('"', "\\\""),
            self.local_profile.os_family,
            self.local_profile.cpu_cores,
            self.local_profile.total_ram_mb,
            self.local_profile.free_ram_mb,
            self.local_profile.estimated_tflops,
            self.mesh_port
        )
    }

    /// Broadcasts UDP beacon on LAN and direct cable links
    pub fn start_beacon_broadcast(&self) {
        let running = self.running.clone();
        let beacon_data = self.build_beacon_packet();
        let port = self.beacon_port;

        thread::spawn(move || {
            let socket = match UdpSocket::bind("0.0.0.0:0") {
                Ok(s) => s,
                Err(_) => return,
            };
            let _ = socket.set_broadcast(true);

            let targets = vec![
                format!("255.255.255.255:{}", port),
                format!("169.254.255.255:{}", port),
            ];

            while running.load(Ordering::Relaxed) {
                for target in &targets {
                    let _ = socket.send_to(beacon_data.as_bytes(), target);
                }
                thread::sleep(Duration::from_millis(2500));
            }
        });
    }

    /// Listens for UDP beacons from plugged PCs & triggers OS notification prompt
    pub fn start_beacon_listener(&self) {
        let running = self.running.clone();
        let local_id = self.local_profile.node_id.clone();
        let aggregator = self.aggregator.clone();
        let prompted = self.prompted_nodes.clone();
        let interactive = self.interactive;
        let port = self.beacon_port;

        thread::spawn(move || {
            let socket = match UdpSocket::bind(format!("0.0.0.0:{}", port)) {
                Ok(s) => s,
                Err(_) => return,
            };
            let _ = socket.set_read_timeout(Some(Duration::from_millis(1500)));

            let mut buf = [0u8; 4096];
            while running.load(Ordering::Relaxed) {
                if let Ok((len, src_addr)) = socket.recv_from(&mut buf) {
                    if let Ok(text) = std::str::from_utf8(&buf[..len]) {
                        if text.contains("\"magic\":\"AX_CLUSTER_V4\"") {
                            // Extract basic fields via simple parsing
                            if let Some(peer_id) = extract_json_field(text, "node_id") {
                                if peer_id != local_id {
                                    let hostname = extract_json_field(text, "hostname").unwrap_or_else(|| "Companion".to_string());
                                    let os_name = extract_json_field(text, "os_name").unwrap_or_else(|| "Linux/Windows".to_string());
                                    let os_family = extract_json_field(text, "os_family").unwrap_or_else(|| "OS".to_string());
                                    let cores = extract_json_num(text, "cpu_cores").unwrap_or(4) as usize;
                                    let ram_mb = extract_json_num(text, "ram_mb").unwrap_or(8192);
                                    let free_ram = extract_json_num(text, "free_ram").unwrap_or(4096);
                                    let tflops = extract_json_float(text, "tflops").unwrap_or(2.5);

                                    let mut should_prompt = false;
                                    {
                                        let mut set = prompted.lock().unwrap();
                                        if !set.contains(&peer_id) {
                                            set.insert(peer_id.clone());
                                            should_prompt = true;
                                        }
                                    }

                                    if should_prompt {
                                        let ip_str = src_addr.ip().to_string();
                                        // Trigger Native OS Notification Prompt!
                                        let accepted = c_kernel_bindings::prompt_cluster_os(
                                            &hostname,
                                            &ip_str,
                                            &os_name,
                                            interactive,
                                        );

                                        if accepted {
                                            let node_info = ClusterNodeInfo {
                                                node_id: peer_id,
                                                hostname,
                                                os_name,
                                                os_family,
                                                primary_ip: ip_str,
                                                cpu_cores: cores,
                                                total_ram_mb: ram_mb,
                                                free_ram_mb: free_ram,
                                                gpus: vec![GpuDevice {
                                                    name: "Cluster Peer Accelerator".to_string(),
                                                    vram_mb: 2048,
                                                    device_type: "Remote GPU/SIMD Engine".to_string(),
                                                }],
                                                estimated_tflops: tflops,
                                                last_seen_secs: std::time::SystemTime::now()
                                                    .duration_since(std::time::UNIX_EPOCH)
                                                    .unwrap_or_default()
                                                    .as_secs(),
                                                is_local: false,
                                            };
                                            aggregator.update_node(node_info);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        });
    }

    /// TCP RPC Server for receiving distributed compute tasks
    pub fn start_mesh_rpc_server(&self) {
        let running = self.running.clone();
        let port = self.mesh_port;
        let local_profile = self.local_profile.clone();

        thread::spawn(move || {
            let listener = match TcpListener::bind(format!("0.0.0.0:{}", port)) {
                Ok(l) => l,
                Err(_) => return,
            };
            let _ = listener.set_nonblocking(true);

            while running.load(Ordering::Relaxed) {
                match listener.accept() {
                    Ok((mut stream, _)) => {
                        let prof = local_profile.clone();
                        thread::spawn(move || {
                            let _ = handle_rpc_stream(&mut stream, &prof);
                        });
                    }
                    Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                        thread::sleep(Duration::from_millis(50));
                    }
                    Err(_) => {}
                }
            }
        });
    }

    /// Starts all cluster networking services
    pub fn start(&self) {
        self.running.store(true, Ordering::Relaxed);
        self.start_beacon_broadcast();
        self.start_beacon_listener();
        self.start_mesh_rpc_server();
    }

    /// Stops cluster networking
    pub fn stop(&self) {
        self.running.store(false, Ordering::Relaxed);
    }
}

/// Dispatches task processing on the TCP stream
fn handle_rpc_stream(stream: &mut TcpStream, prof: &LocalHardwareProfile) -> std::io::Result<()> {
    let _ = stream.set_read_timeout(Some(Duration::from_secs(15)));
    let mut len_buf = [0u8; 4];
    stream.read_exact(&mut len_buf)?;
    let msg_len = u32::from_be_bytes(len_buf) as usize;

    let mut body = vec![0u8; msg_len];
    stream.read_exact(&mut body)?;
    let req = String::from_utf8_lossy(&body);

    let resp = if req.contains("\"action\":\"bench\"") {
        let iters = extract_json_num(&req, "iters").unwrap_or(2_000_000);
        let bench = assembly_kernel::run_assembly_vector_benchmark(iters);
        format!(
            "{{\"status\":\"ok\",\"node_id\":\"{}\",\"hostname\":\"{}\",\"mega_ops\":{:.2},\"gflops\":{:.4},\"simd\":\"{}\"}}",
            prof.node_id, prof.hostname, bench.mega_ops, bench.gflops, bench.simd_engine
        )
    } else if req.contains("\"action\":\"ping\"") {
        format!(
            "{{\"status\":\"ok\",\"node_id\":\"{}\",\"hostname\":\"{}\",\"os_name\":\"{}\",\"cores\":{},\"ram\":{}}}",
            prof.node_id, prof.hostname, prof.os_name, prof.cpu_cores, prof.total_ram_mb
        )
    } else {
        format!("{{\"status\":\"ok\",\"node_id\":\"{}\"}}", prof.node_id)
    };

    let resp_bytes = resp.as_bytes();
    let resp_len = (resp_bytes.len() as u32).to_be_bytes();
    stream.write_all(&resp_len)?;
    stream.write_all(resp_bytes)?;
    stream.flush()?;
    Ok(())
}

fn extract_json_field(json: &str, field: &str) -> Option<String> {
    let pattern = format!("\"{}\":\"", field);
    if let Some(pos) = json.find(&pattern) {
        let start = pos + pattern.len();
        if let Some(end) = json[start..].find('"') {
            return Some(json[start..start + end].to_string());
        }
    }
    None
}

fn extract_json_num(json: &str, field: &str) -> Option<u64> {
    let pattern = format!("\"{}\":", field);
    if let Some(pos) = json.find(&pattern) {
        let start = pos + pattern.len();
        let slice = &json[start..];
        let num_str: String = slice.chars().take_while(|c| c.is_ascii_digit()).collect();
        return num_str.parse::<u64>().ok();
    }
    None
}

fn extract_json_float(json: &str, field: &str) -> Option<f64> {
    let pattern = format!("\"{}\":", field);
    if let Some(pos) = json.find(&pattern) {
        let start = pos + pattern.len();
        let slice = &json[start..];
        let num_str: String = slice.chars().take_while(|c| c.is_ascii_digit() || *c == '.').collect();
        return num_str.parse::<f64>().ok();
    }
    None
}
