def gerar_proxima_versao(versao_atual: str) -> str:
    """
    Gera a próxima versão de um software a partir da versão atual.

    A lógica de versionamento é a seguinte:
    - Incrementa o número menor (ex: de "1.0" para "1.1").
    - Quando o número menor chega a 10, ele é zerado e o número
      maior é incrementado (ex: de "1.10" para "2.0").

    Args:
        versao_atual: A string da versão atual (formato "maior.menor").

    Returns:
        A string da próxima versão.
        
    Raises:
        ValueError: Se o formato da versão for inválido.
    """
    try:
        maior, menor = map(int, versao_atual.split('.'))
    except ValueError:
        raise ValueError("Formato de versão inválido. Use o formato 'maior.menor', ex: '1.0'")

    # Incrementa a versão menor
    menor += 1

    # Se a versão menor chegar a 11 (pois contamos a partir de .1 até .10),
    # reseta a menor para 0 e incrementa a maior.
    if menor > 10:
        menor = 0
        maior += 1

    return f"{maior}.{menor}"