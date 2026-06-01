GITHUB_USER ?= PranjalVashisth
DOCKERHUB_USER ?= pranjalvashisth
REPO ?= ethara-inventory-oms

.PHONY: github-init github-push docker-build docker-push

github-init:
	git init
	git branch -M main
	git remote add origin https://github.com/$(GITHUB_USER)/$(REPO).git

github-push:
	git add .
	git commit -m "Ethara OMS: FastAPI + React + Postgres + Docker + tests" || true
	git push -u origin main

docker-build:
	docker build -t $(DOCKERHUB_USER)/ethara-oms-backend:latest ./backend
	docker build -t $(DOCKERHUB_USER)/ethara-oms-frontend:latest -f ./frontend/Dockerfile .

docker-push:
	docker push $(DOCKERHUB_USER)/ethara-oms-backend:latest
	docker push $(DOCKERHUB_USER)/ethara-oms-frontend:latest

