"""
ProSports AI - Professor Betão Voice Agent
Agente de voz para atendimento telefônico via LiveKit SIP
"""

import logging
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    RoomInputOptions,
)
from livekit.plugins import openai, silero

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("professor-betao")

# Prompt do Professor Betão
SYSTEM_PROMPT = """Você é o Professor Betão, um especialista brasileiro em análise esportiva e apostas de valor.

PERSONALIDADE:
- Fala como um técnico de futebol experiente e carismático
- Usa expressões brasileiras naturais ("Opa!", "Olha só", "É isso aí!", "Beleza!")
- É direto, confiante, mas sempre responsável
- Nunca promete ganhos, sempre fala em probabilidades e análise
- Fala de forma concisa, máximo 2-3 frases por resposta

REGRAS IMPORTANTES:
- NUNCA invente dados ou estatísticas
- Se não souber algo, diga honestamente
- Sempre lembre o usuário sobre jogo responsável
- Mantenha respostas curtas e objetivas
- Pergunte se o usuário quer mais detalhes

SAUDAÇÃO INICIAL (use ao iniciar):
"E aí, tudo bem? Aqui é o Professor Betão do ProSports AI! Como posso te ajudar hoje?"

DESPEDIDA:
"Valeu demais! Lembre-se: aposte com responsabilidade. Abraço do Betão!"
"""


class ProfessorBetao(Agent):
    """Agente de voz Professor Betão"""

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
        )


async def entrypoint(ctx: JobContext):
    """Ponto de entrada do agente - chamado quando uma ligação entra"""
    logger.info(f"Nova chamada recebida! Room: {ctx.room.name}")

    # Conectar à sala LiveKit
    await ctx.connect()
    logger.info("Conectado à sala LiveKit")

    # Configurar a sessão com OpenAI
    session = AgentSession(
        stt=openai.STT(
            model="whisper-1",
            language="pt",
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),
        tts=openai.TTS(
            model="tts-1",
            voice="onyx",  # Voz masculina grave
        ),
        vad=silero.VAD.load(),
    )

    # Criar instância do agente
    agent = ProfessorBetao()

    # Iniciar sessão
    session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            text_enabled=False,
            audio_enabled=True,
        ),
    )

    logger.info("Professor Betão iniciado e pronto para conversar!")

    # Manter a sessão ativa enquanto a chamada durar
    await session.wait()
    logger.info("Sessão encerrada")


if __name__ == "__main__":
    logger.info("Iniciando worker Professor Betão...")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="professor-betao",
        )
    )
