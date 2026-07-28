from src.pennantiq.retrieval import Retriever, rewrite_query

def test_hybrid_retrieval():
    r=Retriever(); out=r.hybrid("How should the system abstain when evidence is weak?",k=3)
    assert out and any("confidence" in d.doc_id for _,d in out)

def test_rewrite():
    assert "pitch family" in rewrite_query("What is the best pitch?")
