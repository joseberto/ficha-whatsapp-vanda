# Ficha de Cadastro pelo WhatsApp

Projeto preparado para o número central **+55 85 92001-3309**, de **Vanda Silva**.

## Como funciona

1. Vanda compartilha o link inicial:
   `https://wa.me/5585920013309?text=CADASTRO%20VANDA`
2. A pessoa toca no link e envia a mensagem já preenchida ao número central.
3. O robô responde com o botão **PREENCHER FICHA**, dentro do WhatsApp.
4. A ficha mostra quem indicou e solicita:
   - nome completo;
   - número do título;
   - zona e seção;
   - endereço completo;
   - data de nascimento;
   - CPF;
   - celular;
   - autorização de tratamento dos dados.
5. Ao enviar, o sistema grava o cadastro, gera o PDF e devolve uma cópia à pessoa.
6. O sistema cria um link exclusivo para essa pessoa encaminhar. Quem abrir o novo link ficará registrado como indicação direta dela.

Exemplo:

`Vanda -> João -> Ana -> Carlos`

No cadastro de Carlos fica registrado apenas **"Indicado por: Ana"**. Todos os cadastros chegam ao número central da Vanda, independentemente de quantos encaminhamentos ocorreram antes.

## Resposta à dúvida sobre os tipos de WhatsApp

- O número central precisa estar conectado à **WhatsApp Business Platform (Cloud API)** para usar o formulário nativo WhatsApp Flows e a automação.
- Quem recebe, preenche ou compartilha pode usar **WhatsApp normal ou WhatsApp Business**.
- O encaminhamento é feito por um link personalizado. Isso é necessário para identificar corretamente quem indicou quem.
- Não transforme nem remova o WhatsApp atual do número antes de fazer backup e confirmar o método de conexão. Dependendo da conta/provedor, pode haver coexistência com o aplicativo WhatsApp Business.

## O que já está pronto neste pacote

- `flow/flow.json`: formulário nativo do WhatsApp;
- `app/main.py`: webhook, envio do Flow e processamento das respostas;
- `app/database.py`: banco SQLite e indicação direta;
- `app/pdf_generator.py`: PDF preenchido automaticamente;
- `scripts/setup_flow.py`: cria e publica o Flow na conta Meta;
- `scripts/export_report.py`: relatório CSV com o indicador direto;
- `output/pdf/ficha_cadastro_modelo.pdf`: prévia do PDF;
- `Dockerfile` e `render.yaml`: implantação no Render.

## Ativação - passos exatos

### 1. Preparar a conta da Meta

É necessário ter:

- Portfólio empresarial da Meta;
- conta do WhatsApp Business (WABA);
- aplicativo da Meta com o produto WhatsApp;
- número **+55 85 92001-3309** verificado na plataforma;
- token permanente;
- `PHONE_NUMBER_ID`, `WABA_ID` e `META_APP_SECRET`.

Essas credenciais são secretas. Não devem ser colocadas no código nem enviadas em conversa pública.

### 2. Configurar as variáveis

Copie `.env.example` para `.env` e preencha somente os valores secretos/IDs que vierem da Meta.

### 3. Instalar e testar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

No Windows, a ativação do ambiente é:

```powershell
.venv\Scripts\activate
```

Teste de saúde: `http://localhost:8000/health`.

### 4. Criar e publicar o WhatsApp Flow

Com `.env` preenchido:

```bash
python scripts/setup_flow.py
```

Copie o `FLOW_ID` mostrado pelo script para o ambiente do servidor.

### 5. Publicar no Render

1. Envie esta pasta a um repositório privado.
2. No Render, crie um **Web Service** a partir do repositório.
3. Cadastre todas as variáveis de `.env.example` no painel do serviço.
4. Use uma pasta persistente para `/data` ou troque SQLite por PostgreSQL antes de grande volume.
5. A URL pública terá o formato `https://SEU-SERVICO.onrender.com`.

### 6. Ligar o webhook na Meta

- URL de callback: `https://SEU-SERVICO.onrender.com/webhook`
- token de verificação: o mesmo valor de `WEBHOOK_VERIFY_TOKEN`
- assine o campo `messages`.

### 7. Testar o fluxo completo

1. Abra o link inicial em outro celular.
2. Envie a mensagem `CADASTRO VANDA`.
3. Toque em **PREENCHER FICHA**.
4. Preencha e envie.
5. Confira a confirmação, o PDF e o novo link personalizado.
6. Abra o novo link em um terceiro celular e confirme se o indicador direto foi registrado.

## Relatório

Para exportar todos os cadastros:

```bash
python scripts/export_report.py
```

O arquivo `output/relatorio_cadastros.csv` conterá cada pessoa e seu indicador direto. CPF e título não aparecem no relatório gerencial por padrão; continuam protegidos no cadastro e no PDF individual.

## Segurança e LGPD

- O formulário exige consentimento.
- O código de indicação não contém CPF, título ou telefone.
- O webhook valida a assinatura enviada pela Meta.
- Use HTTPS e mantenha tokens apenas nas variáveis secretas do servidor.
- Restrinja o acesso ao banco e aos PDFs.
- Defina prazo de retenção e procedimento de exclusão dos dados.

## Observação importante

O sistema e os arquivos estão prontos para implantação, mas a ativação real depende da verificação do número e das credenciais da conta Meta. A aprovação/configuração da conta não pode ser executada apenas com o número de telefone.
