from pydantic import BaseModel, Field

# ── Market Research Engine ──

class MarketResearchInput(BaseModel):
    idea: str = Field(..., description="The product concept or workspace scope")
    additional_context: str = Field(default="", description="Optional additional context or parameters")

class MarketResearchOutput(BaseModel):
    market_size_tam: str = Field(..., description="Total Addressable Market size estimate (e.g. $10B by 2030)")
    market_size_sam: str = Field(..., description="Serviceable Addressable Market size estimate")
    market_size_som: str = Field(..., description="Serviceable Obtainable Market size estimate")
    market_growth_rate: str = Field(..., description="CAGR or annual growth percentage details")
    key_segments: list[str] = Field(default_factory=list, description="Primary customer segments identified")
    pestle_political: str = Field(..., description="Political factors impacting the product")
    pestle_economic: str = Field(..., description="Economic factors impacting the product")
    pestle_social: str = Field(..., description="Social / demographic trends impacting the product")
    pestle_technological: str = Field(..., description="Technological drivers or shifts")
    pestle_legal: str = Field(..., description="Regulatory or legal hurdles/compliance details")
    pestle_environmental: str = Field(..., description="Environmental or sustainability considerations")

MARKET_RESEARCH_PROMPT = (
    "You are the Market Research Engine of AI ProductOS.\n"
    "Perform a complete market sizing (TAM/SAM/SOM), customer segmentation, and PESTLE analysis for the product idea.\n"
    "Return a JSON object matching the MarketResearchOutput schema with all required fields.\n"
    "Be realistic, detailed, and quantitative. Never use generic placeholders."
)

# ── Competitor Analysis Engine ──

class CompetitorItem(BaseModel):
    name: str = Field(..., description="Name of the competitor")
    market_share: str = Field(..., description="Estimated market share or category placement")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    differentiation_factor: str = Field(..., description="How our product differentiates from them")

class CompetitorAnalysisInput(BaseModel):
    idea: str = Field(..., description="The product concept or workspace scope")
    competitors_list: list[str] = Field(default_factory=list, description="Optional user-provided competitor list")

class CompetitorAnalysisOutput(BaseModel):
    competitors: list[CompetitorItem] = Field(default_factory=list)
    swot_strengths: list[str] = Field(default_factory=list, description="Our product's internal strengths")
    swot_weaknesses: list[str] = Field(default_factory=list, description="Our product's internal weaknesses")
    swot_opportunities: list[str] = Field(default_factory=list, description="External market opportunities")
    swot_threats: list[str] = Field(default_factory=list, description="External market threats")
    porter_threat_of_new_entrants: str = Field(..., description="Porter's Five Forces: Threat of New Entrants assessment")
    porter_bargaining_power_of_buyers: str = Field(..., description="Porter's Five Forces: Bargaining Power of Buyers")
    porter_bargaining_power_of_suppliers: str = Field(..., description="Porter's Five Forces: Bargaining Power of Suppliers")
    porter_threat_of_substitutes: str = Field(..., description="Porter's Five Forces: Threat of Substitutes")
    porter_competitive_rivalry: str = Field(..., description="Porter's Five Forces: Competitive Rivalry in Industry")

COMPETITOR_ANALYSIS_PROMPT = (
    "You are the Competitor Analysis Engine of AI ProductOS.\n"
    "Generate a competitive grid, SWOT matrix, and Porter's Five Forces analysis for the given product concept.\n"
    "Return a JSON object matching the CompetitorAnalysisOutput schema with all required fields.\n"
    "Be highly analytical, structural, and detailed. Do not use blank values."
)
