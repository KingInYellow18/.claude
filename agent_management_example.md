# Create a comprehensive example of agent management system implementation
agent_management_example = """
# Example: Hierarchical Agent Selection System for Claude Code

## 1. Agent Metadata Structure (.claude/agents/agent-name.md)

```yaml
---
name: "api-developer"
category: "development"
subcategory: "backend"
description: "Specialized in REST API development, database integration, and backend architecture"
skills: ["api", "database", "backend", "rest", "microservices", "authentication"]
tools: ["Read", "Edit", "Bash", "Database"]
complexity_level: "intermediate"
usage_frequency: 0.85
success_rate: 0.92
last_used: "2025-01-15T10:30:00Z"
context_requirements: ["project_structure", "api_docs", "database_schema"]
---

You are an expert API developer specialized in creating robust backend services...
```

## 2. Agent Selection Router Implementation

```python
import json
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import yaml
from pathlib import Path

class AgentRouter:
    def __init__(self, agents_dir: str = ".claude/agents"):
        self.agents_dir = Path(agents_dir)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.agents_metadata = {}
        self.agent_embeddings = {}
        self.category_tree = self._build_category_tree()
        
    def _load_agents(self):
        \"\"\"Load all agent metadata and create embeddings\"\"\"
        for agent_file in self.agents_dir.glob("*.md"):
            with open(agent_file, 'r') as f:
                content = f.read()
                
            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                metadata = yaml.safe_load(parts[1])
                
                # Create searchable text for embedding
                searchable_text = f"{metadata['description']} {' '.join(metadata.get('skills', []))}"
                embedding = self.embedding_model.encode(searchable_text)
                
                self.agents_metadata[metadata['name']] = metadata
                self.agent_embeddings[metadata['name']] = embedding
    
    def _build_category_tree(self) -> Dict:
        \"\"\"Build hierarchical category structure\"\"\"
        return {
            'development': {
                'frontend': ['react', 'vue', 'angular', 'ui', 'css'],
                'backend': ['api', 'database', 'server', 'microservices'],
                'mobile': ['ios', 'android', 'react-native', 'flutter'],
                'fullstack': ['full-stack', 'end-to-end', 'complete']
            },
            'testing': {
                'unit': ['jest', 'pytest', 'junit', 'unit-test'],
                'integration': ['e2e', 'integration', 'api-testing'],
                'performance': ['load', 'stress', 'benchmark']
            },
            'devops': {
                'deployment': ['docker', 'kubernetes', 'ci-cd', 'deploy'],
                'monitoring': ['logging', 'metrics', 'observability'],
                'infrastructure': ['terraform', 'aws', 'cloud']
            },
            'documentation': {
                'technical': ['api-docs', 'readme', 'technical-writing'],
                'user': ['user-guide', 'tutorial', 'examples']
            }
        }
    
    def select_agent(self, query: str, context: Dict = None) -> List[Dict]:
        \"\"\"
        Multi-stage agent selection process
        Stage 1: Category filtering (240 → ~20-30)
        Stage 2: Semantic similarity (30 → ~5)
        Stage 3: Context scoring (5 → 1-3)
        \"\"\"
        
        # Stage 1: Category-based filtering
        category_candidates = self._filter_by_category(query)
        
        # Stage 2: Semantic similarity ranking
        semantic_candidates = self._rank_by_similarity(query, category_candidates)
        
        # Stage 3: Context-aware final selection
        final_candidates = self._context_aware_selection(semantic_candidates, context)
        
        return final_candidates
    
    def _filter_by_category(self, query: str) -> List[str]:
        \"\"\"Stage 1: Reduce agent pool using category matching\"\"\"
        query_lower = query.lower()
        matching_agents = []
        
        for agent_name, metadata in self.agents_metadata.items():
            # Check primary category match
            category_match = any(
                keyword in query_lower 
                for category_keywords in self.category_tree.get(metadata['category'], {}).values()
                for keyword in category_keywords
            )
            
            # Check skill keywords
            skill_match = any(skill in query_lower for skill in metadata.get('skills', []))
            
            if category_match or skill_match:
                matching_agents.append(agent_name)
        
        return matching_agents
    
    def _rank_by_similarity(self, query: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        \"\"\"Stage 2: Semantic similarity ranking\"\"\"
        query_embedding = self.embedding_model.encode(query)
        
        similarities = []
        for agent_name in candidates:
            agent_embedding = self.agent_embeddings[agent_name]
            similarity = np.dot(query_embedding, agent_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(agent_embedding)
            )
            similarities.append((agent_name, similarity))
        
        # Sort by similarity and return top K
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _context_aware_selection(self, candidates: List[Tuple[str, float]], context: Dict = None) -> List[Dict]:
        \"\"\"Stage 3: Context-aware final scoring\"\"\"
        scored_candidates = []
        
        for agent_name, semantic_score in candidates:
            metadata = self.agents_metadata[agent_name]
            
            # Base score from semantic similarity
            total_score = semantic_score
            
            if context:
                # Recent usage boost (recency bias)
                if context.get('recent_agents') and agent_name in context['recent_agents']:
                    total_score *= 1.1
                
                # Success rate weighting
                total_score *= metadata.get('success_rate', 0.8)
                
                # Project context matching
                if context.get('project_type'):
                    if context['project_type'] in metadata.get('skills', []):
                        total_score *= 1.2
                
                # Complexity matching
                user_complexity = context.get('complexity_level', 'intermediate')
                agent_complexity = metadata.get('complexity_level', 'intermediate')
                if user_complexity == agent_complexity:
                    total_score *= 1.1
            
            scored_candidates.append({
                'name': agent_name,
                'score': total_score,
                'metadata': metadata,
                'selection_reason': self._generate_selection_reason(agent_name, semantic_score, context)
            })
        
        # Sort by final score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def _generate_selection_reason(self, agent_name: str, semantic_score: float, context: Dict) -> str:
        \"\"\"Generate explanation for agent selection\"\"\"
        metadata = self.agents_metadata[agent_name]
        reasons = [f"High semantic match ({semantic_score:.2f})"]
        
        if context and context.get('project_type') in metadata.get('skills', []):
            reasons.append(f"Project type alignment ({context['project_type']})")
        
        if metadata.get('success_rate', 0) > 0.9:
            reasons.append(f"High success rate ({metadata.get('success_rate', 0):.1%})")
            
        return "; ".join(reasons)

## 3. Context-Aware Agent Loader

class ContextOptimizedLoader:
    def __init__(self):
        self.agent_cache = {}
        self.context_window_limit = 100000  # tokens
        
    def load_agent_with_context_optimization(self, agent_name: str, query_context: str) -> str:
        \"\"\"Load agent with minimal context footprint\"\"\"
        
        # Check cache first
        cache_key = f"{agent_name}_{hash(query_context)}"
        if cache_key in self.agent_cache:
            return self.agent_cache[cache_key]
        
        # Load agent file
        agent_content = self._load_agent_file(agent_name)
        
        # Apply context-aware optimizations
        optimized_content = self._optimize_for_context(agent_content, query_context)
        
        # Cache optimized version
        self.agent_cache[cache_key] = optimized_content
        
        return optimized_content
    
    def _optimize_for_context(self, content: str, query_context: str) -> str:
        \"\"\"Apply context optimization strategies\"\"\"
        
        # Strategy 1: Remove irrelevant examples
        content = self._filter_examples_by_relevance(content, query_context)
        
        # Strategy 2: Compress verbose instructions
        content = self._compress_instructions(content)
        
        # Strategy 3: Remove duplicate information
        content = self._deduplicate_content(content)
        
        return content

## 4. Usage Example

def main():
    # Initialize the router
    router = AgentRouter()
    router._load_agents()
    
    # Example query
    query = "I need help building a REST API with user authentication and database integration"
    
    # Context from current session
    context = {
        'project_type': 'api',
        'complexity_level': 'intermediate',
        'recent_agents': ['frontend-developer'],
        'current_files': ['app.py', 'models.py', 'auth.py']
    }
    
    # Get agent recommendations
    recommended_agents = router.select_agent(query, context)
    
    # Display results
    print("Agent Selection Results:")
    for i, agent in enumerate(recommended_agents[:3], 1):
        print(f"{i}. {agent['name']} (Score: {agent['score']:.3f})")
        print(f"   Reason: {agent['selection_reason']}")
        print()

if __name__ == "__main__":
    main()
```

## 5. Implementation Strategies Summary

### A. Hierarchical Filtering (240 → 20-30 agents)
- Category-based pre-filtering using metadata
- Keyword matching against skills and descriptions
- Reduces context window usage by 85-90%

### B. Semantic Similarity Ranking (30 → 5 agents)
- Vector embeddings of agent descriptions
- Query-to-agent semantic matching
- Cosine similarity scoring

### C. Context-Aware Selection (5 → 1-3 agents)
- Recent usage patterns
- Success rate weighting
- Project context alignment
- User complexity matching

### D. Context Optimization Techniques
- Lazy loading of agent content
- Cache frequently accessed agents
- Remove irrelevant examples/content
- Compress verbose instructions
- KV-cache optimization
"""

print(agent_management_example)

# Save to file for easy access
with open("agent_management_system.md", "w") as f:
    f.write(agent_management_example)

print("\n✅ Comprehensive agent management example created and saved to agent_management_system.md")