# Sistema de Análise de Dados — Semana 05

Projeto do Desafio Sprint 5 de Desenvolvimento em Python. Lê um CSV, valida
e-mail, CPF, telefone e data, separa os registros válidos dos inválidos e gera
um relatório no terminal e em um arquivo TXT.

## Arquivos

- `principal.py`: leitura, funções de validação, tratamento de erros e relatório.
- `dados.csv`: oito registros fictícios para demonstrar acertos e erros.
- `relatorio.txt`: resultado da execução com o CSV de exemplo.
- `README.md`: instruções e explicação das regras.

## Como executar

É necessário ter Python 3 instalado. Não há dependências externas.
Na pasta do projeto, execute:

```bash
python3 principal.py
```

No Windows, caso o comando seja `python`, use `python principal.py`.
Por padrão, o programa lê `dados.csv` e grava `relatorio.txt` na pasta do script.
O relatório anterior é substituído a cada execução bem-sucedida.

Também é possível informar outro arquivo e outro destino:

```bash
python3 principal.py meus_dados.csv --saida minha_analise.txt
```

Caminhos informados no comando são relativos à pasta atual do terminal.
A pasta de destino deve existir. O programa impede que a saída seja o próprio
arquivo de entrada. Use `python3 principal.py --help` para consultar os argumentos.

## Formato de entrada

O CSV deve usar vírgula como separador, codificação UTF-8 e os nomes de colunas
`email`, `cpf`, `telefone` e `data`, em letras minúsculas. A ordem das colunas pode
variar. Colunas adicionais com cabeçalho são ignoradas; nomes repetidos são
rejeitados. Espaços nas extremidades dos valores são removidos antes da validação.

Exemplo de entrada:

```csv
email,cpf,telefone,data
ana@example.com,123.456.789-00,(98) 98765-4321,29/02/2024
email-invalido,222.333.444-55,(98) 98765-4321,10/09/2026
```

Cada registro só é aprovado quando os quatro campos passam na validação.
Valores vazios ou ausentes tornam o registro inválido. Valores excedentes sem
coluna correspondente também invalidam o registro. Linhas totalmente vazias são
ignoradas pelo leitor CSV e não entram na contagem.

## Validações com regex

Os padrões são raw strings e usam `re.fullmatch()` para conferir todo o valor.
A opção `re.ASCII` restringe `\d` e `\w` aos caracteres ASCII esperados.

| Campo | Regra aplicada | Justificativa |
| --- | --- | --- |
| E-mail | Usuário, `@` e domínio com extensão de pelo menos duas letras. Aceita letras, números, `_`, `+`, `-` e pontos entre partes do usuário. | Rejeita espaços, ausência de domínio e pontos consecutivos no usuário. É uma regra prática para o exercício, sem verificar a existência da conta ou cobrir todos os formatos possíveis de e-mail. |
| CPF | `r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"` | Exige o formato `000.000.000-00`. Verifica apenas a estrutura; não calcula dígitos verificadores nem consulta cadastro. |
| Telefone | `r"^\([1-9]\d\)\s?[2-9]\d{3,4}-\d{4}$"` | Exige DDD de dois dígitos entre parênteses, número de oito ou nove dígitos e hífen antes dos quatro últimos. Aceita um espaço em branco opcional após o DDD. Não consulta se o DDD ou a linha existem. |
| Data | `r"^\d{2}/\d{2}/\d{4}$"` e `datetime.strptime()` | Exige `DD/MM/AAAA` e uma data existente no calendário, incluindo a regra de ano bissexto. |

No código, `^` e `$` indicam início e fim, `\d` representa dígitos, `\w`
representa letras, dígitos e sublinhado, e `\s` representa espaço em branco.
Quantificadores como `{3}`, `{3,4}`, `+` e `?` controlam a quantidade de caracteres.
O ponto literal do CPF é escrito como `\.` e os parênteses do telefone como
`\(` e `\)`.

Os CPFs do exemplo são fictícios e servem somente para testar o formato.

## Tratamento de exceções

| Exceção | Situação e tratamento |
| --- | --- |
| `FileNotFoundError` | O arquivo de entrada não existe. Exibe o caminho e encerra com uma mensagem. |
| `KeyError` | Falta uma coluna obrigatória. Informa o nome da coluna, inclusive em um CSV sem registros. Um arquivo totalmente vazio também é rejeitado por não ter cabeçalho. |
| `ValueError` | A conversão de texto para data falha, por exemplo em `31/02/2026`. Registra o motivo e continua com as próximas linhas. Também impede usar a entrada como destino do relatório. |
| `FormatoInvalidoError` | Exceção personalizada que herda de `Exception`. Reúne os problemas de um registro que não atende às regras e o inclui entre os inválidos. Também rejeita cabeçalhos repetidos. |
| `UnicodeError` | O arquivo não pode ser decodificado como UTF-8. Orienta a corrigir a codificação. |
| `csv.Error` | O leitor identifica uma estrutura CSV malformada. Interrompe a análise com uma mensagem. |
| `OSError` | Falta de permissão ou outro problema de leitura e escrita. Exibe a falha; se a gravação falhar, o relatório ainda pode ser consultado no terminal. |

A leitura e a escrita utilizam `with open(..., encoding="utf-8")`, que fecha os
arquivos automaticamente. O `try` delimita as operações que podem falhar e os
blocos `except` tratam cada situação. O `else` processa o resultado quando o bloco
`try` termina sem exceções. O `finally` imprime `Processamento encerrado.` tanto
no sucesso quanto nas falhas tratadas durante a análise e a gravação.

Erros nos campos não interrompem a leitura dos demais registros. Erros no arquivo
ou no cabeçalho impedem a geração de um novo relatório. Nesse caso, um relatório
de uma execução anterior, se existir, permanece no disco.

O código de saída é `0` quando a análise e a gravação terminam, mesmo havendo
registros inválidos, e `1` nas falhas tratadas de processamento. Erros nos argumentos
do comando são tratados pelo `argparse` antes da análise.

## Exemplo de saída

Ao executar com os oito registros de `dados.csv`, o resumo é:

```text
RELATÓRIO DE ANÁLISE DE DADOS
============================================================
Total de registros: 8
Registros válidos: 3
Registros inválidos: 5
Percentual de aprovação: 37.50%
```

O relatório completo contém os quatro campos de cada registro, separados em
`DADOS VÁLIDOS` e `DADOS INVÁLIDOS`. Para os inválidos, também apresenta os motivos:

```text
Registro 7: e-mail=fabio@example.com | CPF=444.555.666-77 | telefone=(98) 98765-4321 | data=31/02/2026
Motivos: Data inexistente no calendário
```

Os números identificam a ordem dos registros lidos, sem contar o cabeçalho.
O relatório usa f-strings para inserir os dados e formatar o percentual com duas
casas decimais. Um CSV apenas com cabeçalho gera total zero e percentual `0.00%`.

## Entrega no GitHub

Envie os quatro arquivos deste projeto para o repositório da atividade e deixe-o
público ou com acesso liberado para o avaliador.
