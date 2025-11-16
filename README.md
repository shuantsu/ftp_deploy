# FTP Deploy Tool

**Language / Idioma:** [English](#english) | [Português](#português)

---

## English

### Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Security Considerations](#security-considerations)
- [Files Generated](#files-generated)
- [License](#license)

### Overview

Automated FTP deployment tool that intelligently uploads only changed files to your FTP server. Uses local caching and file hashing to minimize upload time and bandwidth usage.

### Features

- **Smart Upload**: Only uploads modified files based on timestamps and MD5 hashes
- **File Rename Detection**: Automatically detects renamed files and performs server-side renames
- **Exclude Patterns**: Support for file and folder exclusion patterns
- **Dry Run Mode**: Preview what would be uploaded without making changes
- **Cache Management**: Maintains local cache to track uploaded files
- **Nested Directory Support**: Automatically creates remote directory structure

### Installation

1. Ensure Python 3.6+ is installed
2. Download `ftp_deploy.py` to your desired location
3. **Optional - Global Command Setup:**
   - **Windows**: Add the folder containing `ftp_deploy.bat` to your PATH environment variable
   - **Linux/macOS**: Create a symlink or add an alias (see [Linux/macOS Setup](#linuxmacos-setup))

### Configuration

Initialize configuration in your project folder:

```bash
python ftp_deploy.py --init
```

This creates a `.ftprules` file. Edit it with your FTP settings:

```ini
[remote]
ftp.yourserver.com

[user]
yourusername

[password]
yourpassword

[remote-folder]
www/your-remote-folder

[origin]
dist

[ignore]
TEMP/
*.log
node_modules/
```

### Usage

```bash
# Normal deployment
python ftp_deploy.py

# Preview changes without uploading
python ftp_deploy.py --dry-run

# Force upload all files
python ftp_deploy.py --force

# Initialize configuration
python ftp_deploy.py --init

# Open script folder to edit templates
python ftp_deploy.py --open-config-folder
```

### Examples

**Basic deployment:**
```bash
python ftp_deploy.py
```

**Check what would be uploaded:**
```bash
python ftp_deploy.py --dry-run
```

### Linux/macOS Setup

To use as a global command on Linux/macOS:

**Option 1 - Symlink:**
```bash
sudo ln -s /path/to/ftp_deploy.py /usr/local/bin/ftp_deploy
chmod +x /path/to/ftp_deploy.py
```

**Option 2 - Alias (add to ~/.bashrc or ~/.zshrc):**
```bash
alias ftp_deploy="python3 /path/to/ftp_deploy.py"
```

Then use globally:
```bash
ftp_deploy --dry-run
ftp_deploy --init
```

### Security Considerations

⚠️ **Important Security Notes:**

- **Never commit `.ftprules`** - Add it to your `.gitignore`
- **Use strong passwords** and consider SFTP/FTPS for production
- **Limit FTP user permissions** to only necessary directories
- **Regular password rotation** is recommended

### Files Generated

- `.ftprules` - Configuration file (add to .gitignore)
- `.ftp_cache.json` - Upload cache (add to .gitignore)
- `.ftprules.example` - Template file in script directory

### License

This project is open source. Use at your own risk.

---

## Português

### Índice
- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Exemplos](#exemplos)
- [Considerações de Segurança](#considerações-de-segurança)
- [Arquivos Gerados](#arquivos-gerados)
- [Licença](#licença)

### Visão Geral

Ferramenta de deploy FTP automatizada que envia inteligentemente apenas arquivos modificados para seu servidor FTP. Usa cache local e hash de arquivos para minimizar tempo de upload e uso de banda.

### Funcionalidades

- **Upload Inteligente**: Envia apenas arquivos modificados baseado em timestamps e hashes MD5
- **Detecção de Renomeação**: Detecta automaticamente arquivos renomeados e executa renomeação no servidor
- **Padrões de Exclusão**: Suporte para padrões de exclusão de arquivos e pastas
- **Modo Dry Run**: Visualiza o que seria enviado sem fazer alterações
- **Gerenciamento de Cache**: Mantém cache local para rastrear arquivos enviados
- **Suporte a Diretórios Aninhados**: Cria automaticamente estrutura de diretórios remotos

### Instalação

1. Certifique-se que Python 3.6+ está instalado
2. Baixe `ftp_deploy.py` para o local desejado
3. **Opcional - Comando Global:**
   - **Windows**: Adicione a pasta contendo `ftp_deploy.bat` à variável de ambiente PATH
   - **Linux/macOS**: Crie um symlink ou adicione um alias (veja [Configuração Linux/macOS](#configuração-linuxmacos))

### Configuração

Inicialize a configuração na pasta do seu projeto:

```bash
python ftp_deploy.py --init
```

Isso cria um arquivo `.ftprules`. Edite-o com suas configurações FTP:

```ini
[remote]
ftp.seuservidor.com.br

[user]
seuusuario

[password]
suasenha

[remote-folder]
www/sua-pasta-remota

[origin]
dist

[ignore]
TEMP/
*.log
node_modules/
```

### Uso

```bash
# Deploy normal
python ftp_deploy.py

# Visualizar mudanças sem enviar
python ftp_deploy.py --dry-run

# Forçar envio de todos os arquivos
python ftp_deploy.py --force

# Inicializar configuração
python ftp_deploy.py --init

# Abrir pasta do script para editar templates
python ftp_deploy.py --open-config-folder
```

### Exemplos

**Deploy básico:**
```bash
python ftp_deploy.py
```

**Verificar o que seria enviado:**
```bash
python ftp_deploy.py --dry-run
```

### Configuração Linux/macOS

Para usar como comando global no Linux/macOS:

**Opção 1 - Symlink:**
```bash
sudo ln -s /caminho/para/ftp_deploy.py /usr/local/bin/ftp_deploy
chmod +x /caminho/para/ftp_deploy.py
```

**Opção 2 - Alias (adicione ao ~/.bashrc ou ~/.zshrc):**
```bash
alias ftp_deploy="python3 /caminho/para/ftp_deploy.py"
```

Então use globalmente:
```bash
ftp_deploy --dry-run
ftp_deploy --init
```

### Considerações de Segurança

⚠️ **Notas Importantes de Segurança:**

- **Nunca faça commit do `.ftprules`** - Adicione-o ao seu `.gitignore`
- **Use senhas fortes** e considere SFTP/FTPS para produção
- **Limite permissões do usuário FTP** apenas aos diretórios necessários
- **Rotação regular de senhas** é recomendada

### Arquivos Gerados

- `.ftprules` - Arquivo de configuração (adicione ao .gitignore)
- `.ftp_cache.json` - Cache de upload (adicione ao .gitignore)
- `.ftprules.example` - Arquivo template no diretório do script

### Licença

Este projeto é código aberto. Use por sua conta e risco.

