"""
K8s Automated Configuration Compliance Inspector - Demo Version
"""
import os
import yaml
import datetime
import logging
from typing import List, Dict, Any
from flask import Flask, send_from_directory
from jinja2 import Template
from kubernetes import client, config

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("K8s-Inspector")

EXCLUDED_NAMESPACES = {"kube-system", "kube-public", "kube-node-lease", "keda"}

# Flask App for Demo Display
app = Flask(__name__)

@app.route("/")
def serve_report():
    if not os.path.exists("compliance_report.html"):
        return "Report is generating...", 202
    return send_from_directory(".", "compliance_report.html")

def inspect_deployment(deployment: Any) -> List[Dict[str, str]]:
    """Scan a single deployment against compliance policies."""
    issues = []
    containers = deployment.spec.template.spec.containers
    for container in containers:
        image = container.image
        if ":" not in image or image.endswith(":latest"):
            issues.append({
                "severity": "WARNING",
                "message": f"Container '{container.name}' uses 'latest': {image}",
                "impact": "Unpredictable deployments and difficult rollbacks."
            })
        resources = getattr(container, 'resources', None)
        if not resources or not getattr(resources, 'limits', None) or not getattr(resources, 'requests', None):
            issues.append({
                "severity": "CRITICAL",
                "message": f"Container '{container.name}' is missing resource limits/requests.",
                "impact": "Potential node resource starvation (OOM Kills)."
            })
        if not getattr(container, 'liveness_probe', None):
            issues.append({
                "severity": "WARNING",
                "message": f"Container '{container.name}' is missing a livenessProbe.",
                "impact": "K8s cannot detect deep deadlocks or app freezes."
            })
    return issues

def load_mock_data():
    """Fallback for Render Demo using bad-deployments.yaml."""
    logger.warning("No Kubeconfig found. Entering DEMO MODE using local fixtures.")
    if not os.path.exists("bad-deployments.yaml"):
        logger.error("Fixtures file 'bad-deployments.yaml' not found.")
        return []
    try:
        with open("bad-deployments.yaml", "r", encoding="utf-8") as f:
            fixtures = list(yaml.safe_load_all(f))
    except Exception as e:
        logger.error(f"Failed to read fixtures: {e}")
        return []
    
    mock_deployments = []
    for d in fixtures:
        if d and d.get('kind') == 'Deployment':
            class MockContainer:
                def __init__(self, c):
                    self.name = c['name']
                    self.image = c['image']
                    self.resources = type('obj', (object,), {
                        'limits': c.get('resources', {}).get('limits'),
                        'requests': c.get('resources', {}).get('requests')
                    })
                    self.liveness_probe = c.get('livenessProbe')
            
            class MockDeployment:
                def __init__(self, data):
                    self.metadata = type('obj', (object,), {
                        'name': data['metadata']['name'],
                        'namespace': data['metadata'].get('namespace', 'demo-env')
                    })
                    self.spec = type('obj', (object,), {
                        'template': type('obj', (object,), {
                            'spec': type('obj', (object,), {
                                'containers': [MockContainer(c) for c in data['spec']['template']['spec']['containers']]
                            })
                        })
                    })
            mock_deployments.append(MockDeployment(d))
    return mock_deployments

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>K8s Inspector Live Demo</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; margin: 40px; }
        .stat-box { display: inline-block; padding: 20px; border-radius: 8px; color: white; width: 200px; margin-right: 15px; }
        .critical { background: #e11d48; } .warning { background: #f59e0b; } .passed { background: #10b981; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 5px solid #ccc; }
        .card.has-critical { border-left-color: #e11d48; }
        .issue { background: #fff1f2; padding: 10px; border-radius: 4px; border-left: 3px solid #e11d48; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>K8s Compliance Live Dashboard (Demo)</h1>
    <p>Last Analysis: {{ timestamp }}</p>
    <div>
        <div class="stat-box critical"><h2>{{ critical_count }}</h2>  CRITICAL</div>
        <div class="stat-box warning"><h2>{{ warning_count }}</h2> WARNINGS</div>
    </div>
    {% for dep in deployments %}
    <div class="card {% if dep.critical > 0 %}has-critical{% endif %}">
        <h3>[{{ dep.namespace }}] {{ dep.name }}</h3>
        {% for issue in dep.issues %}
            <div class="issue"><strong>{{ issue.severity }}:</strong> {{ issue.message }}</div>
        {% endfor %}
    </div>
    {% endfor %}
</body>
</html>
"""

def generate_report():
    try:
        config.load_kube_config()
        v1 = client.AppsV1Api()
        deployments = v1.list_deployment_for_all_namespaces().items
        logger.info("Connected to live K8s cluster.")
    except Exception:
        deployments = load_mock_data()

    report_data = []
    stats = {"critical": 0, "warning": 0}
    for dep in deployments:
        if dep.metadata.namespace in EXCLUDED_NAMESPACES: continue
        issues = inspect_deployment(dep)
        crit = sum(1 for i in issues if i['severity'] == 'CRITICAL')
        warn = sum(1 for i in issues if i['severity'] == 'WARNING')
        stats["critical"] += crit
        stats["warning"] += warn
        report_data.append({
            "name": dep.metadata.name, 
            "namespace": dep.metadata.namespace, 
            "issues": issues, 
            "critical": crit
        })

    rendered = Template(HTML_TEMPLATE).render(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        critical_count=stats["critical"],
        warning_count=stats["warning"],
        deployments=report_data
    )
    with open("compliance_report.html", "w", encoding="utf-8") as f:
        f.write(rendered)
    logger.info("Report generated successfully.")

if __name__ == "__main__":
    generate_report()
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting web server on port {port}...")
    app.run(host="0.0.0.0", port=port)
