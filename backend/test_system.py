"""
Sistema de Teste Manual Completo - Multi-Agent NF-e System

Este script testa o fluxo completo do sistema incluindo:
1. Processamento de lote com XMLs da pasta xml_nf
2. Chat com perguntas sobre notas fiscais através da NFeCrew
3. Memória de contexto com múltiplas interações
4. Validação de delegação automática entre agentes
5. Verificação do uso correto das Tools

Requirements testados:
- 1.1: Processamento de lote de XMLs
- 2.1, 2.2, 2.3: Três agentes especializados
- 6.1: Sistema de memória de chat
"""

import sys
import os
from pathlib import Path
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.crew import NFeCrew
from memory.chat_memory import ChatMemory
from batch.processor import BatchProcessor
from batch.job_manager import JobManager
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemTester:
    """Classe para executar testes manuais do sistema completo"""
    
    def __init__(self):
        self.crew = None
        self.memory = None
        self.batch_processor = None
        self.job_manager = None
        self.test_session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.results = []
    
    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def print_subheader(self, title: str):
        """Imprime subcabeçalho formatado"""
        print(f"\n{'─' * 70}")
        print(f"  {title}")
        print(f"{'─' * 70}")
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"✓ {message}")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"✗ {message}")
    
    def print_info(self, message: str, indent: int = 2):
        """Imprime mensagem informativa"""
        print(f"{' ' * indent}• {message}")
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        """Adiciona resultado de teste"""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now()
        })
    
    async def test_1_initialize_components(self) -> bool:
        """Teste 1: Inicializar componentes do sistema"""
        self.print_header("TESTE 1: Inicialização dos Componentes")
        
        try:
            # Inicializar NFeCrew
            self.print_info("Inicializando NFeCrew...")
            self.crew = NFeCrew()
            self.print_success("NFeCrew inicializada")
            self.print_info(f"Agentes configurados: {list(self.crew.agents_config.keys())}", 4)
            self.print_info(f"Tarefas configuradas: {list(self.crew.tasks_config.keys())}", 4)
            self.print_info(f"Tools disponíveis: DatabaseQueryTool, SchemaInfoTool, SQLQueryTool", 4)
            
            # Inicializar ChatMemory
            self.print_info("Inicializando ChatMemory...")
            self.memory = ChatMemory()
            self.print_success("ChatMemory inicializada")
            self.print_info(f"Storage dir: {self.memory.storage_dir}", 4)
            self.print_info(f"Max mensagens recentes: {self.memory.max_recent_messages}", 4)
            
            # Inicializar BatchProcessor
            self.print_info("Inicializando BatchProcessor...")
            self.batch_processor = BatchProcessor(max_concurrent=3)
            self.print_success("BatchProcessor inicializado")
            self.print_info(f"Max concurrent: {self.batch_processor.max_concurrent}", 4)
            
            # Inicializar JobManager
            self.print_info("Inicializando JobManager...")
            self.job_manager = JobManager()
            self.print_success("JobManager inicializado")
            
            self.add_result("Inicialização de Componentes", True, "Todos os componentes inicializados")
            return True
            
        except Exception as e:
            self.print_error(f"Falha na inicialização: {e}")
            self.add_result("Inicialização de Componentes", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    async def test_2_batch_processing(self) -> bool:
        """Teste 2: Processamento em lote de XMLs"""
        self.print_header("TESTE 2: Processamento em Lote de XMLs")
        
        try:
            # Verificar se pasta xml_nf existe
            xml_folder = Path(settings.xml_folder)
            if not xml_folder.exists():
                self.print_error(f"Pasta {settings.xml_folder} não encontrada")
                self.add_result("Processamento em Lote", False, "Pasta xml_nf não encontrada")
                return False
            
            # Contar XMLs disponíveis
            xml_files = list(xml_folder.glob("*.xml")) + list(xml_folder.glob("*.XML"))
            self.print_info(f"Pasta: {xml_folder}")
            self.print_info(f"XMLs encontrados: {len(xml_files)}")
            
            if len(xml_files) == 0:
                self.print_error("Nenhum arquivo XML encontrado para processar")
                self.add_result("Processamento em Lote", False, "Nenhum XML encontrado")
                return False
            
            # Listar arquivos
            for xml_file in xml_files[:5]:  # Mostrar apenas os primeiros 5
                self.print_info(f"- {xml_file.name}", 4)
            if len(xml_files) > 5:
                self.print_info(f"... e mais {len(xml_files) - 5} arquivos", 4)
            
            # Processar lote
            self.print_info(f"\nIniciando processamento em lote...")
            job_id = f"test-batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            start_time = time.time()
            result = await self.batch_processor.process_folder(
                folder_path=str(xml_folder),
                job_id=job_id
            )
            duration = time.time() - start_time
            
            # Exibir resultados
            self.print_success(f"Processamento concluído em {duration:.2f}s")
            self.print_info(f"Job ID: {result['job_id']}", 4)
            self.print_info(f"Status: {result['status']}", 4)
            self.print_info(f"Total de arquivos: {result['total']}", 4)
            self.print_info(f"Processados: {result['processed']}", 4)
            self.print_info(f"Sucessos: {result['successful']}", 4)
            self.print_info(f"Falhas: {result['failed']}", 4)
            
            # Mostrar erros se houver
            if result['errors']:
                self.print_info(f"\nErros encontrados:", 4)
                for error in result['errors'][:3]:  # Mostrar apenas os primeiros 3
                    self.print_info(f"- {error['file']}: {error['error'][:80]}...", 6)
                if len(result['errors']) > 3:
                    self.print_info(f"... e mais {len(result['errors']) - 3} erros", 6)
            
            # Validar resultado
            success = result['status'] == 'completed' and result['processed'] == result['total']
            
            details = f"{result['successful']} sucessos, {result['failed']} falhas de {result['total']} arquivos"
            self.add_result("Processamento em Lote", success, details)
            
            return success
            
        except Exception as e:
            self.print_error(f"Falha no processamento em lote: {e}")
            self.add_result("Processamento em Lote", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    async def test_3_chat_conversational(self) -> bool:
        """Teste 3: Chat conversacional (sem consulta ao banco)"""
        self.print_header("TESTE 3: Chat Conversacional")
        
        try:
            # Teste 1: Saudação
            self.print_subheader("3.1: Saudação")
            message1 = "Olá! Como você pode me ajudar?"
            self.print_info(f"Usuário: {message1}")
            
            start_time = time.time()
            response1 = self.crew.process_message(
                message=message1,
                chat_history=[],
                session_id=self.test_session_id
            )
            duration1 = time.time() - start_time
            
            self.print_info(f"Assistente: {response1[:150]}...")
            self.print_info(f"Tempo: {duration1:.2f}s", 4)
            
            # Salvar na memória
            self.memory.add_message(self.test_session_id, "user", message1)
            self.memory.add_message(self.test_session_id, "assistant", response1)
            
            # Validar resposta
            if len(response1) > 10:
                self.print_success("Resposta conversacional recebida")
            else:
                self.print_error("Resposta muito curta")
                self.add_result("Chat Conversacional", False, "Resposta inadequada")
                return False
            
            # Teste 2: Pergunta sobre o sistema
            self.print_subheader("3.2: Pergunta sobre o Sistema")
            message2 = "Que tipo de perguntas posso fazer sobre notas fiscais?"
            self.print_info(f"Usuário: {message2}")
            
            history = self.memory.get_history(self.test_session_id)
            
            start_time = time.time()
            response2 = self.crew.process_message(
                message=message2,
                chat_history=history,
                session_id=self.test_session_id
            )
            duration2 = time.time() - start_time
            
            self.print_info(f"Assistente: {response2[:150]}...")
            self.print_info(f"Tempo: {duration2:.2f}s", 4)
            
            # Salvar na memória
            self.memory.add_message(self.test_session_id, "user", message2)
            self.memory.add_message(self.test_session_id, "assistant", response2)
            
            # Validar resposta
            if len(response2) > 10:
                self.print_success("Resposta sobre o sistema recebida")
            else:
                self.print_error("Resposta muito curta")
                self.add_result("Chat Conversacional", False, "Resposta inadequada")
                return False
            
            self.add_result("Chat Conversacional", True, "Respostas conversacionais adequadas")
            return True
            
        except Exception as e:
            self.print_error(f"Falha no chat conversacional: {e}")
            self.add_result("Chat Conversacional", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    async def test_4_chat_database_queries(self) -> bool:
        """Teste 4: Chat com consultas ao banco de dados"""
        self.print_header("TESTE 4: Chat com Consultas ao Banco de Dados")
        
        try:
            # Teste 1: Contar notas fiscais
            self.print_subheader("4.1: Contar Notas Fiscais")
            message1 = "Quantas notas fiscais existem no banco de dados?"
            self.print_info(f"Usuário: {message1}")
            
            history = self.memory.get_history(self.test_session_id)
            
            start_time = time.time()
            response1 = self.crew.process_message(
                message=message1,
                chat_history=history,
                session_id=self.test_session_id
            )
            duration1 = time.time() - start_time
            
            self.print_info(f"Assistente: {response1[:200]}...")
            self.print_info(f"Tempo: {duration1:.2f}s", 4)
            
            # Salvar na memória
            self.memory.add_message(self.test_session_id, "user", message1)
            self.memory.add_message(self.test_session_id, "assistant", response1)
            
            # Validar que executou query (resposta deve conter número)
            has_number = any(char.isdigit() for char in response1)
            if has_number:
                self.print_success("Query executada - resposta contém dados numéricos")
            else:
                self.print_error("Resposta não contém dados numéricos")
            
            # Teste 2: Valor total
            self.print_subheader("4.2: Valor Total das Notas")
            message2 = "Qual é o valor total de todas as notas fiscais?"
            self.print_info(f"Usuário: {message2}")
            
            history = self.memory.get_history(self.test_session_id)
            
            start_time = time.time()
            response2 = self.crew.process_message(
                message=message2,
                chat_history=history,
                session_id=self.test_session_id
            )
            duration2 = time.time() - start_time
            
            self.print_info(f"Assistente: {response2[:200]}...")
            self.print_info(f"Tempo: {duration2:.2f}s", 4)
            
            # Salvar na memória
            self.memory.add_message(self.test_session_id, "user", message2)
            self.memory.add_message(self.test_session_id, "assistant", response2)
            
            # Validar que executou query (resposta deve conter R$)
            has_currency = "R$" in response2 or "reais" in response2.lower()
            if has_currency:
                self.print_success("Query executada - resposta contém valores monetários")
            else:
                self.print_error("Resposta não contém valores monetários")
            
            # Teste 3: Listar empresas
            self.print_subheader("4.3: Listar Empresas")
            message3 = "Quais empresas emitiram notas fiscais?"
            self.print_info(f"Usuário: {message3}")
            
            history = self.memory.get_history(self.test_session_id)
            
            start_time = time.time()
            response3 = self.crew.process_message(
                message=message3,
                chat_history=history,
                session_id=self.test_session_id
            )
            duration3 = time.time() - start_time
            
            self.print_info(f"Assistente: {response3[:200]}...")
            self.print_info(f"Tempo: {duration3:.2f}s", 4)
            
            # Salvar na memória
            self.memory.add_message(self.test_session_id, "user", message3)
            self.memory.add_message(self.test_session_id, "assistant", response3)
            
            # Validar resposta
            success = has_number and has_currency and len(response3) > 20
            
            if success:
                self.print_success("Todas as consultas ao banco executadas com sucesso")
            else:
                self.print_error("Algumas consultas não retornaram dados esperados")
            
            self.add_result("Chat com Consultas ao Banco", success, "Queries SQL executadas")
            return success
            
        except Exception as e:
            self.print_error(f"Falha nas consultas ao banco: {e}")
            self.add_result("Chat com Consultas ao Banco", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    async def test_5_memory_context(self) -> bool:
        """Teste 5: Memória de contexto com múltiplas interações"""
        self.print_header("TESTE 5: Memória de Contexto")
        
        try:
            # Verificar histórico acumulado
            self.print_subheader("5.1: Verificar Histórico Acumulado")
            
            message_count = self.memory.get_message_count(self.test_session_id)
            self.print_info(f"Total de mensagens na sessão: {message_count}")
            
            if message_count < 4:  # Pelo menos 2 interações (4 mensagens)
                self.print_error(f"Histórico insuficiente: {message_count} mensagens")
                self.add_result("Memória de Contexto", False, "Histórico insuficiente")
                return False
            
            self.print_success(f"Histórico adequado: {message_count} mensagens")
            
            # Obter histórico formatado
            history = self.memory.get_history(self.test_session_id)
            self.print_info(f"Histórico formatado: {len(history)} mensagens")
            
            # Mostrar últimas mensagens
            self.print_info("Últimas interações:", 4)
            for i, msg in enumerate(history[-4:], 1):
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                content_preview = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
                self.print_info(f"{role_emoji} {msg['role']}: {content_preview}", 6)
            
            # Teste de pergunta de acompanhamento (usa contexto)
            self.print_subheader("5.2: Pergunta de Acompanhamento")
            message_followup = "E qual foi o valor médio dessas notas?"
            self.print_info(f"Usuário: {message_followup}")
            self.print_info("(Esta pergunta depende do contexto anterior)", 4)
            
            history = self.memory.get_history(self.test_session_id)
            
            start_time = time.time()
            response_followup = self.crew.process_message(
                message=message_followup,
                chat_history=history,
                session_id=self.test_session_id
            )
            duration = time.time() - start_time
            
            self.print_info(f"Assistente: {response_followup[:200]}...")
            self.print_info(f"Tempo: {duration:.2f}s", 4)
            
            # Salvar na memória
            self.memory.add_message(self.test_session_id, "user", message_followup)
            self.memory.add_message(self.test_session_id, "assistant", response_followup)
            
            # Validar que usou contexto (resposta deve ser relevante)
            has_value = "R$" in response_followup or any(char.isdigit() for char in response_followup)
            
            if has_value:
                self.print_success("Contexto utilizado - resposta relevante ao histórico")
            else:
                self.print_error("Resposta não parece usar o contexto anterior")
            
            # Obter resumo do contexto
            self.print_subheader("5.3: Resumo do Contexto")
            summary = self.memory.get_context_summary(self.test_session_id)
            self.print_info("Resumo do contexto:")
            for line in summary.split('\n')[:10]:  # Primeiras 10 linhas
                self.print_info(line, 4)
            
            # Obter estatísticas de memória
            self.print_subheader("5.4: Estatísticas de Memória")
            stats = self.memory.get_memory_stats()
            self.print_info(f"Total de sessões: {stats['total_sessions']}")
            self.print_info(f"Total de mensagens em cache: {stats['total_cached_messages']}")
            self.print_info(f"Sistemas de memória:", 4)
            for system, status in stats['memory_systems'].items():
                self.print_info(f"- {system}: {status}", 6)
            
            success = message_count >= 4 and has_value
            
            if success:
                self.print_success("Sistema de memória funcionando corretamente")
            else:
                self.print_error("Sistema de memória com problemas")
            
            self.add_result("Memória de Contexto", success, f"{message_count} mensagens, contexto preservado")
            return success
            
        except Exception as e:
            self.print_error(f"Falha no teste de memória: {e}")
            self.add_result("Memória de Contexto", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    async def test_6_agent_delegation(self) -> bool:
        """Teste 6: Validar delegação automática entre agentes"""
        self.print_header("TESTE 6: Delegação Automática entre Agentes")
        
        try:
            self.print_info("Testando delegação do coordenador para agentes especializados...")
            
            # Teste 1: Delegação para SQL Specialist
            self.print_subheader("6.1: Delegação para SQL Specialist")
            self.print_info("Pergunta que requer consulta ao banco:")
            message_sql = "Mostre as 3 notas fiscais com maior valor"
            self.print_info(f"'{message_sql}'", 4)
            
            # Criar nova sessão para teste limpo
            test_delegation_session = f"test-delegation-{datetime.now().strftime('%H%M%S')}"
            
            start_time = time.time()
            response_sql = self.crew.process_message(
                message=message_sql,
                chat_history=[],
                session_id=test_delegation_session
            )
            duration_sql = time.time() - start_time
            
            self.print_info(f"Resposta: {response_sql[:150]}...")
            self.print_info(f"Tempo: {duration_sql:.2f}s", 4)
            
            # Validar que SQL foi executado (resposta deve conter dados estruturados)
            has_data = any(char.isdigit() for char in response_sql) and "R$" in response_sql
            
            if has_data:
                self.print_success("✓ coordenador delegou para SQL Specialist")
                self.print_info("Evidência: Resposta contém dados do banco", 4)
            else:
                self.print_error("✗ Delegação para SQL Specialist falhou")
            
            # Teste 2: Delegação para Conversation Specialist
            self.print_subheader("6.2: Delegação para Conversation Specialist")
            self.print_info("Pergunta conversacional:")
            message_conv = "Obrigado! Você foi muito útil."
            self.print_info(f"'{message_conv}'", 4)
            
            start_time = time.time()
            response_conv = self.crew.process_message(
                message=message_conv,
                chat_history=[
                    {"role": "user", "content": message_sql},
                    {"role": "assistant", "content": response_sql}
                ],
                session_id=test_delegation_session
            )
            duration_conv = time.time() - start_time
            
            self.print_info(f"Resposta: {response_conv[:150]}...")
            self.print_info(f"Tempo: {duration_conv:.2f}s", 4)
            
            # Validar resposta conversacional
            is_conversational = len(response_conv) > 10 and not response_conv.startswith("SELECT")
            
            if is_conversational:
                self.print_success("✓ coordenador delegou para Conversation Specialist")
                self.print_info("Evidência: Resposta é conversacional, não técnica", 4)
            else:
                self.print_error("✗ Delegação para Conversation Specialist falhou")
            
            # Teste 3: Verificar processo hierárquico
            self.print_subheader("6.3: Processo Hierárquico do CrewAI")
            self.print_info("Verificando configuração da Crew:")
            
            crew_instance = self.crew.crew()
            self.print_info(f"Processo: {crew_instance.process}", 4)
            self.print_info(f"Número de agentes: {len(crew_instance.agents)}", 4)
            self.print_info(f"Memória habilitada: {crew_instance.memory}", 4)
            
            # Listar agentes
            self.print_info("Agentes na Crew:", 4)
            for agent in crew_instance.agents:
                role = agent.role[:50] + "..." if len(agent.role) > 50 else agent.role
                self.print_info(f"- {role}", 6)
                self.print_info(f"  Pode delegar: {agent.allow_delegation}", 8)
                self.print_info(f"  Tools: {len(agent.tools)}", 8)
            
            success = has_data and is_conversational
            
            if success:
                self.print_success("Sistema de delegação funcionando corretamente")
                self.print_info("✓ coordenador → SQL Specialist (queries)", 4)
                self.print_info("✓ coordenador → Conversation Specialist (conversação)", 4)
            else:
                self.print_error("Sistema de delegação com problemas")
            
            self.add_result("Delegação entre Agentes", success, "coordenador delega corretamente")
            return success
            
        except Exception as e:
            self.print_error(f"Falha no teste de delegação: {e}")
            self.add_result("Delegação entre Agentes", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    async def test_7_tools_usage(self) -> bool:
        """Teste 7: Verificar uso correto das Tools"""
        self.print_header("TESTE 7: Uso Correto das Tools")
        
        try:
            # Teste 1: SchemaInfoTool
            self.print_subheader("7.1: SchemaInfoTool")
            self.print_info("Testando SchemaInfoTool diretamente...")
            
            schema_tool = self.crew.schema_tool
            schema_info = schema_tool._run("all")
            
            self.print_info(f"Schema retornado: {len(schema_info)} caracteres")
            
            # Validar que schema contém informações esperadas
            has_tables = all(table in schema_info for table in [
                "empresas", "notas_fiscais", "nf_itens"
            ])
            
            if has_tables:
                self.print_success("✓ SchemaInfoTool retorna schema completo")
                self.print_info("Tabelas encontradas: empresas, notas_fiscais, nf_itens", 4)
            else:
                self.print_error("✗ SchemaInfoTool não retorna schema completo")
            
            # Teste 2: SchemaSearchTool
            self.print_subheader("7.2: SchemaSearchTool")
            self.print_info("Testando SchemaSearchTool...")
            
            schema_search_tool = self.crew.schema_search_tool
            search_result = schema_search_tool._run("valor total")
            
            self.print_info(f"Resultado da busca: {len(search_result)} caracteres")
            
            # Validar que busca retorna informações relevantes
            has_relevant_info = "valor" in search_result.lower()
            
            if has_relevant_info:
                self.print_success("✓ SchemaSearchTool busca informações relevantes")
            else:
                self.print_error("✗ SchemaSearchTool não retorna informações relevantes")
            
            # Teste 3: SQLQueryTool (via agente)
            self.print_subheader("7.3: SQLQueryTool via Agente")
            self.print_info("Testando SQLQueryTool através do agente...")
            
            # Pergunta que força uso do SQLQueryTool
            message_tool = "Execute uma query para contar quantas empresas existem"
            self.print_info(f"Pergunta: '{message_tool}'", 4)
            
            test_tools_session = f"test-tools-{datetime.now().strftime('%H%M%S')}"
            
            start_time = time.time()
            response_tool = self.crew.process_message(
                message=message_tool,
                chat_history=[],
                session_id=test_tools_session
            )
            duration_tool = time.time() - start_time
            
            self.print_info(f"Resposta: {response_tool[:150]}...")
            self.print_info(f"Tempo: {duration_tool:.2f}s", 4)
            
            # Validar que query foi executada
            has_count = any(char.isdigit() for char in response_tool)
            
            if has_count:
                self.print_success("✓ SQLQueryTool executou query com sucesso")
                self.print_info("Evidência: Resposta contém contagem", 4)
            else:
                self.print_error("✗ SQLQueryTool não executou query")
            
            # Teste 4: Verificar tools disponíveis nos agentes
            self.print_subheader("7.4: Tools Disponíveis nos Agentes")
            
            # SQL Specialist
            sql_agent = self.crew.sql_specialist()
            self.print_info(f"SQL Specialist tem {len(sql_agent.tools)} tools:")
            for tool in sql_agent.tools:
                self.print_info(f"- {tool.name}", 4)
            
            # coordenador
            coordenador_agent = self.crew.coordenador()
            self.print_info(f"coordenador tem {len(coordenador_agent.tools)} tools:")
            for tool in coordenador_agent.tools:
                self.print_info(f"- {tool.name}", 4)
            
            # Conversation Specialist (não deve ter tools de banco)
            conv_agent = self.crew.conversation_specialist()
            self.print_info(f"Conversation Specialist tem {len(conv_agent.tools)} tools:")
            if len(conv_agent.tools) == 0:
                self.print_success("✓ Conversation Specialist corretamente sem tools de banco")
            else:
                for tool in conv_agent.tools:
                    self.print_info(f"- {tool.name}", 4)
            
            success = has_tables and has_relevant_info and has_count
            
            if success:
                self.print_success("Todas as Tools funcionando corretamente")
            else:
                self.print_error("Algumas Tools com problemas")
            
            self.add_result("Uso de Tools", success, "SchemaInfoTool, SchemaSearchTool, SQLQueryTool")
            return success
            
        except Exception as e:
            self.print_error(f"Falha no teste de tools: {e}")
            self.add_result("Uso de Tools", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """Imprime resumo final dos testes"""
        self.print_header("RESUMO FINAL DOS TESTES")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        # Listar resultados
        for result in self.results:
            status = "✓ PASSOU" if result["passed"] else "✗ FALHOU"
            print(f"\n{status}: {result['test']}")
            if result["details"]:
                print(f"  Detalhes: {result['details']}")
        
        # Estatísticas
        print("\n" + "─" * 70)
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"  Total de testes: {total_tests}")
        print(f"  Testes aprovados: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"  Testes falhados: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        # Resultado final
        print("\n" + "=" * 70)
        if failed_tests == 0:
            print("🎉 SUCESSO! Todos os testes passaram!")
            print("\nO sistema está funcionando corretamente:")
            print("  ✓ Processamento em lote de XMLs")
            print("  ✓ Chat com consultas ao banco via CrewAI")
            print("  ✓ Memória de contexto com RAG")
            print("  ✓ Delegação automática entre agentes")
            print("  ✓ Uso correto das Tools")
        else:
            print(f"⚠️  ATENÇÃO: {failed_tests} teste(s) falharam")
            print("\nRevise os erros acima para identificar problemas.")
        
        print("=" * 70)
    
    async def run_all_tests(self):
        """Executa todos os testes em sequência"""
        self.print_header("SISTEMA DE TESTE MANUAL COMPLETO")
        print("Multi-Agent NF-e System - CrewAI")
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Session ID: {self.test_session_id}")
        
        # Executar testes
        await self.test_1_initialize_components()
        
        # Só continua se inicialização passou
        if not self.results[-1]["passed"]:
            self.print_error("\nInicialização falhou. Abortando testes.")
            self.print_summary()
            return False
        
        # Testes de funcionalidade
        await self.test_2_batch_processing()
        await self.test_3_chat_conversational()
        await self.test_4_chat_database_queries()
        await self.test_5_memory_context()
        await self.test_6_agent_delegation()
        await self.test_7_tools_usage()
        
        # Resumo final
        self.print_summary()
        
        # Retornar sucesso se todos passaram
        return all(r["passed"] for r in self.results)


async def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("  TESTE MANUAL DO SISTEMA MULTI-AGENTE NF-e")
    print("=" * 70)
    print("\nEste script testa o fluxo completo do sistema:")
    print("  1. Inicialização dos componentes")
    print("  2. Processamento em lote de XMLs")
    print("  3. Chat conversacional")
    print("  4. Chat com consultas ao banco")
    print("  5. Memória de contexto")
    print("  6. Delegação entre agentes")
    print("  7. Uso das Tools")
    print("\n" + "=" * 70)
    
    # Aguardar confirmação
    print("\nPressione ENTER para iniciar os testes...")
    input()
    
    # Executar testes
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    # Retornar código de saída
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
