"""
PDF RAGシステム（Retrieval-Augmented Generation）

【注意】このファイルは後方互換性のために残されています。
新しいコードでは、以下のモジュールを直接インポートしてください：
- src.rag.loaders.pdf.PDFRagSystem
- src.rag.models.single_source.ReRankingRAG
- src.rag.models.multi_source.MultiSourceRagSystem
- src.rag.models.multi_source_reranking.MultiSourceReRankingRAG

または、より簡単に：
- from src.rag import PDFRagSystem, ReRankingRAG, MultiSourceRagSystem, MultiSourceReRankingRAG
"""

# 後方互換性のために、新しいモジュール構造からクラスをインポート
from src.rag import PDFRagSystem, ReRankingRAG, MultiSourceRagSystem, MultiSourceReRankingRAG

# __all__ を定義して、外部からインポートできるクラスを明示
__all__ = [
    'PDFRagSystem',
    'ReRankingRAG',
    'MultiSourceRagSystem',
    'MultiSourceReRankingRAG',
]
