# Implementação do Chat Flutuante

## Visão Geral

O chat foi transformado de uma página dedicada em um widget flutuante global, disponível em todas as páginas do sistema, seguindo o padrão de mercado de chatbots modernos.

## Arquitetura

### 1. Componente FloatingChat.vue
**Localização**: `frontend/app/components/FloatingChat.vue`

**Características**:
- Widget flutuante no canto inferior direito
- Expansível/minimizável com animações suaves
- Dimensões: 400px x 600px quando expandido
- Botão circular com ícone de chat quando minimizado
- Badge de notificação para mensagens não lidas

**Estados**:
- **Minimizado**: Botão circular flutuante
- **Expandido**: Janela de chat completa

### 2. Layout Global
**Localização**: `frontend/app/layouts/default.vue`

**Função**: Inclui o FloatingChat em todas as páginas automaticamente

### 3. Página Chat Atualizada
**Localização**: `frontend/app/pages/chat.vue`

**Mudança**: Agora redireciona para o dashboard com mensagem explicativa

## Funcionalidades

### Interface do Chat

#### Header
- Avatar do assistente (🤖)
- Status "Online"
- Botão de limpar histórico
- Botão de minimizar

#### Área de Mensagens
- Scroll automático para última mensagem
- Mensagens do usuário: alinhadas à direita, fundo azul
- Mensagens do assistente: alinhadas à esquerda, com avatar
- Suporte a Markdown nas respostas
- Timestamps em cada mensagem
- Indicador de "digitando..." durante carregamento

#### Tela de Boas-vindas
- Mensagem de boas-vindas
- Sugestões de perguntas rápidas:
  - "Quantas notas fiscais tenho?"
  - "Qual o valor total das notas?"

#### Área de Input
- Textarea com auto-resize
- Limite de altura: 80px
- Enter para enviar
- Shift+Enter para nova linha
- Botão de envio circular

### Botão Flutuante

#### Visual
- Gradiente azul (primary)
- Tamanho: 64px (btn-lg)
- Sombra pronunciada
- Efeito hover: escala 110% + sombra maior
- Animação de pulso no hover

#### Ícones
- Minimizado: ícone de chat (💬)
- Expandido: ícone de X
- Transição suave entre ícones

#### Badge de Notificação
- Aparece quando há mensagens não lidas
- Contador de mensagens
- Cor vermelha (badge-error)
- Posição: canto superior direito do botão

## Animações

### Chat Expand/Collapse
- Duração: 300ms
- Easing: cubic-bezier(0.4, 0, 0.2, 1)
- Origem: bottom right
- Efeitos: opacity + scale + translateY

### Ícone do Botão
- Fade in/out: 200ms
- Scale effect

### Mensagens
- Slide in de baixo para cima
- Duração: 300ms

### Botão Hover
- Pulse ring animation
- Duração: 1.5s infinito

## Estilização

### Cores
- **Header**: Gradiente primary
- **Mensagens do usuário**: Primary background
- **Mensagens do assistente**: Base-100 com borda
- **Botão flutuante**: Gradiente primary

### Scrollbar Customizada
- Largura: 6px
- Cor: rgba(0, 0, 0, 0.2)
- Hover: rgba(0, 0, 0, 0.3)
- Border-radius: 3px

### Markdown Styling
- Código inline: background escuro, padding
- Listas: padding-left 1.2em
- Parágrafos: margin reduzido para compactar

## Responsividade

### Desktop
- Posição fixa: bottom-right
- Largura: 400px
- Altura: 600px

### Mobile
- Mesmas dimensões (pode ser ajustado se necessário)
- Z-index: 50 (sempre no topo)

## Integração com API

### Endpoints Utilizados
- `chatMessage(message)`: Envia mensagem e recebe resposta
- `clearChatHistory()`: Limpa histórico de conversas

### Tratamento de Erros
- Alert ao usuário em caso de falha
- Remove mensagem do usuário se request falhar
- Log de erros no console

## Persistência

### Estado Local
- Mensagens armazenadas em `ref([])`
- Não persiste entre reloads (pode ser implementado com localStorage)

### Contador de Não Lidas
- Incrementa quando mensagem chega com chat minimizado
- Reseta ao abrir o chat

## Acessibilidade

- Títulos descritivos nos botões
- Placeholder informativo no input
- Feedback visual de loading
- Contraste adequado de cores

## Melhorias Futuras Sugeridas

1. **Persistência**: Salvar mensagens no localStorage
2. **Notificações**: Som ao receber mensagem
3. **Typing Indicator**: Mostrar quando assistente está "digitando"
4. **Histórico**: Carregar conversas anteriores
5. **Responsivo Mobile**: Fullscreen em telas pequenas
6. **Temas**: Suporte a dark/light mode
7. **Anexos**: Permitir upload de arquivos
8. **Atalhos**: Ctrl+K para abrir chat
9. **Posição**: Permitir arrastar o widget
10. **Minimizar Automático**: Após X minutos de inatividade

## Comparação com Padrões de Mercado

### Inspirações
- **Intercom**: Botão flutuante, expansão suave
- **Drift**: Badge de notificação, mensagens rápidas
- **Zendesk**: Header com status, avatar do agente
- **Crisp**: Animações suaves, design moderno

### Diferenciais Implementados
- Suporte a Markdown nas respostas
- Sugestões de perguntas rápidas
- Gradiente moderno no header
- Animações fluidas e profissionais

## Uso

### Para o Usuário
1. Procure o botão azul no canto inferior direito
2. Clique para expandir o chat
3. Digite sua pergunta e pressione Enter
4. Minimize clicando no X ou no botão novamente

### Para o Desenvolvedor
O componente é automaticamente incluído em todas as páginas através do layout default. Não é necessária nenhuma configuração adicional.

```vue
<!-- Já incluído automaticamente em todas as páginas -->
<FloatingChat />
```

## Testes Recomendados

1. ✅ Abrir/fechar chat
2. ✅ Enviar mensagem
3. ✅ Receber resposta
4. ✅ Limpar histórico
5. ✅ Mensagens rápidas
6. ✅ Badge de notificação
7. ✅ Scroll automático
8. ✅ Auto-resize do textarea
9. ✅ Markdown rendering
10. ✅ Animações suaves
