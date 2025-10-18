"""
Crisis Fact-Checking Agentic System - JSON Output
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools import tool

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai")
    OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-4o")
    ANTHROPIC_MODEL_ID = os.getenv("ANTHROPIC_MODEL_ID", "claude-sonnet-4-5")

    @classmethod
    def get_model(cls):
        if cls.DEFAULT_MODEL == "anthropic" and cls.ANTHROPIC_KEY:
            return Claude(id=cls.ANTHROPIC_MODEL_ID)
        elif cls.OPENAI_KEY:
            return OpenAIChat(id=cls.OPENAI_MODEL_ID)
        else:
            raise ValueError("No API key configured")

# ============================================================================
# CUSTOM TOOLS
# ============================================================================

class FactCheckTools:
    @staticmethod
    @tool
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        emotional_words = {
            "positive": ["amazing", "great", "excellent", "wonderful", "fantastic", "cure", "miracle"],
            "negative": ["terrible", "awful", "disaster", "dangerous", "deadly", "crisis", "emergency"],
            "fear": ["scary", "terrifying", "alarming", "shocking", "disturbing"]
        }

        text_lower = text.lower()
        scores = {category: sum(1 for word in words if word in text_lower)
                  for category, words in emotional_words.items()}

        total_emotional = sum(scores.values())
        sentiment_score = (scores["positive"] - scores["negative"]) / max(total_emotional, 1)

        return {
            "sentiment_score": sentiment_score,
            "emotion_breakdown": scores,
            "emotional_intensity": total_emotional / max(len(text.split()), 1)
        }

    @staticmethod
    @tool
    def check_source_credibility(url: str) -> Dict[str, Any]:
        credible_domains = [
            "reuters.com", "apnews.com", "bbc.com", "npr.org",
            "who.int", "cdc.gov", "gov.uk", "nature.com",
            "science.org", "nejm.org", "thelancet.com"
        ]

        questionable_domains = [
            "beforeitsnews.com", "naturalnews.com", "infowars.com"
        ]

        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")

        if any(credible in domain for credible in credible_domains):
            credibility_score = 0.9
            risk_level = "low"
        elif any(questionable in domain for questionable in questionable_domains):
            credibility_score = 0.2
            risk_level = "high"
        else:
            credibility_score = 0.5
            risk_level = "medium"

        return {
            "domain": domain,
            "credibility_score": credibility_score,
            "risk_level": risk_level
        }

# ============================================================================
# RESULT PARSER
# ============================================================================

class ResultParser:
    """Parse agent output into structured JSON"""
    
    @staticmethod
    def parse_agent_output(content: str, claim_text: str, source_url: str) -> Dict[str, Any]:
        """Extract structured data from agent response"""
        
        # Ensure content is string
        if not isinstance(content, str):
            content = str(content)
        
        content_lower = content.lower()
        
        # Extract verdict
        verdict = "UNVERIFIED"
        if re.search(r'verdict[:\s]+(true|✅)', content_lower):
            verdict = "TRUE"
        elif re.search(r'verdict[:\s]+(false|❌)', content_lower):
            verdict = "FALSE"
        elif re.search(r'verdict[:\s]+(disputed|⚠️)', content_lower):
            verdict = "DISPUTED"
        
        # Extract confidence
        confidence = "MEDIUM"
        if re.search(r'confidence[:\s]+(high|strong)', content_lower):
            confidence = "HIGH"
        elif re.search(r'confidence[:\s]+(low|weak)', content_lower):
            confidence = "LOW"
        
        # Extract sections
        sections = {
            'reasoning': ResultParser._extract_section(content, ['reasoning', 'analysis', 'decision logic']),
            'evidence': ResultParser._extract_section(content, ['evidence', 'sources', 'supporting']),
            'public_summary': ResultParser._extract_section(content, ['public summary', 'summary', 'conclusion'])
        }
        
        # Calculate credibility score (simple heuristic)
        credibility_score = 0.5
        if verdict == "TRUE":
            credibility_score = 0.8 if confidence == "HIGH" else 0.6
        elif verdict == "FALSE":
            credibility_score = 0.2 if confidence == "HIGH" else 0.3
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "claim_text": claim_text,
            "source_url": source_url or "No source provided",
            "credibility_score": credibility_score,
            "reasoning_chain": sections['reasoning'] or content[:500],
            "evidence_summary": sections['evidence'] or "See detailed analysis",
            "public_summary": sections['public_summary'] or content[:300],
            "full_analysis": content,
            "sources_checked": ResultParser._count_sources(content),
            "key_findings": ResultParser._extract_key_findings(content)
        }
    
    @staticmethod
    def _extract_section(content: str, keywords: list) -> str:
        """Extract section by keywords"""
        if not isinstance(content, str):
            content = str(content)
        
        content_lower = content.lower()
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]+(.*?)(?:\n\n|\n[0-9]\.|$)'
            match = re.search(pattern, content_lower, re.DOTALL)
            if match:
                # Get the original case text from content
                start_pos = match.start(1)
                end_pos = match.end(1)
                original_text = content[start_pos:end_pos].strip()
                return original_text[:800]
        return ""
    
    @staticmethod
    def _count_sources(content: str) -> int:
        """Count mentioned sources"""
        urls = re.findall(r'https?://\S+', content)
        return len(set(urls))
    
    @staticmethod
    def _extract_key_findings(content: str) -> list:
        """Extract bullet points or key findings"""
        findings = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('- ', '• ', '* ', '1.', '2.', '3.')):
                finding = line.strip().lstrip('-•*123456789. ')
                if finding and len(finding) > 10:
                    findings.append(finding[:200])
                if len(findings) >= 5:
                    break
        return findings

# ============================================================================
# AGENT MANAGER
# ============================================================================

class AgentManager:
    def __init__(self):
        self.model = Config.get_model()
        self.tools = FactCheckTools()
        self._create_agents()
        self._create_team()

    def _create_agents(self):
        self.reasoning_agent = Agent(
            name="Reasoning & Synthesis Agent",
            role="Lead fact-checker and verdict generator",
            tools=[DuckDuckGoTools(), self.tools.analyze_sentiment, self.tools.check_source_credibility],
            instructions=[
                "You are the lead fact-checker. Analyze the claim thoroughly.",
                "Search multiple sources and cross-reference information.",
                "Generate output in this EXACT format:",
                "",
                "VERDICT: [TRUE/FALSE/DISPUTED/UNVERIFIED]",
                "CONFIDENCE: [HIGH/MEDIUM/LOW]",
                "",
                "REASONING:",
                "[Explain your decision logic step by step]",
                "",
                "EVIDENCE:",
                "[List key supporting or refuting evidence with sources]",
                "",
                "PUBLIC SUMMARY:",
                "[Clear, accessible explanation for general audience]",
                "",
                "Be thorough but concise. Use web search to verify claims."
            ],
            model=self.model,
            markdown=True
        )

    def _create_team(self):
        self.fact_check_team = Team(
            name="Fact-Checking Team",
            members=[self.reasoning_agent],
            instructions=[
                "Comprehensively fact-check the claim",
                "Follow the structured output format",
                "Be clear and evidence-based"
            ],
            model=self.model,
            markdown=True
        )

# ============================================================================
# CLAIM PROCESSOR
# ============================================================================

class ClaimProcessor:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.parser = ResultParser()

    def process_claim(self, claim_text: str, source_url: str = None) -> Dict[str, Any]:
        """Process claim and return structured JSON"""
        try:
            result = self.agent_manager.fact_check_team.run(
                input=f"""
                Fact-check this claim:

                Claim: {claim_text}
                Source: {source_url or 'User submission'}

                Provide comprehensive fact-check following the structured format.
                Use web search to verify information.
                """
            )

            # Extract content as string
            if isinstance(result.content, str):
                content = result.content
            elif isinstance(result.content, dict):
                # If it's a dict, try to get a text field or convert to JSON string
                content = result.content.get('text', '') or result.content.get('content', '') or str(result.content)
            else:
                content = str(result.content)
            
            print(f"DEBUG: Content type: {type(result.content)}")
            print(f"DEBUG: Content preview: {content[:200]}...")
            
            # Parse response into structured JSON
            parsed_result = self.parser.parse_agent_output(
                content=content,
                claim_text=claim_text,
                source_url=source_url
            )
            
            return parsed_result

        except Exception as e:
            return {
                "verdict": "ERROR",
                "confidence": "N/A",
                "claim_text": claim_text,
                "source_url": source_url or "No source",
                "credibility_score": 0,
                "reasoning_chain": f"Error occurred: {str(e)}",
                "evidence_summary": "Unable to complete analysis",
                "public_summary": "An error occurred during fact-checking",
                "full_analysis": str(e),
                "sources_checked": 0,
                "key_findings": []
            }

# ============================================================================
# MAIN SYSTEM
# ============================================================================

class FactCheckSystem:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.claim_processor = ClaimProcessor(self.agent_manager)

    def check_claim(self, claim_text: str, source_url: str = None) -> Dict[str, Any]:
        """Check claim and return JSON result"""
        return self.claim_processor.process_claim(claim_text, source_url)
    


# async def main():
#     fact = FactCheckSystem()
#     result = await fact.check_claim("The COVID-19 vaccine contains microchips for tracking.")
#     print('dahfdsk',result)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())