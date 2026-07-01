# STAE — Sistema de Controlo de Acessos

## Instalação

```powershell
cd "C:\Users\ADMIN\OneDrive\Documents\GINASIO PROJETO"
python -m pip install -r requirements.txt
```

## Executar (desenvolvimento)

```powershell
$env:STAE_DEBUG="true"
python run.py
```

Abrir: http://127.0.0.1:5000

## Executar (produção)

```powershell
$env:STAE_SECRET_KEY="defina-uma-chave-longa-e-aleatoria"
$env:STAE_DEBUG="false"
python run.py
```

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `STAE_SECRET_KEY` | Chave de sessão Flask | dev key |
| `STAE_DEBUG` | Modo debug (`true`/`false`) | `false` |
| `STAE_HOST` | IP do servidor | `127.0.0.1` |
| `STAE_PORT` | Porta | `5000` |
| `STAE_PER_PAGE` | Registos por página | `15` |

## Contas iniciais (alterar após instalação)

| Tipo | Utilizador | Senha |
|------|------------|-------|
| Admin | admin | admin123 |
| Polícia | policia | policia123 |
| RH | rh | rh123 |

## Testes

```powershell
python -m pytest tests/ -v
```

## Backups

Backups automáticos em `data/backups/` via Dashboard (Admin).
