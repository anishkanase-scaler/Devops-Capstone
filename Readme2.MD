1. Testing and Local Application Verification 
Pytest: All 23 pytest tests passed successfully on the updated backend dependencies
![alt text](image.png) 

2. Docker Compose: Ran docker compose up to build and start the application services locally and verify that the frontend, backend, and database containers started successfully.
![alt text](image-1.png)


3. Frontend: Verified that the Petal Shop frontend was accessible locally and that the application interface loaded correctly.
![alt text](image-2.png)


4. CI/CD Pipeline
All CI/CD checks passed successfully. The pipeline executed the build-and-test job, Trivy security scanning, and Docker image build and push steps.
![alt text](image-3.png)


5. Docker Images Published to GHCR: Both frontend and backend Docker images were successfully pushed to GitHub Container Registry (GHCR)

=> Frontend pushed in GHCR
![alt text](image-4.png)
ghcr.io/anishkanase-scaler/petal-shop-frontend:91396632fbdcb4679e4143e538cfc4cef57dc9ba


=> Backend pushed in GHCR
![alt text](image-5.png)
ghcr.io/anishkanase-scaler/petal-shop-backend:91396632fbdcb4679e4143e538cfc4cef57dc9ba



6. # Frontend Security Fixes
 
Issue: After Trivy scanning, the frontend image had 2 CRITICAL and 39 HIGH vulnerabilities. The nginx-unprivileged:1.27-alpine base image used Alpine 3.21.3, which was outdated. The CRITICAL findings were CVE-2026-31789 in OpenSSL (libcrypto3 and libssl3). The HIGH findings affected OpenSSL, libexpat, libpng, libxml2, musl, zlib, c-ares, nghttp2-libs and tiff.

Changes made in frontend/Dockerfile:

=> Upgraded the base image from nginx-unprivileged:1.27-alpine (Alpine 3.21.3) to 1.30-alpine (Alpine 3.24.2).
=> Retained the unprivileged, non-root image.
=> Added a HEALTHCHECK using wget.


7. # Backend Security Fixes

Issue: After Trivy scanning, the backend image had 47 HIGH vulnerabilities. The 44 HIGH OS-package findings affected util-linux, ncurses, systemd, perl-base and libacl1. Additionally, Starlette 0.41.3 had 3 HIGH. Trivy also flagged msgpack, setuptools and urllib3 vulnerabilities bundled inside pip.

Changes made in backend/requirements.txt:

=> Upgraded FastAPI from 0.115.6 to 0.143.3.
=> Pinned Starlette to 1.8.0 to keep builds reproducible.
=> Upgraded prometheus-fastapi-instrumentator from 7.0.2 to 8.1.0, as the old version blocked Starlette 1.x.
=> Left the other dependency pins unchanged.

Changes made in backend/Dockerfile:

=> Uninstalled pip, setuptools and wheel after installing dependencies, as the application doesn't need them at runtime.
=> Added a HEALTHCHECK that calls the existing /health endpoint, fixing the earlier LOW DS=>0026 finding.

Testing: All 23 pytest tests passed on the updated versions.


8. Trivy Security Scan Results
![alt text](image-7.png)


9. Terraform Validation and Deployment
![alt text](image-8.png)


10. Applying terraform plan
![alt text](image-9.png)


11. Applying terraform
![alt text](image-10.png)


12. ![alt text](image-11.png)
Terraform output and State list.


13. AWS Infrastructure Verification: After successfully applying the Terraform configuration, verified the provisioned AWS resources.
![alt text](image-12.png) - EC2
![alt text](image-13.png) - EKS
![alt text](image-14.png) - VPC
![alt text](image-15.png) - Subnet
![alt text](image-16.png) - Route Table
![alt text](image-17.png) - IGW(Internet Gateway)
![alt text](image-18.png) - Security Groups


14. Terraform destroyed
![alt text](image-19.png)

15. Helm install
![alt text](image-20.png)

16. Helm get pods and services and helm list
![alt text](image-21.png)


17. kubectl get ingress
![alt text](image-22.png)


18. Ingress localhost on browser
![alt text](image-23.png)


Video Link inside Drive folde:
https://drive.google.com/drive/folders/1eQ9GsEEKd5uq27uqpHmT0j0bvrJPos4W?usp=sharing