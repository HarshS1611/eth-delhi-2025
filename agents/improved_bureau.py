#!/usr/bin/env python3
"""
Improved Multi-Agent Bureau Setup - ETH Delhi 2025
Following Innovation Labs documentation for proper agent-to-agent communication
"""

from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

# Import our agents
from orchestrator_agent import OrchestratorAgent
from enhanced_validation_agent import DatasetValidationAgent
from legal_compliance_agent import LegalComplianceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_comprehensive_bureau():
    """Create a bureau with all agents following Innovation Labs pattern"""
    bureau = Bureau(name="eth_delhi_2025_validation_bureau", port=8003)
    
    # Create all agents with different ports
    orchestrator = OrchestratorAgent(name="orchestrator", port=8002)
    validator = DatasetValidationAgent(name="dataset_validator", port=8000)
    legal_agent = LegalComplianceAgent(name="legal_compliance", port=8001)
    
    # Add all agents to bureau for coordination
    bureau.add(orchestrator.agent)
    bureau.add(validator.agent)
    bureau.add(legal_agent.agent)
    
    logger.info("🏢 Bureau created with all agents:")
    logger.info(f"   📡 Orchestrator: {orchestrator.agent.address}")
    logger.info(f"   🔍 Validator: {validator.agent.address}")
    logger.info(f"   ⚖️ Legal Agent: {legal_agent.agent.address}")
    
    return bureau, orchestrator, validator, legal_agent

def create_agent_discovery_bureau():
    """Create bureau with proper agent discovery following documentation"""
    bureau = Bureau(name="discovery_bureau", port=8004)
    
    # Agent 1: Orchestrator (sends requests)
    orchestrator = Agent(
        name="orchestrator_discoverer",
        port=8005,
        seed="orchestrator_discovery_seed",
        endpoint=["http://localhost:8005/submit"]
    )
    
    # Agent 2: Validator (receives and responds)
    validator = Agent(
        name="validator_responder", 
        port=8006,
        seed="validator_response_seed",
        endpoint=["http://localhost:8006/submit"]
    )
    
    # Message models
    class ValidationRequest(Model):
        request_id: str
        dataset_path: str
        requester_address: str
    
    class ValidationResponse(Model):
        request_id: str
        success: bool
        score: float
        message: str
    
    # Fund agents
    fund_agent_if_low(orchestrator.wallet.address())
    fund_agent_if_low(validator.wallet.address())
    
    # Orchestrator startup - sends message to validator
    @orchestrator.on_event("startup")
    async def orchestrator_startup(ctx: Context):
        ctx.logger.info(f"🚀 Orchestrator started: {ctx.address}")
        
        # Send validation request to validator
        request = ValidationRequest(
            request_id="demo_request_001",
            dataset_path="/path/to/dataset.csv",
            requester_address=ctx.address
        )
        
        ctx.logger.info(f"📤 Sending validation request to validator...")
        await ctx.send(validator.address, request)
    
    # Validator message handler - receives and responds
    @validator.on_message(model=ValidationRequest)
    async def handle_validation_request(ctx: Context, sender: str, msg: ValidationRequest):
        ctx.logger.info(f"📥 Validator received request from {sender}")
        ctx.logger.info(f"   Request ID: {msg.request_id}")
        ctx.logger.info(f"   Dataset: {msg.dataset_path}")
        
        # Simulate validation processing
        await asyncio.sleep(1)
        
        # Send response back
        response = ValidationResponse(
            request_id=msg.request_id,
            success=True,
            score=85.7,
            message="Dataset validation completed successfully"
        )
        
        ctx.logger.info(f"📤 Sending validation response back to {sender}")
        await ctx.send(sender, response)
    
    # Orchestrator response handler
    @orchestrator.on_message(model=ValidationResponse)
    async def handle_validation_response(ctx: Context, sender: str, msg: ValidationResponse):
        ctx.logger.info(f"📥 Orchestrator received response from {sender}")
        ctx.logger.info(f"   Request ID: {msg.request_id}")
        ctx.logger.info(f"   Success: {msg.success}")
        ctx.logger.info(f"   Score: {msg.score}")
        ctx.logger.info(f"   Message: {msg.message}")
    
    # Add agents to bureau
    bureau.add(orchestrator)
    bureau.add(validator)
    
    return bureau

def create_sync_communication_demo():
    """Demo of ctx.send_and_receive (synchronous communication)"""
    bureau = Bureau(name="sync_comm_bureau", port=8007)
    
    # Create agents
    alice = Agent(name="alice", port=8008, seed="alice_sync_seed")
    bob = Agent(name="bob", port=8009, seed="bob_sync_seed")
    
    class Question(Model):
        text: str
        
    class Answer(Model):
        text: str
        
    # Fund agents
    fund_agent_if_low(alice.wallet.address())
    fund_agent_if_low(bob.wallet.address())
    
    # Alice asks Bob a question and waits for response
    @alice.on_interval(period=10.0)
    async def ask_question(ctx: Context):
        question = Question(text="How is the dataset validation going?")
        
        ctx.logger.info(f"🤔 Alice asking Bob: {question.text}")
        
        # Synchronous communication - wait for response
        reply, status = await ctx.send_and_receive(
            bob.address, 
            question, 
            response_type=Answer
        )
        
        if isinstance(reply, Answer):
            ctx.logger.info(f"✅ Alice received answer: {reply.text}")
        else:
            ctx.logger.info(f"❌ Alice failed to get answer: {status}")
    
    # Bob answers Alice's questions
    @bob.on_message(model=Question)
    async def answer_question(ctx: Context, sender: str, msg: Question):
        ctx.logger.info(f"📝 Bob received question: {msg.text}")
        
        # Process and respond
        answer = Answer(text="Validation is going great! 85% accuracy achieved.")
        await ctx.send(sender, answer)
        ctx.logger.info(f"📤 Bob sent answer back to Alice")
    
    bureau.add(alice)
    bureau.add(bob)
    
    return bureau

# Following Innovation Labs pattern - bureau.run() at module level
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "full":
            print("🏢 Starting Full Validation Bureau...")
            bureau, orchestrator, validator, legal_agent = create_comprehensive_bureau()
            bureau.run()
            
        elif mode == "discovery":
            print("🔍 Starting Agent Discovery Demo...")
            bureau = create_agent_discovery_bureau()
            bureau.run()
            
        elif mode == "sync":
            print("🔄 Starting Synchronous Communication Demo...")
            bureau = create_sync_communication_demo()
            bureau.run()
            
        else:
            print("❌ Unknown mode. Use: full, discovery, or sync")
    else:
        print("🎯 ETH Delhi 2025 - Agent Communication Demos")
        print("Usage:")
        print("  python improved_bureau.py full      # Full validation bureau")
        print("  python improved_bureau.py discovery # Agent discovery demo") 
        print("  python improved_bureau.py sync      # Sync communication demo")