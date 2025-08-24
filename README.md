# Desafio: API Bancária Assíncrona com FastAPI

O desafio consiste em criar uma API RESTful assíncrona utilizando **FastAPI** para gerenciar operações bancárias — depósitos e saques — associadas a contas correntes.  
A proposta é desenvolver um backend moderno, seguro e performático, empregando autenticação **JWT** e seguindo boas práticas de design de APIs.

## Objetivos

A API deverá contemplar as seguintes funcionalidades:

- **Cadastro de Transações:** Registrar depósitos e saques em contas correntes.
- **Consulta de Extrato:** Disponibilizar um endpoint para exibir o histórico de transações de uma conta.
- **Autenticação JWT:** Garantir que apenas usuários autenticados possam acessar endpoints protegidos.

## Requisitos Técnicos

Para atender ao desafio, deverão ser seguidos os seguintes requisitos:

- **FastAPI:** Utilizar o framework aproveitando seus recursos assíncronos para operações de I/O eficientes.
- **Modelagem de Dados:** Criar modelos que representem contas correntes e transações, garantindo:
  - Associação de transações a contas correntes.
  - Possibilidade de múltiplas transações por conta.
- **Validações:**  
  - Proibir depósitos e saques com valores negativos.  
  - Verificar saldo antes de permitir saques.
- **Segurança:** Implementar autenticação com JWT para proteger endpoints restritos.
- **Documentação:** Utilizar **OpenAPI** para manter a API bem documentada, com descrições claras para endpoints, parâmetros e modelos.


---
<br>


# Resolução do Desafio

## Modelos (Models)

### 1. Usuário (User)
Representa um usuário cadastrado no sistema.

- **id**: `UUID4` – Identificador único do usuário.  
  > O uso do `UUIDv4` garante aleatoriedade na geração dos identificadores, o que aumenta a segurança. No entanto, essa característica dificulta a ordenação em listagens. Uma alternativa seria o `UUIDv7`, que suporta ordenação, mas ainda não é compatível com o Pydantic. Como este é um projeto simples, o uso de `UUIDv4` não traz problemas significativos.
- **username**: `string` – Nome de usuário único utilizado para login.
- **password**: `string` – Senha armazenada em formato *hash*.
- **email**: `Email string` – Endereço de e-mail único.
- **first_name / last_name**: `string` – Nome e sobrenome do usuário.
- **permission**: `UserAccess` – Nível de acesso no sistema.
- **status**: `UserStatus` – Estado atual do usuário (ativo, inativo, suspenso).
- **created_at**: `datetime` – Data e hora de criação do registro.
- **accounts**: `list[Account]` – Relação: contas pertencentes ao usuário.

**Métodos/Propriedades adicionais**:
- **full_name**: `string` – Retorna o nome completo do usuário.

---

### 2. Conta (Account)
Representa uma conta bancária de um usuário.

- **id**: `int` – Identificador único da conta.
- **user_id**: `UUID4` – Chave estrangeira que referencia o usuário proprietário.
- **balance**: `float` – Saldo atual da conta.
- **created_at**: `datetime` – Data e hora de criação da conta.
- **owner**: `User` – Relação: usuário dono da conta.
- **transactions_sent**: `list[Transaction]` – Relação: transações enviadas.
- **transactions_received**: `list[Transaction]` – Relação: transações recebidas.

**Métodos/Propriedades adicionais**:
- **all_transactions**: `list[Transaction]` – Retorna todas as transações (enviadas e recebidas).

---

### 3. Transação (Transaction)
Representa uma movimentação financeira entre contas.

- **id**: `int` – Identificador único da transação.
- **source_account_id**: `int | None` – Chave estrangeira da conta de origem (*nula em depósitos*).
- **destination_account_id**: `int | None` – Chave estrangeira da conta de destino (*nula em saques*).
- **transaction_type**: `TransactionType` – Tipo de transação (ex: depósito, saque, transferência).
- **amount**: `float` – Valor transferido (deve ser > 0).
- **description**: `string | None` – Texto opcional descrevendo a transação.
- **created_at**: `datetime` – Data e hora de criação da transação.

---

## Esquemas (Schemas)

### 1. Usuário (User)
Esquemas de entrada e saída de um Usuário.

- **CreateUser**:
  - `username`: str (Entre 3 a 30 caracteres)
  - `password`: str (Mínimo de 8 caracteres, convertido em hash)
  - `email`: EmailStr
  - `first_name`: str (Máximo de 15 caracteres)
  - `last_name`: str (Máximo de 15 caracteres)

- **UpdateUser**:
  - `username`: str (Entre 3 a 30 caracteres)
  - `password`: str (Mínimo de 8 caracteres, convertido em hash)
  - `email`: EmailStr
  - `first_name`: str (Máximo de 15 caracteres)
  - `last_name`: str (Máximo de 15 caracteres)
  - `permission`: UserAccess | None = None
  - `status`: UserStatus | None = None

- **ShowUser**:
  - `id`: UUID4
  - `username`: str
  - `email`: EmailStr
  - `first_name`: str
  - `last_name`: str
  - `permission`: UserAccess
  - `status`: UserStatus
  - `created_at`: AwareDatetime

---

### 2. Token
Esquemas de entrada e saída de um token.

- **TokenResponse**:
  - `access_token`: str
  - `token_type`: str

- **TokenStore**:
  - `_revoked_tokens`: set[str] = set()
  - `revoke()`: Adiciona o token na lista de tokens revogados
  - `is_revoked()`: Verifica se o token foi revogado.

---

### 3. Conta (Account)
Esquemas de entrada e saída de uma Conta.

- **CreateAccount**:
  - `user_id`: UUID4
  - `balance`: float = 0.0

- **UpdateAccount**:
  - `balance`: float | None = None

- **ShowAccount**:
  - `id`: int
  - `user_id`: str
  - `balance`: float

---

### 4. Transação (Transaction)
Esquemas de entrada e saída para movimentação financeira entre contas.

- **CreateTransaction**:
  - `source_account_id`: int | None = None
  - `destination_account_id`: int | None = None
  - `type`: TransactionType
  - `amount`: float (> 0)
  - `description`: str | None = None

- **ShowTransaction**:
  - `id`: int
  - `source_account_id`: int | None = None
  - `destination_account_id`: int | None = None
  - `type`: TransactionType
  - `amount`: float (> 0)
  - `description`: str | None = None
  - `created_at`: AwareDatetime

---

## Roteadores e Serviços (Routers and Services)

### 1. Usuário (User)
- **create_user:** [POST] Criar um novo usuário.
- **read_user:** [GET] Buscar um usuário pelo id.
- **list_users:** [GET] Listar todos os usuários (pode buscar por username ou email, útil para login).
- **update_user:** [PATCH] Atualizar dados do usuário (nome, email, permissões, status, etc.).
- **delete_user:** [DELETE] Remover um usuário.

---

### 2. Conta (Account)
- **create_account:** [POST] Criar uma nova conta vinculada a um usuário.
- **read_account:** [GET] Buscar conta pelo id.
- **list_accounts:** [GET] Listar todas as contas de um usuário.
- **update_account:** [PATCH] Atualizar informações da conta.
- **delete_account:** [DELETE] Fechar/remover uma conta.

---

### 3. Transações (Transaction)
- **create_transaction:** [POST] Criar uma nova transação (saque, depósito, transferência).
- **read_transaction:** [GET] Buscar uma transação específica.
- **list_transactions:** [GET] Listar todas as transações de uma conta (com filtros: período, tipo, valor mínimo/máximo).
- **reverse_transaction:** [DELETE] Estornar/Cancelar uma transação (se permitido pelas regras).

---

### 4. Autenticação / Sessão (Auth)
- **user_login:** [POST] Login, geração de token JWT.
- **refresh_token:** [GET] Atualização de token JWT.
- **get_current_user:** [GET] Obter usuário atual usando o token JWT.
- **user_logout:** [DELETE] Logout (invalida o token, se necessário).
