# 🛡️ K8s-Compliance-Inspector

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Compatible-blue?style=for-the-badge&logo=kubernetes&logoColor=white)
![Status](https://img.shields.io/badge/Demo-Live_on_Render-success.svg?style=for-the-badge&logo=render&logoColor=white)

> **🚀 [LIVE DEMO: View Real-time K8s Compliance Report](https://k8s-compliance-demo.onrender.com/)**

**Kube-Compliance-Inspector** is a lightweight, agentless configuration compliance engine for Kubernetes. Written purely in Python using the official `kubernetes` client library, it queries the cluster state directly and generates clean HTML reports detailing configuration risks.

**Preventing production outages starts with enforcing strict configuration baselines.**

---

## 🎯 Core Principles

This tool scans all Deployments across non-system namespaces and validates them against critical SRE best practices:

*   🔴 **CRITICAL: Missing Resource Limits/Requests.** (Prevents node resource starvation and OOM Kills).
*   🟠 **WARNING: Usage of `latest` or missing image tags.** (Prevents unpredictable deployments and rollback failures).
*   🟠 **WARNING: Missing Liveness Probes.** (Prevents zombie pods and undetected deadlocks).

## 📊 Output Example

The engine generates professional, standalone HTML reports (`compliance_report.html`) categorizing findings by Namespace and Severity, providing actionable insights with minimal noise.

## 🚀 Quick Start

### Prerequisites
*   Python 3.11+
*   A valid Kubeconfig file (usually `~/.kube/config`) with read access to the cluster.

### Execution

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the inspector:**
    ```bash
    python inspector.py
    ```

3.  **View the results:**
    Open the newly generated `compliance_report.html` in any web browser.

## 🧪 Testing with Fixtures

For demonstration purposes, a `bad-deployments.yaml` file is included containing intentionally misconfigured deployments alongside one correctly configured deployment. 

```bash
kubectl apply -f bad-deployments.yaml
python inspector.py
```

## 💡 Extensibility

The rule engine in `inspector.py` is designed to be easily extensible. New compliance checks (e.g., checking for root users, missing security contexts, or specific labels) can be added as simple functions.

## 📄 License
MIT License
