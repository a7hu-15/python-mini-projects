import unittest
import tempfile
import os
from k8s_manifest_linter.k8s_manifest_linter import audit_k8s_manifest, audit_container_spec


class TestK8sManifestLinter(unittest.TestCase):
    def test_privileged_container_detection(self):
        container = {
            "name": "web",
            "image": "nginx:1.25",
            "securityContext": {"privileged": True}
        }
        issues = audit_container_spec(container, "spec.template.spec")
        privileged_issues = [i for i in issues if i["rule"] == "PrivilegedContainer"]
        self.assertEqual(len(privileged_issues), 1)
        self.assertEqual(privileged_issues[0]["severity"], "CRITICAL")

    def test_unpinned_image_tag_detection(self):
        container = {
            "name": "app",
            "image": "myrepo/myapp:latest"
        }
        issues = audit_container_spec(container, "spec.template.spec")
        image_issues = [i for i in issues if i["rule"] == "UnpinnedImageTag"]
        self.assertEqual(len(image_issues), 1)

    def test_missing_resource_limits(self):
        container = {
            "name": "app",
            "image": "myrepo/myapp:1.0.0"
        }
        issues = audit_container_spec(container, "spec.template.spec")
        res_issues = [i for i in issues if i["rule"] == "MissingResourceLimits"]
        self.assertEqual(len(res_issues), 1)

    def test_audit_manifest_file(self):
        manifest_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insecure-deployment
spec:
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        securityContext:
          privileged: true
"""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml") as f:
            f.write(manifest_content)
            temp_path = f.name

        try:
            report = audit_k8s_manifest(temp_path)
            self.assertFalse(report["valid"])
            self.assertTrue(report["error_count"] >= 2)
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
