# ytwatch

Assista (ou ouça) YouTube direto no terminal, sem abrir navegador — via `mpv` + `yt-dlp`.

## Requisitos

- [mpv](https://mpv.io/) instalado no sistema
- Python 3.9+
- Pacote `yt-dlp` (veja instalação abaixo)

## Instalação

```bash
# instala o player mpv
brew install mpv

# instala a dependência python
python3 -m pip install -r requirements.txt

# torna executável e adiciona ao PATH
chmod +x ytwatch.py
mkdir -p ~/bin
cp ytwatch.py ~/bin/ytwatch
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Uso

```bash
ytwatch <url ou termo de busca>
ytwatch -q 720 <url ou busca>       # limita qualidade
ytwatch -a <url ou busca>           # só áudio
ytwatch -n 5 <termo de busca>       # escolhe entre 5 resultados
ytwatch -b <url ou busca>           # toca em segundo plano
```

### Exemplos

```bash
ytwatch https://youtube.com/watch?v=dQw4w9WgXcQ
ytwatch -q 720 lofi hip hop radio
ytwatch -a podcast sobre historia do brasil
ytwatch -n 5 receita de pao de queijo
ytwatch -b -a musica pra estudar
```

## Licença

Uso pessoal, sinta-se livre pra modificar.
