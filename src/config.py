"""Configuração central: todos os scripts leem daqui para garantir o mesmo modelo e a mesma métrica."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ / "dados"
DIR_RESULTADOS = RAIZ / "resultados"
ARQ_BASE = DIR_DADOS / "base.json"
ARQ_PERGUNTAS = DIR_DADOS / "perguntas.json"

# Pasta do banco local. Fica fora do Git (.gitignore): quem clonar recria com indexar.py.
CAMINHO_CHROMA = RAIZ / "chroma_db"

MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DIMENSAO_ESPERADA = 384
LIMITE_TOKENS = 128
METRICA = "cosine"  # o padrão do Chroma é l2; e não dá para trocar depois de criar a coleção
DISPOSITIVO = "cpu"

# v1 = texto puro; v2 = melhoria (título do trecho prefixado ao texto). Ver README, seção "Melhoria".
COLECOES = {
    "v1": "conceitos_ia_v1",
    "v2": "conceitos_ia_v2",
}
