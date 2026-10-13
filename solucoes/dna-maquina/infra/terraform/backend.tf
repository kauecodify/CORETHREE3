"""
CORETHREE3 - DNA de Maquinas
Configuracao de Backend do Terraform

Este arquivo configura o backend do Terraform para armazenar o estado remoto.
"""

# Configuracao do backend S3 para armazenar o estado do Terraform
terraform {
  backend "s3" {
    # O bucket sera criado manualmente ou via outro Terraform
    # bucket = "corethree3-terraform-state"
    
    # Chave do estado
    key    = "dna-maquina/terraform.tfstate"
    
    # Regiao do bucket
    region = "us-east-1"
    
    # Criptografia do estado
    encrypt = true
    
    # Controle de versao
    versioning = true
    
    # Locking com DynamoDB
    # dynamodb_table = "corethree3-terraform-lock"
  }
}

# Para ambientes de producao, usar o seguinte backend:
# terraform {
#   backend "s3" {
#     bucket         = "corethree3-terraform-state-prod"
#     key            = "dna-maquina/prod/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     versioning     = true
#     dynamodb_table = "corethree3-terraform-lock-prod"
#   }
# }

# Para ambientes de desenvolvimento local, usar o backend local:
# terraform {
#   backend "local" {
#     path = "relative/path/to/terraform.tfstate"
#   }
# }
