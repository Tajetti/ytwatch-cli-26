#!/usr/bin/env python3
"""
ytwatch - assiste YouTube direto no terminal, via mpv + yt-dlp

Uso:
  ytwatch.py <url ou termo de busca>
  ytwatch.py -q 720 <url ou busca>     -> limita qualidade
  ytwatch.py -a <url ou busca>         -> só áudio (sem vídeo)
  ytwatch.py -n 5 <termo de busca>     -> mostra 5 resultados pra escolher
  ytwatch.py -b <url ou busca>         -> toca em segundo plano (libera o terminal)

Dependências:
  pip install yt-dlp
  brew install mpv   (mpv precisa estar instalado no sistema, não é um pacote python)
"""

import argparse
import shutil
import subprocess
import sys

try:
    import yt_dlp
except ImportError:
    print("Erro: pacote 'yt-dlp' não encontrado. Instale com: pip install yt-dlp", file=sys.stderr)
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Assiste YouTube no terminal (mpv + yt-dlp)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemplos:
  ytwatch.py https://youtube.com/watch?v=dQw4w9WgXcQ
  ytwatch.py -q 720 lofi hip hop radio
  ytwatch.py -a podcast sobre historia do brasil
  ytwatch.py -n 5 receita de pao de queijo
  ytwatch.py -b -a musica pra estudar
""",
    )
    parser.add_argument("query", nargs="+", help="URL do vídeo ou termo de busca")
    parser.add_argument(
        "-q", "--quality", default="best",
        help="Limita a qualidade em altura de linhas (ex: 480, 720, 1080). Padrão: best",
    )
    parser.add_argument(
        "-a", "--audio", action="store_true",
        help="Só áudio, sem vídeo (economiza banda/CPU)",
    )
    parser.add_argument(
        "-n", "--num", type=int, default=1,
        help="Ao buscar por termo, mostra N resultados pra escolher (padrão: 1 = toca o primeiro direto)",
    )
    parser.add_argument(
        "-b", "--background", action="store_true",
        help="Toca em segundo plano, liberando o terminal (roda o mpv desacoplado)",
    )
    return parser.parse_args()


def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def check_mpv():
    if shutil.which("mpv") is None:
        print("Erro: 'mpv' não encontrado. Instale com: brew install mpv", file=sys.stderr)
        sys.exit(1)


def build_ytdl_format(quality: str) -> str:
    if quality == "best":
        return "best"
    return f"best[height<={quality}]"


def play(url: str, ytdl_format: str, audio_only: bool, background: bool):
    cmd = ["mpv", f"--ytdl-format={ytdl_format}"]
    if audio_only:
        cmd.append("--no-video")
    cmd.append(url)

    if not background:
        print(f"▶ Abrindo: {url}")
        subprocess.run(cmd, check=False)
        return

    # Modo segundo plano: desacopla o mpv do terminal (sem stdin/stdout/stderr
    # herdados e em nova sessão), assim ele continua tocando mesmo que você
    # feche este terminal ou rode outros comandos.
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print(f"▶ Tocando em segundo plano (PID {process.pid}): {url}")
    print(f"   Pra parar: kill {process.pid}")


def search_videos(query: str, num: int):
    """Busca vídeos no YouTube e retorna lista de dicts {title, id, url}."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,  # não baixa nada, só metadados
    }
    # OBS: default_search só é aplicado pelo yt-dlp via linha de comando.
    # Chamando extract_info() direto em Python, o prefixo de busca
    # (ytsearchN:) precisa ser montado manualmente.
    search_query = f"ytsearch{num}:{query}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

    entries = info.get("entries", []) if info else []
    results = []
    for entry in entries:
        if not entry:
            continue
        video_id = entry.get("id")
        title = entry.get("title", "sem título")
        results.append({
            "title": title,
            "id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })
    return results


def choose_video(results):
    print()
    for i, r in enumerate(results, start=1):
        print(f"  {i:2d}) {r['title']}")
    print()

    while True:
        choice = input(f"Escolha um vídeo [1-{len(results)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            return results[int(choice) - 1]
        print("Escolha inválida, tente de novo.")


def main():
    args = parse_args()
    check_mpv()

    query = " ".join(args.query)
    ytdl_format = build_ytdl_format(args.quality)

    if is_url(query):
        play(query, ytdl_format, args.audio, args.background)
        return

    if args.num <= 1:
        print(f"🔎 Buscando e abrindo: {query}")
        results = search_videos(query, 1)
        if not results:
            print("Nenhum resultado encontrado.", file=sys.stderr)
            sys.exit(1)
        play(results[0]["url"], ytdl_format, args.audio, args.background)
        return

    print(f'🔎 Buscando "{query}" (top {args.num})...')
    results = search_videos(query, args.num)
    if not results:
        print("Nenhum resultado encontrado.", file=sys.stderr)
        sys.exit(1)

    selected = choose_video(results)
    play(selected["url"], ytdl_format, args.audio, args.background)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompido.")
        sys.exit(130)
