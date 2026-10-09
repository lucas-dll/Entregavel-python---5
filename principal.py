"""Sistema de análise de dados — Entregável Python, Semana 05."""

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path


CAMPOS = ("email", "cpf", "telefone", "data")
PASTA = Path(__file__).resolve().parent


class FormatoInvalidoError(Exception):
    """Indica que um registro não atende às regras de validação."""


def validar_email(valor):
    padrao = r"^[\w+-]+(?:\.[\w+-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return re.fullmatch(padrao, valor, flags=re.ASCII) is not None


def validar_cpf(valor):
    return re.fullmatch(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", valor, re.ASCII) is not None


def validar_telefone(valor):
    padrao = r"^\([1-9]\d\)\s?[2-9]\d{3,4}-\d{4}$"
    return re.fullmatch(padrao, valor, re.ASCII) is not None


def validar_data(valor):
    if re.fullmatch(r"^\d{2}/\d{2}/\d{4}$", valor, re.ASCII) is None:
        return False
    # A conversão também rejeita datas impossíveis, como 31/02/2024.
    datetime.strptime(valor, "%d/%m/%Y")
    return True


def validar_registro(registro):
    erros = []
    if None in registro:
        erros.append("Quantidade de valores maior que a de colunas")
    if not validar_email(registro["email"]):
        erros.append("E-mail fora do formato usuario@dominio.com")
    if not validar_cpf(registro["cpf"]):
        erros.append("CPF fora do formato 000.000.000-00")
    if not validar_telefone(registro["telefone"]):
        erros.append("Telefone fora do formato (98) 98765-4321 ou (98) 3456-7890")
    try:
        data_valida = validar_data(registro["data"])
    except ValueError:
        erros.append("Data inexistente no calendário")
    else:
        if not data_valida:
            erros.append("Data fora do formato DD/MM/AAAA")
    if erros:
        raise FormatoInvalidoError("; ".join(erros))


def analisar_arquivo(caminho):
    validos = []
    invalidos = []
    with open(caminho, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        colunas = leitor.fieldnames or []
        for campo in CAMPOS:
            if campo not in colunas:
                raise KeyError(campo)
        if len(colunas) != len(set(colunas)):
            raise FormatoInvalidoError("O cabeçalho contém colunas repetidas")

        for numero, linha in enumerate(leitor, start=1):
            registro = {
                campo: (linha[campo] or "").strip() for campo in CAMPOS
            }
            if None in linha:
                registro[None] = linha[None]
            try:
                validar_registro(registro)
            except FormatoInvalidoError as erro:
                invalidos.append((numero, registro, str(erro)))
            else:
                validos.append((numero, registro))
    return validos, invalidos


def formatar_registro(numero, registro):
    return (
        f"Registro {numero}: e-mail={registro['email']} | "
        f"CPF={registro['cpf']} | telefone={registro['telefone']} | "
        f"data={registro['data']}"
    )


def gerar_relatorio(validos, invalidos):
    total = len(validos) + len(invalidos)
    percentual = len(validos) / total * 100 if total else 0
    linhas = [
        "RELATÓRIO DE ANÁLISE DE DADOS",
        "=" * 60,
        f"Total de registros: {total}",
        f"Registros válidos: {len(validos)}",
        f"Registros inválidos: {len(invalidos)}",
        f"Percentual de aprovação: {percentual:.2f}%",
        "",
        "DADOS VÁLIDOS",
    ]
    for numero, registro in validos:
        linhas.append(formatar_registro(numero, registro))
    if not validos:
        linhas.append("Nenhum registro válido.")
    linhas.extend(["", "DADOS INVÁLIDOS"])
    for numero, registro, motivo in invalidos:
        linhas.append(formatar_registro(numero, registro))
        linhas.append(f"Motivos: {motivo}")
    if not invalidos:
        linhas.append("Nenhum registro inválido.")
    return "\n".join(linhas) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Valida dados de um arquivo CSV.")
    parser.add_argument("arquivo", nargs="?", type=Path, default=PASTA / "dados.csv")
    parser.add_argument("--saida", type=Path, default=PASTA / "relatorio.txt")
    args = parser.parse_args()

    try:
        if args.arquivo.resolve() == args.saida.resolve():
            raise ValueError("A saída deve ser diferente do arquivo de entrada")
        if args.saida.exists() and args.arquivo.exists():
            if args.arquivo.samefile(args.saida):
                raise ValueError("A saída aponta para o mesmo arquivo de entrada")
        validos, invalidos = analisar_arquivo(args.arquivo)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {args.arquivo}")
        return 1
    except KeyError as erro:
        print(f"Coluna obrigatória ausente no CSV: {erro.args[0]}")
        return 1
    except UnicodeError:
        print("Não foi possível ler o arquivo. Salve o CSV com codificação UTF-8.")
        return 1
    except (ValueError, FormatoInvalidoError, csv.Error) as erro:
        print(f"Erro nos dados: {erro}")
        return 1
    except OSError as erro:
        print(f"Erro ao abrir ou ler o arquivo: {erro}")
        return 1
    else:
        relatorio = gerar_relatorio(validos, invalidos)
        print(relatorio, end="")
        try:
            with open(args.saida, "w", encoding="utf-8") as arquivo:
                arquivo.write(relatorio)
        except OSError as erro:
            print(f"Erro ao salvar o relatório: {erro}")
            return 1
        else:
            print(f"\nRelatório salvo em: {args.saida}")
            return 0
    finally:
        print("Processamento encerrado.")


if __name__ == "__main__":
    raise SystemExit(main())
