"""Configuration for the Redrob Senior AI Engineer ranker.

All weights are intentionally explicit so the model can be explained in an
interview and tuned without touching parsing or orchestration code.
"""

CURRENT_DATE = "2026-06-25"
TOP_K = 100
DEFAULT_OUTPUT = "submission.csv"

INPUT_CANDIDATE_FILES = (
    "candidates.jsonl",
    "candidates.jsonl.gz",
)

PROFICIENCY_WEIGHTS = {
    "beginner": 0.45,
    "intermediate": 0.75,
    "advanced": 1.0,
    "expert": 1.2,
}

SKILL_WEIGHTS = {
    "python": 5.5,
    "embeddings": 5.4,
    "embedding": 5.4,
    "sentence transformers": 4.8,
    "retrieval": 5.5,
    "rag": 4.6,
    "ranking": 5.3,
    "learning to rank": 4.8,
    "information retrieval": 5.0,
    "search": 3.8,
    "nlp": 3.7,
    "llm": 3.7,
    "llms": 3.7,
    "faiss": 4.8,
    "milvus": 4.8,
    "qdrant": 4.8,
    "pinecone": 4.8,
    "weaviate": 4.8,
    "elasticsearch": 4.3,
    "opensearch": 4.3,
    "fine-tuning": 2.6,
    "fine tuning": 2.6,
    "lora": 2.5,
    "qlora": 2.5,
    "peft": 2.5,
    "a/b testing": 2.8,
    "ab testing": 2.8,
    "ndcg": 3.8,
    "mrr": 3.5,
    "map": 3.0,
    "evaluation": 2.6,
}

VECTOR_DB_TERMS = (
    "faiss",
    "milvus",
    "qdrant",
    "pinecone",
    "weaviate",
    "elasticsearch",
    "opensearch",
    "vector database",
    "vector db",
    "ann index",
    "nearest neighbor",
)

RETRIEVAL_TERMS = (
    "retrieval",
    "information retrieval",
    "semantic search",
    "hybrid search",
    "vector search",
    "dense retrieval",
    "rag",
    "recommendation",
    "recommender",
    "ranking",
    "ranker",
    "learning-to-rank",
    "learning to rank",
    "search relevance",
    "candidate matching",
    "matching system",
)

EMBEDDING_TERMS = (
    "embedding",
    "embeddings",
    "sentence transformer",
    "sentence-transformer",
    "bge",
    "e5",
    "semantic representation",
)

EVALUATION_TERMS = (
    "ndcg",
    "mrr",
    "mean average precision",
    "map",
    "precision@",
    "recall@",
    "offline evaluation",
    "online evaluation",
    "a/b test",
    "ab test",
    "ranking evaluation",
    "relevance evaluation",
)

PRODUCTION_TERMS = (
    "production",
    "deployed",
    "deployment",
    "scaling",
    "scale",
    "pipeline",
    "serving",
    "real users",
    "monitoring",
    "inference",
    "microservices",
    "architecture",
    "api",
    "apis",
    "latency",
    "throughput",
    "on-call",
    "reliability",
    "observability",
    "kubernetes",
    "docker",
    "airflow",
    "kafka",
    "spark",
    "feature store",
)

AI_TITLE_TERMS = (
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    "applied scientist",
    "search engineer",
    "ranking engineer",
    "nlp engineer",
    "mlops engineer",
)

ADJACENT_TECH_TITLE_TERMS = (
    "backend engineer",
    "data engineer",
    "software engineer",
    "full stack developer",
    "platform engineer",
    "analytics engineer",
)

NON_TECH_TITLE_TERMS = (
    "marketing manager",
    "operations manager",
    "hr manager",
    "sales executive",
    "accountant",
    "civil engineer",
    "mechanical engineer",
    "graphic designer",
    "content writer",
    "customer support",
)

CONSULTING_COMPANIES = (
    "tcs",
    "infosys",
    "wipro",
    "cognizant",
    "capgemini",
    "accenture",
    "mindtree",
    "hcl",
    "tech mahindra",
)

PRODUCT_INDUSTRIES = (
    "software",
    "fintech",
    "e-commerce",
    "ecommerce",
    "saas",
    "internet",
    "marketplace",
    "media",
    "edtech",
    "healthtech",
)

PREFERRED_CITIES = (
    "pune",
    "noida",
)

TIER1_INDIAN_CITIES = (
    "delhi",
    "gurgaon",
    "gurugram",
    "mumbai",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "chennai",
)

STEM_FIELDS = (
    "computer science",
    "artificial intelligence",
    "machine learning",
    "data science",
    "information technology",
    "statistics",
    "mathematics",
)

CV_SPEECH_ROBOTICS_TERMS = (
    "computer vision",
    "image classification",
    "object detection",
    "speech recognition",
    "tts",
    "robotics",
    "gan",
    "gans",
)

RECENT_LLM_ONLY_TERMS = (
    "langchain",
    "openai api",
    "chatgpt",
    "anthropic",
    "prompt engineering",
)
