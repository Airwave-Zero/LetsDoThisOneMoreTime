import os
import re
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==============================================================
# REGEX + LOOKUPS (FULL RESTORED SET)
# ==============================================================

import re
from typing import Dict, List, Tuple


# ── TITLE NORMALIZATION ───────────────────────────────────────

TITLE_PATTERNS: List[Tuple[str, str, str]] = [
    # (regex, standardized_title, job_family)

    # Data / AI
    (r"(?i)\bdata\s*scien", "Data Scientist", "Data"),
    (r"(?i)\bdata\s*analy", "Data Analyst", "Data"),
    (r"(?i)\bdata\s*eng", "Data Engineer", "Data"),
    (r"(?i)\banalytics?\s*eng", "Analytics Engineer", "Data"),
    (r"(?i)\bbi\s*analyst|\bbusiness\s*intell", "BI Analyst", "Data"),
    (r"(?i)\bdata\s*ops", "Data Operations", "Data"),
    (r"(?i)\bml\s*architect|\bai/ml\s*arch|\bai\/ml\s*arch", "ML Architect", "Data"),
    (r"(?i)\bml\b|\bmachine\s*learn", "ML Engineer", "Data"),
    (r"(?i)\bai\s*eng|\bai\s*research", "AI Engineer", "Data"),
    (r"(?i)\bresearch\s*scien", "Research Scientist", "Data"),

    # Software
    (r"(?i)\bfront[-\s]?end|\bfrontend", "Frontend Engineer", "Software"),
    (r"(?i)\bback[-\s]?end|\bbackend", "Backend Engineer", "Software"),
    (r"(?i)\bfull[-\s]?stack", "Full-Stack Engineer", "Software"),
    (r"(?i)\bdevops", "DevOps Engineer", "Software"),
    (r"(?i)\bsre\b|\bsite\s*reliab", "SRE", "Software"),
    (r"(?i)\binfra(?:structure)?\s*eng", "Infrastructure Engineer", "Software"),
    (r"(?i)\bcloud\s*infrastructure", "Cloud Infrastructure Engineer", "Software"),
    (r"(?i)\bcloud\s*(?:soft|eng|engineer)", "Cloud Engineer", "Software"),
    (r"(?i)\bplatform\s*eng", "Platform Engineer", "Software"),
    (r"(?i)\bsystems?\s*eng", "Systems Engineer", "Software"),
    (r"(?i)\bsecurity\s*eng", "Security Engineer", "Software"),
    (r"(?i)\bqa\b|\bquality\s*assur|\btest\s*eng", "QA Engineer", "Software"),
    (r"(?i)\beng(?:ineering)?\s*manage", "Engineering Manager", "Software"),
    (r"(?i)\bsoftware\s*eng(?!.*manage)", "Software Engineer", "Software"),
    (r"(?i)\bblockchain|\bsolidity|\bweb3", "Blockchain Engineer", "Software"),

    # Design / Product
    (r"(?i)\bproduct\s*design", "Product Designer", "Design"),
    (r"(?i)\bux\s*research", "UX Researcher", "Design"),
    (r"(?i)\bux\s*design|\bui/ux|\bui\s*/\s*ux", "UX Designer", "Design"),
    (r"(?i)\bproduct\s*owner", "Product Owner", "Product"),
    (r"(?i)\bprogram\s*manage", "Program Manager", "Product"),
    (r"(?i)\bproduct\s*manage|\bpm\b", "Product Manager", "Product"),

    # Marketing
    (r"(?i)\bproduct\s*market", "Product Marketing Manager", "Marketing"),
    (r"(?i)\bgrowth\s*(?:analy|market)", "Growth Analyst", "Marketing"),
    (r"(?i)\bmarketing\s*(?:manage|intern|direct)", "Marketing Manager", "Marketing"),
    (r"(?i)\bcontent\s*writ", "Content Writer", "Marketing"),
    (r"(?i)\bsocial\s*media", "Social Media Manager", "Marketing"),
    (r"(?i)\bcommunity", "Community Specialist", "Marketing"),

    # Sales / Customer Success / Support
    (r"(?i)\bsales\s*eng", "Sales Engineer", "Sales"),
    (r"(?i)\baccount\s*exec", "Account Executive", "Sales"),
    (r"(?i)\bsolutions?\s*eng", "Solutions Engineer", "Sales"),
    (r"(?i)\bpre[\s-]?sales", "Pre-Sales Engineer", "Sales"),
    (r"(?i)\btechnical\s*account", "Technical Account Manager", "Customer Success"),
    (r"(?i)\bcustomer\s*success", "Customer Success Manager", "Customer Success"),
    (r"(?i)\bcustomer\s*eng", "Customer Engineer", "Customer Success"),
    (r"(?i)\bcustomer\s*support", "Customer Support", "Support"),
    (r"(?i)\benablement", "Enablement Specialist", "Support"),

    # People / Finance / Compliance
    (r"(?i)\bhead\s*of\s*people|\bpeople\s*(?:partner|ops|operations|lead|manager)|\bhr\b|\bhuman\s*resources", "People/HR Lead", "People"),
    (r"(?i)\bfp&a|\bfinancial\s*planning", "FP&A", "Finance"),
    (r"(?i)\brisk\s*(?:analyst|manager)", "Risk Management", "Finance"),
    (r"(?i)\bfinance|\baccountan|\brevenue\s*acc", "Finance/Accounting", "Finance"),
    (r"(?i)\bcompliance", "Compliance Specialist", "Compliance"),
    (r"(?i)\btreasury", "Treasury", "Finance"),
    (r"(?i)\bunderwrit", "Underwriting", "Finance"),
    (r"(?i)\binvestigat", "Investigator", "Compliance"),

    # Operations / IT / Localization
    (r"(?i)\bbusiness\s*op|\brevenue\s*op", "Revenue/Biz Ops", "Operations"),
    (r"(?i)\bit\s*project|\bit\s*manage", "IT Project Manager", "IT"),
    (r"(?i)\btranslat", "Translator", "Localization"),
    (r"(?i)\btechnician\b|\bproduction\s*technician", "Technician", "Operations"),
    (r"(?i)\bsupply\s*chain", "Supply Chain", "Operations"),
    (r"(?i)\blogistics", "Logistics", "Operations"),
    (r"(?i)\bwarehouse", "Warehouse Operations", "Operations"),

    # Healthcare
    (r"(?i)\bmedical\s*assistant", "Medical Assistant", "Healthcare"),
    (r"(?i)\bphysician|\bmd\b|\bdoctor\b", "Physician", "Healthcare"),
    (r"(?i)\bnurse|\bnp\b|\bnurse\s*practitioner", "Nurse Practitioner", "Healthcare"),
    (r"(?i)\bclinical", "Clinical Specialist", "Healthcare"),

    # Hardware
    (r"(?i)\bmanufactur", "Manufacturing Engineer", "Hardware"),
    (r"(?i)\bmechanical\s*eng", "Mechanical Engineer", "Hardware"),
    (r"(?i)\belectrical\s*eng", "Electrical Engineer", "Hardware"),
    (r"(?i)\brobotics?", "Robotics Engineer", "Hardware"),
    (r"(?i)\bembedded", "Embedded Engineer", "Hardware"),

    # Education
    (r"(?i)\bteacher|\beducator|\binstructor", "Teacher", "Education"),

    # Leadership - keep broad leadership near bottom to avoid swallowing specific titles
    (r"(?i)\bhead\s*of", "Head of Department", "Leadership"),
    (r"(?i)\bdirector", "Director", "Leadership"),
]

COMPILED_TITLE_PATTERNS = [(re.compile(p), t, f) for p, t, f in TITLE_PATTERNS]


SENIORITY_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"(?i)\bintern\b|\bentry[-\s]?level\b|\bjunior\b|\bjr\b|\bassociate\b|\btrainee\b"), "Junior"),
    (re.compile(r"(?i)\bii\b|\biii\b|\bmid[-\s]?level\b|\bintermediate\b"), "Mid"),
    (re.compile(r"(?i)\bsenior\b|\bsr\b|\blead\b|\bprincipal\b|\bstaff\b"), "Senior"),
    (re.compile(r"(?i)\bmanager\b|\bdirector\b|\bvp\b|\bhead\s*of\b|\bchief\b|\bc[-\s]?level\b"), "Leadership"),
]


REMOTE_PATTERNS: Dict[str, re.Pattern] = {
    "Remote": re.compile(r"(?i)\bremote\b|\bdistributed\b|\bwork\s*from\s*home\b|\bwork\s*from\s*anywhere\b|\bremote[-\s]*first\b|\bfully[-\s]*remote\b"),
    "Hybrid": re.compile(r"(?i)\bhybrid\b|\bhybrid[-\s]*remote\b"),
    "Onsite": re.compile(r"(?i)\bonsite\b|\bin[-\s]*person\b|\boffice[-\s]*based\b"),
}


# ── SKILL LOOKUPS ─────────────────────────────────────────────


SKILL_CATEGORIES: Dict[str, List[str]] = {

    "Programming": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang",
        "Rust", "Ruby", "Scala", "PHP", "Swift", "Kotlin", "R",
        "MATLAB", "Bash", "Shell", "PowerShell",
    ],

    "Frontend": [
        "React", "Angular", "Vue", "Next.js", "Nuxt",
        "HTML", "CSS", "Sass", "Less",
        "Tailwind", "Bootstrap", "Material UI",
        "Svelte", "jQuery",
        "Webpack", "Vite", "Babel",
        "Storybook",
    ],

    "Backend": [
        "Node", "Node.js", "Java", "Python", "C++", "C#",
        "Express", "NestJS",
        "Django", "Flask", "FastAPI",
        "Spring", "Spring Boot",
        "ASP.NET", "ASP.NET Core",
        "GraphQL", "REST", "gRPC",
        "Message Queues", "RabbitMQ",
        "Microservices", "Monolith",
    ],

    "Cloud": [
        "AWS", "GCP", "Azure",
        "Cloudflare", "Heroku",
        "Terraform", "Pulumi",
        "CloudFormation",
        "Serverless", "Lambda", "Functions",
        "EC2", "ECS", "EKS",
        "S3", "GCS", "Blob Storage",
        "IAM", "VPC",
    ],

    "Data": [
        "SQL", "NoSQL",
        "Spark", "PySpark",
        "Pandas", "NumPy",
        "Scikit", "Scikit-Learn",
        "TensorFlow", "PyTorch",
        "DBT",
        "Snowflake", "Redshift", "BigQuery", "Databricks",
        "Kafka", "Kinesis",
        "Airflow", "Prefect", "Dagster",
        "ETL", "ELT",
        "Athena", "Presto", "Trino",
        "Sigma", "Looker Studio",
        "Data Modeling", "Data Warehousing",
    ],

    "DevOps": [
        "Docker", "Kubernetes",
        "Terraform", "Pulumi",
        "CI/CD", "GitHub Actions", "GitLab CI",
        "Jenkins", "CircleCI",
        "Ansible", "Chef", "Puppet",
        "Helm",
        "ArgoCD", "Flux",
        "Datadog", "Prometheus", "Grafana",
        "SRE",
    ],

    "ML/AI": [
        "Machine Learning", "Deep Learning",
        "NLP", "Computer Vision",
        "Transformers", "Attention",
        "LLM", "Large Language Models",
        "GPT", "BERT",
        "Neural Network",
        "Generative AI", "Diffusion",
        "Feature Engineering",
        "Model Training", "Model Evaluation",
        "MLOps",
    ],

    "Tools": [
        "Git", "GitHub", "GitLab", "Bitbucket",
        "Jira", "Confluence",
        "Figma", "Notion",
        "VS Code", "PyCharm", "IntelliJ",
        "Postman", "Swagger",
        "Docker Desktop",
    ],

    "Methodology": [
        "Agile", "Scrum", "Kanban",
        "Waterfall",
        "Lean",
        "Test-Driven Development", "TDD",
        "Behavior-Driven Development", "BDD",
    ],

    "Database": [
        "PostgreSQL", "MySQL", "SQL Server", "Oracle",
        "MongoDB", "Redis",
        "Elasticsearch", "OpenSearch",
        "DynamoDB", "Cassandra",
        "DuckDB", "SQLite",
        "Snowflake",
        "Cosmos DB",
        "Time Series Databases",
    ],

    "Blockchain": [
        "Solidity", "Ethereum", "Solana", "Web3",
        "Smart Contracts",
        "Hardhat", "Foundry",
    ],

    "Data Analysis": [
        "Data Analysis", "Statistics",
        "Excel", "Google Sheets",
        "Tableau", "Power BI", "Looker",
        "DAX", "Power Query",
        "A/B Testing",
        "Visualization",
        "Business Intelligence",
    ],

    "Security": [
        "SIEM", "SOAR",
        "IAM", "RBAC",
        "OAuth", "OIDC",
        "OWASP",
        "Zero Trust",
        "Penetration Testing",
        "Vulnerability Management",
    ],
}



# Safe canonical names for storage / columns / pyarrow operations

SKILL_ALIASES: Dict[str, str] = {
    # ---- Languages ----
    "c++": "cpp",
    "C++": "cpp",
    "c#": "csharp",
    "C#": "csharp",

    # ---- JavaScript ecosystem ----
    "node.js": "nodejs",
    "node js": "nodejs",
    "next.js": "nextjs",
    "nuxt.js": "nuxtjs",
    "react.js": "react",
    "vue.js": "vue",
    "angular.js": "angular",

    # ---- DevOps / CI ----
    "ci/cd": "cicd",
    "ci cd": "cicd",
    "github actions": "github_actions",
    "gitlab ci": "gitlab_ci",
    "circle ci": "circleci",
    "argo cd": "argocd",

    # ---- Data / ML ----
    "scikit-learn": "scikit",
    "scikit learn": "scikit",
    "machine learning": "machine_learning",
    "deep learning": "deep_learning",
    "computer vision": "computer_vision",
    "natural language processing": "nlp",
    "large language models": "llm",
    "neural network": "neural_network",
    "neural networks": "neural_networks",
    "generative ai": "generative_ai",
    "feature engineering": "feature_engineering",
    "data modeling": "data_modeling",
    "data warehousing": "data_warehousing",

    # ---- BI / Analytics ----
    "power bi": "powerbi",
    "power query": "power_query",
    "looker studio": "looker_studio",
    "google sheets": "google_sheets",
    "a/b testing": "ab_testing",
    "ab testing": "ab_testing",
    "business intelligence": "business_intelligence",
    "data analysis": "data_analysis",

    # ---- Cloud / Infra ----
    "cloud formation": "cloudformation",
    "aws lambda": "lambda",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure functions": "azure_functions",
    "serverless": "serverless",

    # ---- APIs / Protocols ----
    "rest api": "rest",
    "restful api": "rest",
    "grpc": "grpc",            # kept explicit for safety
    "graph ql": "graphql",

    # ---- Security / Auth ----
    "role based access control": "rbac",
    "identity and access management": "iam",
    "zero trust": "zero_trust",
    "penetration testing": "penetration_testing",

    # ---- Methodologies ----
    "test driven development": "tdd",
    "behavior driven development": "bdd",

    # ---- Misc / Text Variants ----
    "message queues": "message_queues",
    "micro services": "microservices",
    "time series databases": "time_series_databases",
}


def canonical_skill(skill: str) -> str:

    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill)


def normalize_company_name(name: str) -> str:
    """Normalize company name for consistent display.
    
    Rules:
      - If first character is a letter, capitalize it
      - If starts with a number, capitalize the first letter after the number
      - Handle edge cases (empty strings, None)
    
    Examples:
      - "apple" → "Apple"
      - "3m" → "3M"
      - "123abc" → "123Abc"
    """
    if not name or not isinstance(name, str):
        return name
    
    name = name.strip()
    if not name:
        return name
    
    # Find the first alphabetic character
    for i, char in enumerate(name):
        if char.isalpha():
            # Capitalize that character and return
            return name[:i] + char.upper() + name[i+1:]
    
    # If no alphabetic character found (all numbers/symbols), return as-is
    return name

SKILL_TO_CATEGORY: Dict[str, str] = {
    canonical_skill(skill): category
    for category, skills in SKILL_CATEGORIES.items()
    for skill in skills
}

ALL_KNOWN_SKILLS: List[str] = sorted(SKILL_TO_CATEGORY)

COMPILED_SKILLS: Dict[str, Tuple[re.Pattern, str]] = {
    skill: (
        re.compile(rf"(?<!\w){re.escape(skill)}(?!\w)", re.IGNORECASE),
        canonical_skill(skill),
    )
    for skills in SKILL_CATEGORIES.values()
    for skill in skills
}


# ── BUZZWORD / COMPLEXITY LOOKUPS ─────────────────────────────

BUZZWORDS: List[str] = [
    "synergy", "leverage", "disrupt", "innovate", "empower",
    "paradigm", "scalable", "ecosystem", "blockchain", "holistic",
    "cutting-edge", "world-class", "best-in-class", "game-changer",
    "thought leader", "rockstar", "ninja", "guru", "unicorn",
    "fast-paced", "self-starter", "wear many hats", "dynamic",
    "passion", "crushing it", "move the needle", "bandwidth",
    "low-hanging fruit", "deep dive", "circle back",
]

_BUZZWORD_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(b) for b in BUZZWORDS) + r")\b",
    re.IGNORECASE,
)


INCLUSIVE_TERMS: List[str] = [
    "equal opportunity", "diversity", "inclusion", "accommodation",
    "accessible", "belonging", "equity",
]

_INCLUSIVE_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(t) for t in INCLUSIVE_TERMS) + r")\b",
    re.IGNORECASE,
)


# ── DOMAIN PATTERNS ───────────────────────────────────────────

DOMAIN_PATTERNS: List[Tuple[str, str]] = [
    (r"(?i)\bfintech|\bbanking|\bpayment|\blending|\bmortgage", "FinTech"),
    (r"(?i)\bhealthcare|\bmedical|\bhospice|\bclinical|\bnhs|\bhealth\s*system", "Healthcare"),
    (r"(?i)\bweb3|\bblockchain|\bcrypto|\bdecentrali|\bnft", "Web3/Crypto"),
    (r"(?i)\bsolar|\benergy|\bclimate|\bsustainab|\brenewable", "CleanTech/Energy"),
    (r"(?i)\bgaming|\bgame\b", "Gaming"),
    (r"(?i)\binsur", "InsurTech"),
    (r"(?i)\bedtech|\beducat|\blearn|\bschool|\bacademic", "EdTech"),
    (r"(?i)\bsaas", "SaaS"),
    (r"(?i)\be[-\s]?commerce|\bretail", "E-commerce/Retail"),
    (r"(?i)\bsecurity|\bcyber", "Cybersecurity"),
    (r"(?i)\bmedia|\bfilm|\bstream|\bcontent", "Media/Entertainment"),
    (r"(?i)\badtech|\badvertis", "AdTech"),
    (r"(?i)\blogistics|\bwarehouse", "Logistics"),
    (r"(?i)\brobotics|\bautomation", "Robotics"),
    (r"(?i)\baerospace|\baviation|\bspacecraft|\bsatellite", "Aerospace"),
    (r"(?i)\bmanufactur", "Manufacturing"),
    (r"(?i)\bgovernment|\bpublic\s*sector", "Public Sector"),
]

COMPILED_DOMAIN_PATTERNS = [(re.compile(p), d) for p, d in DOMAIN_PATTERNS]


# ── GEO NORMALIZATION LOOKUPS ─────────────────────────────────

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}

US_STATE_ABBREV: Dict[str, str] = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}

_STATE_FULL_TO_ABBREV = {v.lower(): k for k, v in US_STATE_ABBREV.items()}

# Optional non-US subdivision/state aliases
NON_US_REGION_ABBREV: Dict[str, str] = {
    "ontario": "ON",
    "quebec": "QC",
    "british columbia": "BC",
    "karnataka": "KA",
    "são paulo": "SP",
    "sao paulo": "SP",
    "bavaria": "BY",
}


GEO_CLUSTERS_US: Dict[str, set] = {
    "West Coast": {"CA", "OR", "WA"},
    "East Coast": {"NY", "NJ", "CT", "MA", "PA", "MD", "VA", "DC", "FL", "NC", "GA"},
    "Midwest": {"IL", "OH", "MI", "IN", "WI", "MN", "MO", "IA"},
    "South": {"TX", "TN", "AL", "LA", "AR", "MS", "KY", "SC"},
    "Mountain": {"CO", "UT", "AZ", "NV", "ID", "MT", "WY", "NM"},
}


CITY_ALIASES: Dict[str, str] = {
    "nyc": "new york city",
    "sf": "san francisco",
    "sfo": "san francisco",
    "la": "los angeles",
    "dc": "washington",
    "washington dc": "washington",
    "washington d.c.": "washington",
    "d.c.": "washington",
    "slc": "salt lake city",
    "sea": "seattle",
    "bos": "boston",
    "chi": "chicago",
    "dal": "dallas",
    "hou": "houston",
    "atx": "austin",
    "pdx": "portland",
    "phx": "phoenix",
    "det": "detroit",
    "msp": "minneapolis",
    "pit": "pittsburgh",
    "rdu": "raleigh",
    "clt": "charlotte",
    "den": "denver",
    "oak": "oakland",
    "bk": "brooklyn",
    "mv": "mountain view",
    "cdmx": "mexico city",
    "bengaluru": "bangalore",
    "sao paulo": "são paulo",
    "kiev": "kyiv",
    "vienna": "wien",
}


CITY_TO_STATE: Dict[str, str] = {
    # US - existing/core
    "san francisco": "CA",
    "new york": "NY",
    "new york city": "NY",
    "los angeles": "CA",
    "seattle": "WA",
    "denver": "CO",
    "carrollton": "TX",
    "oakland": "CA",
    "santa ana": "CA",
    "chicago": "IL",
    "austin": "TX",
    "boston": "MA",
    "portland": "OR",
    "san diego": "CA",
    "miami": "FL",
    "atlanta": "GA",
    "washington": "DC",
    "philadelphia": "PA",
    "dallas": "TX",
    "houston": "TX",
    "phoenix": "AZ",
    "detroit": "MI",
    "minneapolis": "MN",
    "nashville": "TN",
    "raleigh": "NC",
    "charlotte": "NC",
    "pittsburgh": "PA",
    "salt lake city": "UT",

    # US - California
    "bay area": "CA",
    "berkeley": "CA",
    "carlsbad": "CA",
    "chula vista": "CA",
    "el segundo": "CA",
    "emeryville": "CA",
    "foster city": "CA",
    "huntington beach": "CA",
    "irvine": "CA",
    "kearny mesa": "CA",
    "los gatos": "CA",
    "marina del rey": "CA",
    "menlo park": "CA",
    "mountain view": "CA",
    "palo alto": "CA",
    "poway": "CA",
    "redwood city": "CA",
    "sacramento": "CA",
    "san fernando": "CA",
    "san jose": "CA",
    "san marcos": "CA",
    "san mateo": "CA",
    "santa clara": "CA",
    "santa rosa": "CA",
    "silicon valley": "CA",
    "west los angeles": "CA",

    # US - other states
    "arlington": "VA",
    "arvada": "CO",
    "aurora": "CO",
    "bellevue": "WA",
    "billings": "MT",
    "boise city": "ID",
    "boulder": "CO",
    "brooklyn": "NY",
    "buffalo": "NY",
    "chantilly": "VA",
    "cherry creek": "CO",
    "cheyenne": "WY",
    "culpeper": "VA",
    "culpepper": "VA",
    "eighty four": "PA",
    "el paso": "TX",
    "falls church": "VA",
    "hobbs": "NM",
    "indianapolis": "IN",
    "jackson hole": "WY",
    "lehi": "UT",
    "mesa": "AZ",
    "nashville-davidson": "TN",
    "ponchatoula": "LA",
    "roosevelt": "UT",
    "royal oak": "MI",
    "spring": "TX",
    "tulsa": "OK",
    "walden": "CO",
    "weirton": "WV",
    "williston": "ND",

    # Canada provinces
    "montreal": "QC",
    "ottawa": "ON",
    "toronto": "ON",
    "vancouver": "BC",

    # India/Brazil local states/regions
    "bangalore": "KA",
    "bengaluru": "KA",
    "delhi": "DL",
    "hyderabad": "TG",
    "jaipur": "RJ",
    "pune": "MH",
    "são paulo": "SP",
    "sao paulo": "SP",

    # International region/state-like codes
    "bogota": "DC",
    "bogotá": "DC",
    "mexico city": "CDMX",
    "sydney": "NSW",
    "melbourne": "VIC",
    "tokyo": "TK",
    "shanghai": "SH",
}


CITY_TO_COUNTRY: Dict[str, str] = {
    # Core international
    "london": "UK",
    "paris": "FR",
    "berlin": "DE",
    "amsterdam": "NL",
    "lisbon": "PT",
    "milan": "IT",
    "pisa": "IT",
    "maastricht": "NL",
    "oslo": "NO",
    "dubai": "AE",
    "seoul": "KR",
    "nairobi": "KE",
    "toronto": "CA",
    "jakarta": "ID",
    "bangalore": "IN",
    "bengaluru": "IN",
    "são paulo": "BR",
    "sao paulo": "BR",
    "manila": "PH",
    "philippines": "PH",
    "latin america": "LATAM",
    "remote": "REMOTE",

    # US cities / areas
    "atlanta": "US",
    "arlington": "US",
    "arvada": "US",
    "aurora": "US",
    "austin": "US",
    "bay area": "US",
    "bellevue": "US",
    "berkeley": "US",
    "billings": "US",
    "boise city": "US",
    "boston": "US",
    "boulder": "US",
    "brooklyn": "US",
    "buffalo": "US",
    "carlsbad": "US",
    "carrollton": "US",
    "chantilly": "US",
    "charlotte": "US",
    "cherry creek": "US",
    "cheyenne": "US",
    "chicago": "US",
    "chula vista": "US",
    "culpeper": "US",
    "culpepper": "US",
    "dallas": "US",
    "denver": "US",
    "detroit": "US",
    "eighty four": "US",
    "el paso": "US",
    "el segundo": "US",
    "emeryville": "US",
    "falls church": "US",
    "foster city": "US",
    "hobbs": "US",
    "houston": "US",
    "huntington beach": "US",
    "indianapolis": "US",
    "irvine": "US",
    "jackson hole": "US",
    "kearny mesa": "US",
    "lehi": "US",
    "los angeles": "US",
    "los gatos": "US",
    "marina del rey": "US",
    "menlo park": "US",
    "mesa": "US",
    "miami": "US",
    "minneapolis": "US",
    "mountain view": "US",
    "nashville": "US",
    "nashville-davidson": "US",
    "new york": "US",
    "new york city": "US",
    "oakland": "US",
    "palo alto": "US",
    "philadelphia": "US",
    "phoenix": "US",
    "pittsburgh": "US",
    "ponchatoula": "US",
    "portland": "US",
    "poway": "US",
    "raleigh": "US",
    "redwood city": "US",
    "roosevelt": "US",
    "royal oak": "US",
    "sacramento": "US",
    "salt lake city": "US",
    "san diego": "US",
    "san fernando": "US",
    "san francisco": "US",
    "san jose": "US",
    "san marcos": "US",
    "san mateo": "US",
    "santa ana": "US",
    "santa clara": "US",
    "santa fe": "US",
    "santa rosa": "US",
    "seattle": "US",
    "silicon valley": "US",
    "spring": "US",
    "tribeca": "US",
    "tulsa": "US",
    "walden": "US",
    "washington": "US",
    "weirton": "US",
    "west los angeles": "US",
    "williston": "US",

    # Canada
    "montreal": "CA",
    "ottawa": "CA",
    "vancouver": "CA",

    # Latin America
    "bogota": "CO",
    "bogotá": "CO",
    "buenos aires": "AR",
    "capital federal": "AR",
    "cabo": "MX",
    "medellin": "CO",
    "mexico city": "MX",
    "santiago": "CL",

    # Europe
    "aarhus": "DK",
    "barcelona": "ES",
    "belgrade": "RS",
    "bergen": "NO",
    "bilbao": "ES",
    "brussels": "BE",
    "bremen": "DE",
    "budapest": "HU",
    "christchurch": "NZ",
    "costa brava": "ES",
    "dublin": "IE",
    "frankfurt am main": "DE",
    "gdansk": "PL",
    "gothenburg": "SE",
    "hamburg": "DE",
    "hannover": "DE",
    "ingolstadt": "DE",
    "istanbul": "TR",
    "kyiv": "UA",
    "kiev": "UA",
    "konstanz": "DE",
    "lehrte": "DE",
    "leipzig": "DE",
    "ljubljana": "SI",
    "madrid": "ES",
    "manchester": "UK",
    "munich": "DE",
    "nantes": "FR",
    "nottingham": "UK",
    "oxford": "UK",
    "porto": "PT",
    "prague": "CZ",
    "rome": "IT",
    "sevenoaks": "UK",
    "sofia": "BG",
    "stuttgart": "DE",
    "toulouse": "FR",
    "warsaw": "PL",
    "wien": "AT",
    "vienna": "AT",
    "zamudio": "ES",
    "zug": "CH",
    "zurich": "CH",

    # Asia-Pacific
    "bangkok": "TH",
    "delhi": "IN",
    "delhi ncr": "IN",
    "hangzhou": "CN",
    "hong kong": "HK",
    "hyderabad": "IN",
    "jaipur": "IN",
    "kotte": "LK",
    "melbourne": "AU",
    "pune": "IN",
    "shanghai": "CN",
    "singapore": "SG",
    "sydney": "AU",
    "taipei": "TW",
    "tel aviv": "IL",
    "tel aviv-yafo": "IL",
    "tokyo": "JP",
    "ulaanbaatar": "MN",

    # Africa
    "accra": "GH",
    "amalinda": "ZA",
    "bugembe": "UG",
    "central region": "UG",
    "eastern cape": "ZA",
    "lagos": "NG",
    "lusaka": "ZM",
    "mdantsane": "ZA",
    "mumbwa": "ZM",
    "kapiri mposhi": "ZM",
    "polokwane": "ZA",
    "somolu": "NG",
    "soweto": "ZA",
    "turfloop": "ZA",
}


REGION_KEYWORDS: Dict[str, str] = {
    "REMOTE": r"(?i)\bremote\b|\bremote[-\s]*first\b|\bfully[-\s]*remote\b|\bwork\s*from\s*anywhere\b|\bdistributed\b|\bwork\s*from\s*home\b",
    "HYBRID": r"(?i)\bhybrid\b|\bhybrid[-\s]*remote\b",
    "ONSITE": r"(?i)\bonsite\b|\bin[-\s]*person\b|\boffice[-\s]*based\b",

    "NA": r"(?i)\bna\b|\bnam\b|\bnorth\s*america\b",
    "AMER": r"(?i)\bamer\b|\bamers\b|\bamericas\b",
    "LATAM": r"(?i)\blatam\b|\blatin\s*america\b",
    "EU": r"(?i)\beurope\b|\beu\b|\beuropean\s*union\b",
    "EMEA": r"(?i)\bemea\b|\beurope,\s*middle\s*east,\s*africa\b",
    "APAC": r"(?i)\bapac\b|\basia[-\s]*pacific\b",
    "DACH": r"(?i)\bdach\b",
    "UKI": r"(?i)\buk[&\s]*i\b|\buk\s*and\s*ireland\b|united\s*kingdom\s*and\s*ireland",
    "BENELUX": r"(?i)\bbenelux\b",

    "MIDDLE_EAST": r"(?i)\bmiddle\s*east\b",
    "AFRICA": r"(?i)\bafrica\b",
    "NORTH_AFRICA": r"(?i)\bnorth\s*africa\b",
    "AFRANIL": r"(?i)\bafranil\b|\bnorth\s*africa\b|\bfrance\b|\bisrael\b",

    "SOUTH_AMERICA": r"(?i)\bsouth\s*america\b",
    "CENTRAL_AMERICA": r"(?i)\bcentral\s*america\b",
    "CARIBBEAN": r"(?i)\bcaribbean\b",

    "SOUTHEAST_ASIA": r"(?i)\bsoutheast\s*asia\b",
    "EAST_ASIA": r"(?i)\beast\s*asia\b",
    "SOUTH_ASIA": r"(?i)\bsouth\s*asia\b",
    "OCEANIA": r"(?i)\boceania\b",

    "WESTERN_EUROPE": r"(?i)\bwestern\s*europe\b",
    "EASTERN_EUROPE": r"(?i)\beastern\s*europe\b|\beastern\s*eu\b",
    "NORTHERN_EUROPE": r"(?i)\bnorthern\s*europe\b|\bnorthern\s*eu\b",
    "SOUTHERN_EUROPE": r"(?i)\bsouthern\s*europe\b|\bsouthern\s*eu\b",
    "CENTRAL_EUROPE": r"(?i)\bcentral\s*europe\b|\bcet\b",

    "BAY_AREA": r"(?i)\bbay\s*area\b|\bsilicon\s*valley\b",
    "WEST_COAST": r"(?i)\bwest\s*coast\b|\bpacific\s*time\b|\bpt\b|\bpst\b",
    "EAST_COAST": r"(?i)\beast\s*coast\b|\beastern\s*time\b|\bet\b|\best\b",
    "MIDWEST": r"(?i)\bmidwest\b",
    "ROCKIES": r"(?i)\brockies\b|\bmountain\s*time\b|\bmt\b|\bmst\b",
    "NORTHEAST_US": r"(?i)\bnortheast\b",
    "SOUTHEAST_US": r"(?i)\bsoutheast\b",
}

COMPILED_REGION_KEYWORDS = {
    region: re.compile(pattern)
    for region, pattern in REGION_KEYWORDS.items()
}

# Only use this for explicitly-parsed COUNTRY fields (not state fields).
# 2-letter codes are avoided to prevent CA (Canada vs California), CO (Colombia vs Colorado),
# IN (India vs Indiana), etc. ambiguity.
# Always parse city/state/country separately in _parse_location().
COUNTRY_ALIASES: Dict[str, str] = {
    # United States — avoid "us" because it is 2 letters
    "united states": "United States",
    "united states of america": "United States",
    "usa": "United States",
    "u.s.a.": "United States",

    # United Kingdom / Ireland — avoid "uk" because it is 2 letters
    "united kingdom": "United Kingdom",
    "great britain": "United Kingdom",
    "britain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "northern ireland": "United Kingdom",
    "ireland": "Ireland",

    # Canada — never use "ca" alone
    "canada": "Canada",
    "canadian": "Canada",

    # Europe
    "germany": "Germany",
    "france": "France",
    "spain": "Spain",
    "italy": "Italy",
    "netherlands": "Netherlands",
    "belgium": "Belgium",
    "austria": "Austria",
    "switzerland": "Switzerland",
    "sweden": "Sweden",
    "norway": "Norway",
    "denmark": "Denmark",
    "finland": "Finland",
    "portugal": "Portugal",
    "poland": "Poland",
    "czech republic": "Czech Republic",
    "czechia": "Czech Republic",
    "hungary": "Hungary",
    "romania": "Romania",
    "bulgaria": "Bulgaria",
    "serbia": "Serbia",
    "ukraine": "Ukraine",
    "greece": "Greece",
    "turkey": "Turkey",
    "slovenia": "Slovenia",

    # Asia-Pacific
    "china": "China",
    "japan": "Japan",
    "south korea": "South Korea",
    "korea": "South Korea",
    "sri lanka": "Sri Lanka",
    "new zealand": "New Zealand",
    "philippines": "Philippines",
    "singapore": "Singapore",
    "taiwan": "Taiwan",
    "thailand": "Thailand",
    "india": "India",
    "australia": "Australia",
    "hong kong": "Hong Kong",
    "indonesia": "Indonesia",

    # Middle East
    "united arab emirates": "United Arab Emirates",
    "uae": "United Arab Emirates",
    "israel": "Israel",

    # Latin America
    "mexico": "Mexico",
    "brazil": "Brazil",
    "argentina": "Argentina",
    "chile": "Chile",
    "colombia": "Colombia",
    "costa rica": "Costa Rica",

    # Africa
    "kenya": "Kenya",
    "nigeria": "Nigeria",
    "uganda": "Uganda",
    "south africa": "South Africa",
    "zambia": "Zambia",
    "ghana": "Ghana",

    # Remote
    "remote": "Remote",

    # Region-like aliases
    "latam": "Latin America",
    "latin america": "Latin America",
    "emea": "Europe, Middle East, Africa",
    "apac": "Asia-Pacific",
    "dach": "Germany, Austria, Switzerland",
    "amer": "Americas",
    "amers": "Americas",
    "americas": "Americas",
    "europe": "Europe",
    "european union": "Europe",
    "benelux": "Belgium, Netherlands, Luxembourg",
    "uki": "United Kingdom and Ireland",
    "uk&i": "United Kingdom and Ireland",
    "united kingdom and ireland": "United Kingdom and Ireland",
}


# Regex to pull "City, ST", "City, State", or "City, ST, Country"
_GEO_RE = re.compile(
    r"^(?P<city>[A-Za-z .'\-&]+?)\s*,\s*(?P<state>[A-Za-z .]+?)(?:\s*,\s*(?P<country>.+))?$"
)

# ==============================================================
# HELPERS
# ==============================================================

def match_best(text: str, patterns, default="Other"):
    """Return the BEST matching value from patterns (not just the first).
    
    Checks all patterns and returns the one with the highest quality score based on:
      1. Match span length (longer = more specific)
      2. Pattern regex length (longer patterns = more specific intent)
      3. Earlier position (slight preference for primary/common patterns in ties)
    
    Performance: O(n) where n = number of patterns (must check all to find best).
    With ~90 patterns and vectorized Series.apply(), overhead is negligible.
    This is only slightly slower than match_first since both iterate, but match_best
    keeps iterating even after first match to find the most specific one.
    
    Example:
      - Title: "Senior Data Scientist II"
      - Both "Data Scientist" and "Senior" patterns match
      - "Data Scientist" match is longer → wins
    """
    if not isinstance(text, str):
        return default
    
    best_score = -1
    best_val = default
    
    for idx, item in enumerate(patterns):
        pat, val = item[0], item[1]  # extract pattern and value (ignore extra fields)
        match = pat.search(text)
        if match:
            # Score formula prioritizes: specificity > pattern complexity > position
            match_length = match.end() - match.start()
            pattern_length = len(pat.pattern)
            # Multiply match_length by large factor so it dominates all other factors
            score = (match_length * 10000) + pattern_length - idx
            
            if score > best_score:
                best_score = score
                best_val = val
    
    return best_val


def _parse_location(loc: str) -> Tuple[str, str, str]:
    """Parse a single location string into (city, state, country).
    Handles: 'City, ST', 'City, State', 'City, ST, Country', 'Remote', etc.
    """
    if not isinstance(loc, str) or not loc.strip():
        return ("Unknown", "Unknown", "Unknown")

    loc_clean = loc.strip()

    # Check for remote first
    if re.match(r"(?i)^remote", loc_clean):
        return ("Remote", "Remote", "Remote")

    m = _GEO_RE.match(loc_clean)
    if not m:
        return (loc_clean.title(), "Unknown", "Unknown")

    city = m.group("city").strip().title()
    raw_state = m.group("state").strip()
    raw_country = (m.group("country") or "").strip()

    # Normalize state
    state_upper = raw_state.upper().strip(".")
    if state_upper in US_STATE_ABBREV:
        state = US_STATE_ABBREV[state_upper]
        country = "United States"
    elif raw_state.lower() in _STATE_FULL_TO_ABBREV:
        state = raw_state.title()
        country = "United States"
    else:
        state = raw_state.title()
        country = "Unknown"

    # Override country if explicitly provided
    if raw_country:
        norm = COUNTRY_ALIASES.get(raw_country.lower().strip("."), raw_country.title())
        country = norm

    # If state resolved to a US state but no country was given, default US
    # (already handled above)

    return (city, state, country)


# ==============================================================
# 2A — STANDARDISATION
# ==============================================================

def standardise_jobs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Title + family — match BEST (not first) to get most specific classification
    df["standardized_title"] = df["job_title"].apply(
        lambda t: match_best(t, COMPILED_TITLE_PATTERNS)
    )

    df["job_family"] = df["job_title"].apply(
        lambda t: match_best(t, [(p, f) for p, _, f in COMPILED_TITLE_PATTERNS])
    )

    # Combine relevant text columns once
    combined = (
        df["job_title"].fillna("") + " " +
        df["job_description"].fillna("") + " " +
        df.get("seniority_level", pd.Series("", index=df.index)).fillna("")
    )

    def infer_seniority(t):
        # Use match_best to get the most specific seniority level match
        # (e.g., prefer "senior" over just "engineer" if both are present)
        best_level = "Mid"
        best_score = -1
        
        for idx, (pat, lvl) in enumerate(SENIORITY_PATTERNS):
            match = pat.search(t.lower())
            if match:
                match_length = match.end() - match.start()
                pattern_length = len(pat.pattern)
                score = (match_length * 10000) + pattern_length - idx
                
                if score > best_score:
                    best_score = score
                    best_level = lvl

                    
        
        return best_level

    df["seniority_level_clean"] = combined.apply(infer_seniority)

    df["remote_type"] = combined.apply(
        lambda t: "Remote" if REMOTE_PATTERNS["Remote"].search(t)
        else "Hybrid" if REMOTE_PATTERNS["Hybrid"].search(t)
        else "Onsite"
    )

    return df


# ==============================================================
# 2B — SKILLS (VECTORIZED)
# ==============================================================

def build_skills(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    text = (
        df["job_description"].fillna("") + " " +
        df.get("requirements", pd.Series("", index=df.index)).fillna("")
    ).str.lower()

    flags = {}
    for s in ALL_KNOWN_SKILLS:
        if len(s) <= 3:
            flags[s] = text.str.contains(rf"\b{s}\b", regex=True)
        else:
            flags[s] = text.str.contains(s, regex=False)
    skill_df = pd.DataFrame(flags)

    # Vectorized: build list of matched skill names per row
    # Use matrix multiply trick: get column names where True
    skill_cols = skill_df.columns.tolist()
    skill_matrix = skill_df.values  # bool ndarray (n, k)
    df["skills_extracted"] = [
        [skill_cols[j] for j in np.where(row)[0]]
        for row in skill_matrix
    ]
    df["skill_count"] = skill_df.sum(axis=1)

    # Skill categories — vectorized via the same matrix
    df["skill_categories"] = [
        list({SKILL_TO_CATEGORY[skill_cols[j]] for j in np.where(row)[0]})
        for row in skill_matrix
    ]

    return df


# ==============================================================
# 2G — INDUSTRY DOMAINS
# ==============================================================

def build_domains(df: pd.DataFrame) -> pd.DataFrame:
    """Extract industry domains using precompiled domain patterns.
    
    Uses match_best() to identify the most specific industry domain.
    
    Adds:
      - industry_domain: primary industry domain match (e.g., "FinTech", "Healthcare")
    """
    df = df.copy()
    combined_text = (
        df["job_title"].fillna("") + " " +
        df["job_description"].fillna("")
    )
    
    # Use match_best to get most specific domain
    df["industry_domain"] = combined_text.apply(
        lambda t: match_best(t, COMPILED_DOMAIN_PATTERNS, default="Other")
    )
    
    return df


# ==============================================================
# 2C — COMPENSATION
# ==============================================================

def build_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cleaned = df["salary_range"].fillna("").str.replace(r"[,$€£]", "", regex=True)
    nums = cleaned.str.extractall(r"(\d+(?:\.\d+)?)")[0].unstack()
    df["salary_min"] = pd.to_numeric(nums.get(0), errors="coerce")
    df["salary_max"] = pd.to_numeric(nums.get(1, nums.get(0)), errors="coerce")
    df["salary_midpoint"] = df[["salary_min", "salary_max"]].mean(axis=1)

    # Salary band classification — fully vectorized
    midpoint = df["salary_midpoint"]
    df["salary_band"] = pd.cut(
        midpoint,
        bins=[0, 60_000, 100_000, 150_000, 200_000, np.inf],
        labels=["<60k", "60k-100k", "100k-150k", "150k-200k", "200k+"],
        right=True,
    )
    return df


# ==============================================================
# 2D — TEXT SIGNALS (FULL RESTORED: complexity + buzzwords)
# ==============================================================

def build_text_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    desc = df["job_description"].fillna("")

    # Basic counts — vectorized
    words = desc.str.split()
    df["description_word_count"] = words.str.len().fillna(0).astype(int)
    df["description_length"] = desc.str.len()

    # Sentence count — vectorized via regex count
    df["sentence_count"] = desc.str.count(r"[.!?]+\s")
    df["sentence_count"] = df["sentence_count"].replace(0, 1)  # avoid div/0

    # Avg words per sentence — vectorized
    df["avg_words_per_sentence"] = (
        df["description_word_count"] / df["sentence_count"]
    ).round(1)

    # Buzzword count — single compiled regex, vectorized .str.count()
    df["buzzword_count"] = desc.str.count(_BUZZWORD_RE)

    # Buzzword density — per 100 words
    df["buzzword_density"] = (
        df["buzzword_count"] / df["description_word_count"].replace(0, 1) * 100
    ).round(2)

    # Inclusive language count — vectorized
    df["inclusive_term_count"] = desc.str.count(_INCLUSIVE_RE)

    # Reading complexity tier — vectorized via pd.cut on avg_words_per_sentence
    df["reading_complexity"] = pd.cut(
        df["avg_words_per_sentence"],
        bins=[0, 12, 18, 25, np.inf],
        labels=["Simple", "Moderate", "Complex", "Very Complex"],
        right=True,
    )

    # Has requirements section flag — vectorized
    df["has_requirements_section"] = desc.str.contains(
        r"(?i)requirements?|qualifications?|what you.?ll need",
        regex=True,
    )

    # Has benefits section flag — vectorized
    df["has_benefits_section"] = desc.str.contains(
        r"(?i)benefits?|perks|what we offer|compensation",
        regex=True,
    )

    return df


# ==============================================================
# 2E — COMPANY FEATURES
# ==============================================================

def build_company_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Normalize company names for consistency
    df["company_name"] = df["company_name"].apply(normalize_company_name)
    
    agg = df.groupby("company_name").agg(
        company_job_count=("job_id", "count"),
        company_avg_salary=("salary_midpoint", "mean"),
    ).reset_index()
    return df.merge(agg, on="company_name", how="left"), agg


# ==============================================================
# 2F — GEO (FULL RESTORED: city / state / country normalization)
# ==============================================================

def build_geo(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Parse, normalize, and enrich geographic data.
    
    Adds:
      - geo_city, geo_state, geo_country (parsed & normalized)
      - is_us (boolean flag)
      - geo_metro (metro area alias normalization)
      - geo_city_normalized (aliased city names)
      - geo_city_inferred_country (country lookup from city)
      - geo_cluster (US regional cluster: West Coast, East Coast, etc.)
      - geo_region_keyword (regional keywords: EMEA, APAC, LATAM, etc.)
    """
    df = df.copy()
    loc_series = df["job_location"].fillna("")

    # Vectorized parse — apply on Series (not axis=1)
    parsed = loc_series.apply(_parse_location)
    df["geo_city"] = parsed.str[0]
    df["geo_state"] = parsed.str[1]
    df["geo_country"] = parsed.str[2]

    # US flag — vectorized
    df["is_us"] = df["geo_country"] == "United States"

    # City alias normalization (lowercase for case-insensitive lookup)
    city_lower = df["geo_city"].str.lower()
    df["geo_city_normalized"] = city_lower.map(CITY_ALIASES).fillna(df["geo_city"])
    
    # City-to-country enrichment (for non-US locations)
    df["geo_city_inferred_country"] = city_lower.map(CITY_TO_COUNTRY)

    # Metro area normalization (common aliases) — vectorized .replace()
    metro_map = {
        "New York": "New York City",
        "Nyc": "New York City",
        "Manhattan": "New York City",
        "Brooklyn": "New York City",
        "Sf": "San Francisco",
        "San Fran": "San Francisco",
        "La": "Los Angeles",
        "D.C.": "Washington",
        "Dc": "Washington",
        "Washington D.C.": "Washington",
    }
    df["geo_metro"] = df["geo_city"].replace(metro_map)

    # US regional cluster assignment
    def get_us_cluster(state: str) -> str:
        """Return the regional cluster for a US state, or 'Other' if not found."""
        if not isinstance(state, str):
            return "Other"
        for cluster, states in GEO_CLUSTERS_US.items():
            if state in states:
                return cluster
        return "Other"

    df["geo_cluster"] = df["geo_state"].apply(get_us_cluster)

    # Regional keyword matching for non-US or multi-region listings
    def extract_region(location_text: str) -> str:
        """Extract region keywords (EMEA, APAC, LATAM, etc.) from location."""
        if not isinstance(location_text, str) or not location_text.strip():
            return "Not Specified"
        
        for region, pattern in COMPILED_REGION_KEYWORDS.items():
            if pattern.search(location_text):
                return region
        return "Not Specified"

    df["geo_region_keyword"] = loc_series.apply(extract_region)

    # Geo summary table for gold_geo.parquet
    geo_summary = (
        df.groupby(["geo_country", "geo_state", "geo_metro"])
        .agg(
            job_count=("job_id", "count"),
            avg_salary=("salary_midpoint", "mean"),
        )
        .reset_index()
        .sort_values("job_count", ascending=False)
    )

    return df, geo_summary


# ==============================================================
# 2G — TIME FEATURES
# ==============================================================

def build_time_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df["posting_date_parsed"] = pd.to_datetime(df["posting_date"], errors="coerce")
    df["posting_month"] = df["posting_date_parsed"].dt.to_period("M").astype(str)
    df["posting_dow"] = df["posting_date_parsed"].dt.day_name()

    trend = df.groupby("posting_month").size().reset_index(name="job_count")
    return df, trend


# ==============================================================
# 3A — SIMILARITY (CHUNKED, SAFE)
# ==============================================================

def build_similarity(df: pd.DataFrame, threshold=0.85, chunk_size=500) -> pd.DataFrame:
    df = df.copy()
    texts = (
        df["job_title"].fillna("") + " " + df["job_description"].fillna("")
    ).tolist()

    tfidf = TfidfVectorizer(max_features=3000, stop_words="english")
    X = tfidf.fit_transform(texts)
    n = X.shape[0]

    max_sims = np.zeros(n, dtype=np.float32)
    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        sims = cosine_similarity(X[start:end], X)
        for i in range(end - start):
            sims[i, start + i] = 0  # zero out self-similarity
        max_sims[start:end] = sims.max(axis=1)

    df["max_similarity_score"] = np.round(max_sims, 4)
    df["is_likely_duplicate"] = df["max_similarity_score"] >= threshold
    return df


# ==============================================================
# 3B — DEMAND
# ==============================================================
def add_yearly_decay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["posting_date_parsed"] = pd.to_datetime(
        df["posting_date_parsed"],
        errors="coerce"
    )

    df["posting_year"] = df["posting_date_parsed"].dt.year

    yearly_ref = df.groupby("posting_year")["posting_date_parsed"].transform("max")

    df["days_since_post"] = (
        yearly_ref - df["posting_date_parsed"]
    ).dt.days.fillna(365)

    df["recency_weight"] = np.exp(-0.0077 * df["days_since_post"])

    return df
def build_demand_by_year(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = add_yearly_decay(df)

    demand = (
        df.groupby(["posting_year", "standardized_title"])
        .agg(
            demand_score=("recency_weight", "sum"),
            raw_count=("standardized_title", "size")
        )
        .reset_index()
    )

    yearly_total = demand.groupby("posting_year")["demand_score"].transform("sum")

    demand["demand_pct"] = np.where(
        yearly_total > 0,
        (demand["demand_score"] / yearly_total) * 100,
        0
    )

    return df.merge(
        demand,
        on=["posting_year", "standardized_title"],
        how="left"
    )
# ==============================================================
# 3C — SKILL–SALARY
# ==============================================================

def build_skill_salary(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df[["skills_extracted", "salary_midpoint"]].dropna(subset=["salary_midpoint"])
    tmp = tmp.explode("skills_extracted").dropna(subset=["skills_extracted"])
    agg = tmp.groupby("skills_extracted").agg(
        avg_salary=("salary_midpoint", "mean"),
        median_salary=("salary_midpoint", "median"),
        job_count=("salary_midpoint", "count"),
    ).reset_index()
    agg["skill_category"] = agg["skills_extracted"].map(SKILL_TO_CATEGORY)
    return agg


# ==============================================================
# 3D — CAREER PATHS
# ==============================================================

def build_career_paths(df: pd.DataFrame) -> pd.DataFrame:
    """Career pathing when each seniority level has ONE title per job family."""
    order = {"Junior": 0, "Mid": 1, "Senior": 2, "Leadership": 3}

    sub = (
        df[["job_family", "standardized_title", "seniority_level_clean"]]
        .drop_duplicates()
    )
    sub["rank"] = sub["seniority_level_clean"].map(order)

    # Drop duplicates at the (job_family, rank) level — keep first or flag them
    dupes = sub.groupby(["job_family", "rank"]).size().reset_index(name="count")
    if (dupes["count"] > 1).any():
        print("⚠️ Warning: Multiple titles at the same seniority level detected.")
        print(dupes[dupes["count"] > 1])

    sub = sub.sort_values(["job_family", "rank"])

    # Shift only across DIFFERENT ranks
    sub["to_title"] = sub.groupby("job_family")["standardized_title"].shift(-1)
    sub["to_rank"] = sub.groupby("job_family")["rank"].shift(-1)

    # Keep only rows where the next title is actually a HIGHER rank
    result = sub[sub["to_rank"] > sub["rank"]].copy()

    return result[["job_family", "standardized_title", "seniority_level_clean", "to_title"]].drop_duplicates()



# ==============================================================
# 3E — QUALITY (FULL RESTORED)
# ==============================================================

def build_quality(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Scoring components — all vectorized
    has_salary = df["salary_midpoint"].notna().astype(int) * 20
    desc_score = df["description_word_count"].clip(0, 500) / 500 * 20
    has_reqs = df["has_requirements_section"].astype(int) * 15
    has_benefits = df["has_benefits_section"].astype(int) * 10
    low_buzzword = (df["buzzword_density"] < 5).astype(int) * 10
    has_skills = (df["skill_count"] >= 3).astype(int) * 15
    inclusive = (df["inclusive_term_count"] >= 1).astype(int) * 10

    df["quality_score"] = (
        has_salary + desc_score + has_reqs + has_benefits
        + low_buzzword + has_skills + inclusive
    ).round(1)

    # Tier classification — vectorized
    df["quality_tier"] = pd.cut(
        df["quality_score"],
        bins=[0, 30, 55, 75, 100],
        labels=["Low", "Fair", "Good", "Excellent"],
        right=True,
    )

    return df


# ==============================================================
# PIPELINE — MULTI-PARQUET GOLD (mirrors silver structure)
# ==============================================================

GOLD_OUTPUTS = {
    "gold_jobs":          "Core enriched job listings",
    "gold_company":       "Company-level aggregations",
    "gold_geo":           "Geography summary (city/state/country)",
    "gold_posting_trend": "Monthly posting volume trend",
    "gold_skill_salary":  "Skill ↔ salary cross-reference",
    "gold_career_paths":  "Inferred career progression edges",
    "gold_similarity":    "Duplicate detection metadata",
}


def _write_parquet(df: pd.DataFrame, outdir: str, name: str) -> str:
    path = os.path.join(outdir, f"{name}.parquet")
    df.to_parquet(path, index=False)
    rows = len(df)
    size_kb = os.path.getsize(path) / 1024
    print(f"   {name}.parquet  →  {rows:,} rows  ({size_kb:,.1f} KB)")
    return path


def run_pipeline(input_path: str, outdir: str) -> Dict[str, pd.DataFrame]:
    """Execute the full gold-layer pipeline.

    Mirrors the silver pipeline pattern:
      1. Read silver parquet
      2. Run enrichment steps sequentially
      3. Split into purpose-specific gold tables
      4. Write each as its own parquet file

    Returns a dict of {table_name: DataFrame} for downstream use.
    """
    os.makedirs(outdir, exist_ok=True)
    print(f"{'='*60}")
    print("GOLD PIPELINE — START")
    print(f"{'='*60}")
    t0 = time.time()

    # ── LOAD ─────────────────────────────────────────────────
    print(f"\nReading: {input_path}")
    df = pd.read_parquet(input_path)
    print(f"   Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # Normalize website names (job_source) for consistent capitalization
    if "job_source" in df.columns:
        df["job_source"] = df["job_source"].apply(normalize_company_name)

    # ── LAYER 2: ENRICHMENT ──────────────────────────────────
    print("\n── Layer 2: Enrichment ──")

    print("  2A  Standardisation …")
    df = standardise_jobs(df)

    print("  2B  Skills extraction …")
    df = build_skills(df)

    print("  2C  Compensation parsing …")
    df = build_compensation(df)

    print("  2D  Text signals (complexity + buzzwords) …")
    df = build_text_signals(df)

    print("  2E  Company features …")
    df, company_df = build_company_features(df)

    print("  2F  Geo normalization (city/state/country) …")
    df, geo_df = build_geo(df)

    print("  2G  Industry domains …")
    df = build_domains(df)

    print("  2H  Time features …")
    df, posting_trend_df = build_time_features(df)

    # ── LAYER 3: ANALYTICS ───────────────────────────────────
    print("\n── Layer 3: Analytics ──")

    print("  3A  Similarity (chunked cosine) …")
    df = build_similarity(df)

    print("  3B  Demand scoring …")
    df = build_demand_by_year(df)

    print("  3C  Skill–salary cross-reference …")
    skill_salary_df = build_skill_salary(df)

    print("  3D  Career paths …")
    career_df = build_career_paths(df)

    print("  3E  Quality scoring …")
    df = build_quality(df)

    # ── SPLIT INTO GOLD TABLES ───────────────────────────────
    print(f"\n── Writing gold tables to: {outdir} ──")

    # Similarity slice — keep only flagged rows + metadata
    sim_cols = [
        "job_id", "max_similarity_score",
        "is_likely_duplicate",
    ]
    sim_df = df[sim_cols].copy()

    outputs: Dict[str, pd.DataFrame] = {}

    # Domain summary — aggregated by industry
    domain_summary = df.groupby("industry_domain").agg(
        job_count=("job_id", "count"),
        avg_salary=("salary_midpoint", "mean"),
        avg_quality_score=("quality_score", "mean"),
    ).reset_index().sort_values("job_count", ascending=False)

    outputs["gold_jobs"] = df
    outputs["gold_company"] = company_df
    outputs["gold_geo"] = geo_df
    outputs["gold_posting_trend"] = posting_trend_df
    outputs["gold_skill_salary"] = skill_salary_df
    outputs["gold_career_paths"] = career_df
    outputs["gold_similarity"] = sim_df
    outputs["gold_domain_summary"] = domain_summary

    for name, frame in outputs.items():
        _write_parquet(frame, outdir, name)

    # ── DONE ─────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"GOLD PIPELINE — DONE in {elapsed:.1f}s")
    print(f"  {len(outputs)} gold tables written")
    print(f"{'='*60}")

    return outputs

# ==============================================================
# ENTRYPOINT
# ==============================================================

def main():
    run_pipeline(
        input_path=r"C:\Users\Gabriel\Desktop\LetsDoThisOneMoreTime\Data Pipelines\ReallyBigJobData_Pipeline\gold_layer_extracted\all_combined_job_desc.parquet",
        outdir=r"C:\Users\Gabriel\Desktop\LetsDoThisOneMoreTime\Data Pipelines\ReallyBigJobData_Pipeline\gold_layer_extracted",
    )

if __name__ == "__main__":
    main()