"""
EXEMPLES LIVE: MCP Real i Aura Real

Demostra que ambdós adapters són només "portals" cap al matix use case.

El que fa que siguin "reals":
1. Registren tools o métodes reals al teu framework
2. Traducen el protocol del framework cap a AskCommand
3. Deleguen tota la lògica a container/use case
4. Retornen resposta amb format que el framework espera

TODO: Afegir aquí codi real quan tinguis la versió final de MCP o Aura.
"""

# ============================================================================
# ESCENARI 1: MCP Server registrant tool i rebent crides
# ============================================================================

# Pseudocodi del que faria el teu servidor MCP real:
#
# from mcp_host.server_real import MCPServerRealSimulation
# import asyncio
#
# async def main():
#     server = MCPServerRealSimulation()
#
#     # Codi MCP real registraria les tools amb la llibreria MCP
#     # (això és pseudocodi del que faries amb la teva llibreria):
#     #
#     # for tool in server.list_tools():
#     #     mcp_lib.register_tool(tool.name, tool.description, tool.schema)
#
#     # Client crida la tool
#     result = await server.execute_tool(
#         "ask_llm",
#         {
#             "conversation_id": "sess-123",
#             "message": "Quin és el sentit de la vida?",
#         },
#     )
#
#     print(f"MCP Tool Result: {result}")
#     # Output: {'answer': '[echo local] Quin és el sentit de la vida?', 'model': 'local-echo'}


# ============================================================================
# ESCENARI 2: Aura Framework processi una request
# ============================================================================

# Pseudocodi del que faria el teu Aura framework real:
#
# from aura_host.adapter_real import AuraAdapterReal, AuraRequest
# import asyncio
#
# async def main():
#     adapter = AuraAdapterReal()
#
#     # El teu Aura crea una request
#     request = AuraRequest(
#         session_id="aura-user-42",
#         prompt="Explica'm la fotosíntesi",
#         context={"language": "ca", "tone": "academic"},
#     )
#
#     # El teu Aura envia la request
#     response = await adapter.process(request)
#
#     print(f"Aura Response: {response.reply}")
#     # Output: [echo local] Explica'm la fotosíntesi


# ============================================================================
# ESCENARI 3: Els dos cridats simultàniament, compartint historial
# ============================================================================

# from mcp_host.server_real import MCPServerRealSimulation
# from aura_host.adapter_real import AuraAdapterReal, AuraRequest
# from llm_infrastructure.composition.container import Container
# import asyncio
#
# async def main():
#     container = Container()
#
#     # MCP server i Aura adapter compartiex el MATEIX container
#     mcp_server = MCPServerRealSimulation(container=container)
#     aura_adapter = AuraAdapterReal(container=container)
#
#     # MCP client pregunta
#     mcp_result = await mcp_server.execute_tool(
#         "ask_llm",
#         {"conversation_id": "shared", "message": "Hola, soc MCP"}
#     )
#
#     # Aura client pregunta a la MATEIXA conversa
#     aura_request = AuraRequest(
#         session_id="shared",
#         prompt="Hola, soc Aura"
#     )
#     aura_result = await aura_adapter.process(aura_request)
#
#     # Tots dos veuen el historial complet
#     history = await container.memory().load("shared")
#     print(f"Historial compartit ({len(history)} missatges):")
#     for msg in history:
#         print(f"  {msg.role}: {msg.content}")
#
#     # Output:
#     # Historial compartit (4 missatges):
#     #   system: You are a reliable assistant...
#     #   user: Hola, soc MCP
#     #   assistant: [echo local] Hola, soc MCP
#     #   user: Hola, soc Aura
#     #   assistant: [echo local] Hola, soc Aura


# ============================================================================
# COM FER-HO REAL
# ============================================================================

# Quan tinguis la teva llibreria MCP real:
#
# 1. Importa MCPServerRealSimulation a la teva codebase
# 2. Al lloc on registres tools, fes:
#
#    server = MCPServerRealSimulation()
#    for tool in server.list_tools():
#        # usa la teva API de registro de MCP
#        register_tool_to_mcp(tool)
#
# 3. Al teu handler d'execution de tools:
#
#    async def handle_tool_execution(tool_name, args):
#        return await server.execute_tool(tool_name, args)


# Quan tinguis el teu Aura framework finalitzat:
#
# 1. Crea una instancia de AuraAdapterReal
# 2. Al teu entrada principal de Aura:
#
#    adapter = AuraAdapterReal()
#    response = await adapter.process(aura_request)
#
# 3. Aura es comunica completament transparent amb el sistema.
