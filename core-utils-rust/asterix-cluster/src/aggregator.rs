//! ASTERIX OS — Cluster Hardware Performance Aggregator
//! Fuses CPU cores, GPU accelerators, and memory across all active cluster nodes.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use crate::hardware::{GpuDevice, LocalHardwareProfile};

#[derive(Debug, Clone)]
pub struct ClusterNodeInfo {
    pub node_id: String,
    pub hostname: String,
    pub os_name: String,
    pub os_family: String,
    pub primary_ip: String,
    pub cpu_cores: usize,
    pub total_ram_mb: u64,
    pub free_ram_mb: u64,
    pub gpus: Vec<GpuDevice>,
    pub estimated_tflops: f64,
    pub last_seen_secs: u64,
    pub is_local: bool,
}

#[derive(Debug, Clone)]
pub struct AggregatedClusterTopology {
    pub total_nodes: usize,
    pub combined_cpu_cores: usize,
    pub combined_ram_mb: u64,
    pub combined_free_ram_mb: u64,
    pub combined_gpu_count: usize,
    pub combined_tflops: f64,
    pub nodes: Vec<ClusterNodeInfo>,
    pub gpus: Vec<(String, GpuDevice)>, // (Hostname, GPU)
}

#[derive(Clone)]
pub struct ClusterAggregator {
    nodes: Arc<Mutex<HashMap<String, ClusterNodeInfo>>>,
    local_id: String,
}

impl ClusterAggregator {
    pub fn new(local_profile: &LocalHardwareProfile) -> Self {
        let mut map = HashMap::new();
        let local_info = ClusterNodeInfo {
            node_id: local_profile.node_id.clone(),
            hostname: local_profile.hostname.clone(),
            os_name: local_profile.os_name.clone(),
            os_family: local_profile.os_family.clone(),
            primary_ip: local_profile.primary_ip.clone(),
            cpu_cores: local_profile.cpu_cores,
            total_ram_mb: local_profile.total_ram_mb,
            free_ram_mb: local_profile.free_ram_mb,
            gpus: local_profile.gpus.clone(),
            estimated_tflops: local_profile.estimated_tflops,
            last_seen_secs: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            is_local: true,
        };
        map.insert(local_profile.node_id.clone(), local_info);

        ClusterAggregator {
            nodes: Arc::new(Mutex::new(map)),
            local_id: local_profile.node_id.clone(),
        }
    }

    pub fn update_node(&self, node: ClusterNodeInfo) {
        if let Ok(mut map) = self.nodes.lock() {
            map.insert(node.node_id.clone(), node);
        }
    }

    pub fn get_topology(&self) -> AggregatedClusterTopology {
        let map = self.nodes.lock().unwrap();
        let total_nodes = map.len();
        let combined_cpu_cores = map.values().map(|n| n.cpu_cores).sum();
        let combined_ram_mb = map.values().map(|n| n.total_ram_mb).sum();
        let combined_free_ram_mb = map.values().map(|n| n.free_ram_mb).sum();
        let combined_tflops = ((map.values().map(|n| n.estimated_tflops).sum::<f64>()) * 100.0).round() / 100.0;

        let mut gpus = Vec::new();
        for node in map.values() {
            for gpu in &node.gpus {
                gpus.push((node.hostname.clone(), gpu.clone()));
            }
        }
        let combined_gpu_count = gpus.len();

        let mut nodes_vec: Vec<ClusterNodeInfo> = map.values().cloned().collect();
        // Sort so local is first
        nodes_vec.sort_by_key(|n| !n.is_local);

        AggregatedClusterTopology {
            total_nodes,
            combined_cpu_cores,
            combined_ram_mb,
            combined_free_ram_mb,
            combined_gpu_count,
            combined_tflops,
            nodes: nodes_vec,
            gpus,
        }
    }
}
