# CORETHREE3 - DNA de Maquinas - Infraestrutura Terraform

Este diretorio contem a configuracao de infraestrutura como codigo para o sistema DNA de Maquinas usando Terraform.

## Estrutura

```
infra/terraform/
├── main.tf          # Configuracao principal dos recursos AWS
├── variables.tf     # Variaveis de configuracao
├── outputs.tf       # Saidas do Terraform
├── backend.tf       # Configuracao do backend
└── README.md        # Este arquivo
```

## Requisitos

- Terraform >= 1.0.0
- AWS CLI configurado com credenciais validas
- Permissoes de administrador na conta AWS

## Instalacao

### 1. Instalar Terraform

Siga as instrucoes em [https://learn.hashicorp.com/tutorials/terraform/install-cli](https://learn.hashicorp.com/tutorials/terraform/install-cli)

### 2. Configurar AWS CLI

```bash
aws configure
```

Informe as credenciais da AWS quando solicitado.

### 3. Configurar variaveis de ambiente (opcional)

```bash
export AWS_ACCESS_KEY_ID=sua_chave_de_acesso
export AWS_SECRET_ACCESS_KEY=seu_segredo_de_acesso
export AWS_DEFAULT_REGION=us-east-1
```

## Uso

### Inicializar o Terraform

```bash
cd solucoes/dna-maquina/infra/terraform
terraform init
```

### Planejar a implantacao

```bash
# Para ambiente de desenvolvimento
terraform plan -var="environment=dev"

# Para ambiente de producao
terraform plan -var="environment=prod"
```

### Aplicar a configuracao

```bash
# Para ambiente de desenvolvimento
terraform apply -var="environment=dev" -auto-approve

# Para ambiente de producao
terraform apply -var="environment=prod" -auto-approve
```

### Destruir a infraestrutura

```bash
# Para ambiente de desenvolvimento
terraform destroy -var="environment=dev" -auto-approve

# Para ambiente de producao
terraform destroy -var="environment=prod" -auto-approve
```

## Variaveis Principais

| Variavel | Descricao | Valor Padrao |
|----------|-----------|--------------|
| aws_region | Regiao AWS | us-east-1 |
| environment | Ambiente (dev, staging, prod) | dev |
| project_name | Nome do projeto | corethree3-dna-maquina |

## Recursos Criados

### VPC e Rede
- VPC com CIDR 10.0.0.0/16
- 3 Subnets privadas (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)
- 3 Subnets publicas (10.0.101.0/24, 10.0.102.0/24, 10.0.103.0/24)
- NAT Gateway para acesso a internet das subnets privadas

### Seguranca
- Security Group para IoT Core
- Security Group para instancias EC2
- IAM Role para EC2 com permissao SSM, S3 e CloudWatch
- IAM Role para Lambda com permissao basica de execucao

### IoT Core
- Thing Type: DNAMaquina-Device
- Politica de seguranca para dispositivos

### Bancos de Dados
- **DynamoDB**:
  - Tabela de dispositivos
  - Tabela de sensores
  - Tabela de alertas
  - Tabela de predicoes
  - Tabela de manutencao

- **Timestream**:
  - Banco de dados: corethree3-dna-maquina-timestream
  - Tabelas: vibration, temperature, pressure, current, voltage

### Armazenamento
- **S3**:
  - Bucket de Data Lake
  - Bucket de Firmware
  - Bucket de Logs

### Compute
- **Lambda Functions**:
  - process_readings: Processa leituras de sensores
  - detect_anomalies: Detecta anomalias
  - predict_failures: Prediz falhas
  - schedule_maintenance: Agenda manutencao

### API Gateway
- API HTTP com stage para cada ambiente
- Integracao com funcoes Lambda

### EventBridge
- Regras agendadas para:
  - Processamento de leituras (5 minutos)
  - Detecao de anomalias (15 minutos)
  - Predicao de falhas (1 hora)

### SNS
- Topicos para alertas:
  - Alertas criticos
  - Alertas altos
  - Alertas medios
  - Alertas baixos

### CloudWatch
- Dashboard com metricas do sistema
- Grupos de logs para API Gateway

## Personalizacao

### Ambientes

Para criar um novo ambiente, defina as variaveis no comando:

```bash
terraform apply -var="environment=novo-ambiente" -auto-approve
```

### Regiao AWS

Para usar uma regiao diferente:

```bash
terraform apply -var="aws_region=sa-east-1" -auto-approve
```

### Nomes de Recursos

Para personalizar os nomes dos recursos, edite o arquivo `variables.tf`.

## Boas Praticas

1. **Ambientes Separados**: Sempre use ambientes separados (dev, staging, prod)
2. **Controle de Versao**: Mantenha o codigo do Terraform no controle de versao
3. **Lock de Estado**: Use locking com DynamoDB para evitar conflitos
4. **Backup do Estado**: O estado do Terraform e critico, faca backup regularmente
5. **Revisao de Mudancas**: Sempre revise o plano antes de aplicar
6. **Modularizacao**: Considere modularizar a configuracao para reutilizacao

## Solucao de Problemas

### Erro de Permissao

Se receber erros de permissao, verifique:
- As credenciais AWS estao configuradas corretamente
- O IAM user/role tem as permissao necessarias
- As politicas IAM estao anexadas corretamente

### Erro de Recurso Ja Existente

Se receber erros de recursos ja existentes:
- Verifique se ja existe uma implantacao no mesmo ambiente
- Use `terraform import` para importar recursos existentes
- Ou destrua a infraestrutura existente antes de criar uma nova

### Erro de Lock

Se o Terraform reclama de lock:
- Verifique se ha outro processo do Terraform em execucao
- Use `terraform force-unlock LOCK_ID` para remover o lock (com cuidado)

## Integracao CI/CD

### GitHub Actions

Exemplo de workflow para GitHub Actions:

```yaml
name: Terraform Apply

on:
  push:
    branches: [ main ]
    paths:
      - 'solucoes/dna-maquina/infra/terraform/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v1
      with:
        terraform_version: 1.0.0
    
    - name: Terraform Init
      run: terraform init
      working-directory: solucoes/dna-maquina/infra/terraform
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    
    - name: Terraform Plan
      run: terraform plan -var="environment=dev"
      working-directory: solucoes/dna-maquina/infra/terraform
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    
    - name: Terraform Apply
      if: github.ref == 'refs/heads/main'
      run: terraform apply -var="environment=dev" -auto-approve
      working-directory: solucoes/dna-maquina/infra/terraform
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Seguranca

### Segredos
- Nunca armazene segredos no codigo
- Use variaveis de ambiente ou AWS Secrets Manager
- Use IAM Roles em vez de credenciais estaticas quando possivel

### Criptografia
- Todos os buckets S3 tem criptografia habilitada
- O estado do Terraform e criptografado no S3
- Use KMS para criptografia adicional se necessario

### Acesso
- Restrinja o acesso as credenciais AWS
- Use politicas IAM minimas necessarias
- Audite regularmente as permissao

## Custos

### Estimativa de Custos

Os custos variam de acordo com:
- Numero de dispositivos
- Volume de dados
- Frequencia de processamento
- Regiao AWS

Principais componentes de custo:
- AWS IoT Core: Por mensagem
- Timestream: Por GB armazenado e consultado
- Lambda: Por execucao e tempo de execucao
- DynamoDB: Por operacao de leitura/escrita
- S3: Por GB armazenado

### Otimizacao de Custos

1. **Lambda**: Use memoria e timeout adequados
2. **Timestream**: Use Magnetic Store para dados historicos
3. **DynamoDB**: Use modo on-demand para cargas de trabalho variaveis
4. **S3**: Use lifecycle policies para remover dados antigos
5. **IoT**: Use batch de mensagens quando possivel

## Documentacao Adicional

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS IoT Core](https://aws.amazon.com/iot-core/)
- [Amazon Timestream](https://aws.amazon.com/timestream/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
