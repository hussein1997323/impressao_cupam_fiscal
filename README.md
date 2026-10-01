# Teste da Bematech MP-4200 HS

Aplicativo simples para enviar um cupom de teste diretamente para a porta serial da impressora, sem depender da fila de impressão do Windows.

## Como executar

1. Conecte e ligue a impressora.
2. Execute `executar.cmd`.
3. Na tela, selecione a porta da impressora. A configuração inicial é `COM12` e `9600` bps.
4. Clique em **Testar conexão**.
5. Clique em **Imprimir teste**.

Na primeira execução, o iniciador instala automaticamente a biblioteca `pyserial`.

## Erro de porta ocupada

Se a mensagem informar que a porta está ocupada, feche a fila de impressão e qualquer sistema que esteja usando a impressora. Filas antigas do Windows ligadas à mesma COM também podem manter a porta bloqueada.
