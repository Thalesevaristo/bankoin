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
