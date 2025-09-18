# IFPE - Sistemas Distribuídos
# Protótipo: Armazenamento Distribuído de arquivos com MinIO

## Discente: Heitor Fidelis
## Docente: Luciano de Souza Cabral

---

## Tecnologias Utilizadas

- **Python 3.12**
- **FastAPI** – framework web assíncrono para expor a API de upload
- **Boto3** – cliente AWS S3 para interação com o MinIO
- **MinIO** – armazenamento de objetos compatível com S3
- **HTML + JavaScript** – interface web para upload e listagem de arquivos
- **Docker Compose** – orquestração dos serviços

---

## Descrição da Arquitetura

1. **Front-End (HTML + JS)**
   - Permite o upload de arquivos de vídeo via navegador.
   - Usa **URLs pré-assinadas (Presigned URLs)** para enviar os arquivos diretamente ao MinIO.
   - Lista os arquivos já armazenados no bucket.

2. **Backend (FastAPI)**
   - Expõe um endpoint `/presign` que gera URLs pré-assinadas para upload no MinIO.
   - Expõe um endpoint `/list` que retorna a lista de arquivos armazenados.

3. **MinIO**
   - Funciona como sistema de **armazenamento distribuído de objetos**, compatível com a API do S3.
   - Os arquivos são replicados e ficam disponíveis para distribuição global.
   - Painel de administração acessível em `http://localhost:9001`.

---

## Funcionalidades

- Upload de arquivos via navegador utilizando **Presigned URLs**.
- Armazenamento seguro e escalável no **MinIO**.
- Listagem dos arquivos já armazenados no bucket `videos`.
- Integração simples com aplicações web por meio de **API REST**.

---

## Como executar o protótipo localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/hfidelis/distributed-systems-ifpe
cd distributed-systems-ifpe/minio_prototype
```

### 2. Construir e iniciar os serviços com Docker Compose

```bash
docker-compose up --build
```

### 3. Acessar a interface web
Abra o navegador e acesse `http://localhost:8000` para usar a interface de upload e listagem de arquivos.

### 4. Acessar o painel do MinIO
Acesse `http://localhost:9001` para o painel de administração do MinIO.
Use as credenciais:
- Usuário: `minioadmin`
- Senha: `minioadmin`
