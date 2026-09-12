# Guia simplificado - sem Meta e sem Render

Esta versão foi criada para colocar o cadastro em funcionamento rapidamente.

## O que ela faz

- abre o formulário no navegador interno do WhatsApp;
- identifica o indicador direto pelo link;
- valida CPF e telefone;
- abre a conversa do número central de Vanda Silva com a ficha preenchida;
- gera uma imagem da ficha;
- cria um link pessoal para cada participante compartilhar.

## O que não é necessário

- conta de desenvolvedor da Meta;
- WhatsApp Cloud API;
- token;
- Render;
- servidor pago;
- banco de dados.

## Publicação no GitHub Pages

1. Abra o repositório `ficha-whatsapp-vanda`.
2. Entre em `Settings`.
3. Entre em `Pages`.
4. Em `Build and deployment`, selecione `Deploy from a branch`.
5. Selecione a branch `main` e a pasta `/ (root)`.
6. Clique em `Save`.

O GitHub mostrará o endereço público do formulário.

## Primeiro link

Ao final do endereço publicado, acrescente:

`?indicado_por=Vanda%20Silva`

Esse será o link inicial da Vanda.

## Fluxo direto

- Vanda compartilha o link inicial com João.
- João preenche: indicado por Vanda Silva.
- Após preencher, João toca em `COMPARTILHAR MEU LINK`.
- Ana abre o link de João: indicado por João.
- Todos enviam o cadastro diretamente para o WhatsApp de Vanda.
