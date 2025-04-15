#!/bin/bash

# Parâmetros
RESOURCE_GROUP="projeto-api-rg"
ACR_NAME="meuacrprojeto"
APP_NAME="pi-encomendas-webapp"
PLAN_NAME="api-plan"
IMAGE_NAME="api-projeto"
IMAGE_TAG="v1"
LOCATION="westeurope"

# Login no Azure
echo "🔐 A fazer login no Azure..."
az login

# Criar Resource Group
echo "📦 A criar resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Criar Azure Container Registry
echo "📦 A criar Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Ativar modo admin no ACR (necessário para obter credenciais)
echo "🔧 A ativar o modo admin no ACR..."
az acr update -n $ACR_NAME --admin-enabled true

# Login no ACR
echo "🔐 A fazer login no ACR..."
az acr login --name $ACR_NAME

# Construir imagem Docker
echo "🐳 A construir imagem Docker..."
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG .

# Push da imagem para o ACR
echo "📤 A fazer push da imagem para o ACR..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Criar App Service Plan
echo "☁️ A criar App Service Plan..."
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --is-linux --sku B1

# Criar Web App for Containers (sem flags inválidas)
echo "🌐 A criar Web App com container..."
az webapp create --resource-group $RESOURCE_GROUP \
                 --plan $PLAN_NAME \
                 --name $APP_NAME \
                 --deployment-container-image-name $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Obter credenciais do ACR
echo "�� A obter credenciais do ACR..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Configurar container no Web App
echo "⚙️ A configurar container no Web App..."
az webapp config container set --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

echo "✅ Deploy completo!"
