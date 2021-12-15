# cert-exporter
Kubernetes certificates exporter is designed to parse certificates and export expiration information for Prometheus to scrape.

### Certificates sources
- pem files from nodes
- certs stored in kubernetes secrets
- https urls

### Metrics samples
```
certexporter{cn="*.google.com" exp_date="21.02.2022" type="remote" location="google.com:443"} 20
certexporter{cn="NGINXIngressController" exp_date="11.09.2023" type="kube" location="ingress/nginx-nginx-ingress-default-server-secret"} 65
certexporter{cn="USERTrust ECC Certification Authority" exp_date="18.01.2038" type="node" location="host:/etc/ssl/certs/USERTrust_ECC_Certification_Authority.pem"} 42
```
