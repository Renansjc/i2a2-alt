"""
Teste ao vivo da API - Execute com o main.py rodando
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Imprime resposta formatada"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)


def test_health():
    """Testa health check"""
    print("\n🏥 Testando Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_detailed_health():
    """Testa health detalhado"""
    print("\n🔍 Testando Health Detalhado...")
    response = requests.get(f"{BASE_URL}/health/detailed")
    print_response("Health Detalhado", response)
    
    if response.status_code == 200:
        data = response.json()
        services = data.get("services", {})
        
        print("\n📊 Status dos Serviços:")
        for service, info in services.items():
            status = "✅" if info.get("initialized") else "❌"
            print(f"  {status} {service}: {info.get('initialized', False)}")
    
    return response.status_code == 200


def test_chat_greeting():
    """Testa chat com saudação"""
    print("\n💬 Testando Chat - Saudação...")
    
    payload = {
        "session_id": "test-session-001",
        "message": "Olá! Como você pode me ajudar?"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload
    )
    
    print_response("Chat - Saudação", response)
    return response.status_code == 200


def test_chat_database_query():
    """Testa chat com consulta ao banco"""
    print("\n🗄️ Testando Chat - Consulta ao Banco...")
    
    payload = {
        "session_id": "test-session-001",
        "message": "Quantas notas fiscais existem no banco de dados?"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload
    )
    
    print_response("Chat - Consulta ao Banco", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📝 Resposta do Agente: {data.get('message', '')[:200]}...")
        print(f"⏱️ Tempo de processamento: {data.get('metadata', {}).get('processing_time_ms', 0)}ms")
        print(f"🤖 Agente usado: {data.get('agent_used', 'unknown')}")
    
    return response.status_code == 200


def test_chat_history():
    """Testa recuperação de histórico"""
    print("\n📚 Testando Histórico do Chat...")
    
    response = requests.get(
        f"{BASE_URL}/api/chat/history/test-session-001"
    )
    
    print_response("Histórico do Chat", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n💬 Total de mensagens: {data.get('message_count', 0)}")
    
    return response.status_code == 200


def test_memory_stats():
    """Testa estatísticas de memória"""
    print("\n📊 Testando Estatísticas de Memória...")
    
    response = requests.get(f"{BASE_URL}/api/chat/stats")
    print_response("Estatísticas de Memória", response)
    return response.status_code == 200


def test_batch_list_jobs():
    """Testa listagem de jobs batch"""
    print("\n📦 Testando Listagem de Jobs Batch...")
    
    response = requests.get(f"{BASE_URL}/api/batch/jobs")
    print_response("Lista de Jobs Batch", response)
    return response.status_code == 200


def main():
    """Executa todos os testes"""
    print("="*60)
    print("🚀 TESTE AO VIVO DA API")
    print("="*60)
    print(f"URL Base: {BASE_URL}")
    print("Certifique-se de que o main.py está rodando!")
    print("="*60)
    
    # Aguarda um momento
    time.sleep(1)
    
    results = []
    
    # Testes básicos
    results.append(("Health Check", test_health()))
    results.append(("Health Detalhado", test_detailed_health()))
    
    # Testes de chat
    results.append(("Chat - Saudação", test_chat_greeting()))
    time.sleep(2)  # Aguarda processamento
    
    results.append(("Chat - Consulta BD", test_chat_database_query()))
    time.sleep(2)  # Aguarda processamento
    
    results.append(("Histórico Chat", test_chat_history()))
    results.append(("Estatísticas Memória", test_memory_stats()))
    
    # Testes de batch
    results.append(("Lista Jobs Batch", test_batch_list_jobs()))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n📈 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! A API está funcionando perfeitamente!")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique os logs acima.")
    
    print("\n💡 Dica: Acesse http://localhost:8000/docs para testar interativamente!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API!")
        print("Certifique-se de que o main.py está rodando em http://localhost:8000")
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
