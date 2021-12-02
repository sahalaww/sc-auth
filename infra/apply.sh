#!/bin/bash
kubectl apply -f sc-auth-namespace.yaml
kubectl apply -f sc-auth-secret.yaml
kubectl apply -f sc-auth-deployment.yaml
kubectl apply -f sc-auth-service.yaml
kubectl apply -f sc-auth-ingress.yaml
