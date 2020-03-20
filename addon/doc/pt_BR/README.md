# Anúncio de horas em diferentes fusos horários

## Informações
* Autor: "Munawar"
* Descarregar a [versão estável: ][1]
* Compatibilidade: NVDA versão 2019.2 até 2020.1

## Introdução
Um extra para o NVDA para anunciar a hora e data em fusos horários seleccionados.

Desde há muito tempo que o Windows permite visualizar relógios para diferentes fusos horários. Quando os utilizadores configuram estes relógios, eles ficam imediatamente visíveis.
Infelizmente, para utilizadores de leitores de ecrã, como o NVDA] (https://www.nvaccess.org/) ou o [Jaws](http://www.freedomscientific.com), não há uma maneira simples de ler essa informação.
Os leitores de ecrã não suportam relógios adicionais, pelo que os utilizadores de leitores de ecrã têm de utilizar outras soluções, algumas delas pagas.

Uma parte do trabalho que eu faço implica trabalhar em vários fusos horários, e, eventualmente, canso-me de calcular manualmente os horários na minha cabeça, eespecialmente nos casos em que as diferenças incluem meia-hora, como a Índia, que tem uma diferença de +5:30 em relação ao UTC.

Por isso, criei este extra para o NVDA.
O extra permite ouvir as horas nos diferentes fusos horários seleccionados através do "Anel de fusos horários".

## Uso
Após instalar o extra, abra o menu do NVDA, vá para ""Preferências", depois para "Anúncio de horas em diferentes fusos horários", e por fim pressione Enter em "Configurar o anel de fusos horários...".

Será aberta a janela para configurar os fusos horários que quer ouvir.
Marque os itens na lista de fusos horários para os adicionar ao seu "Anel de fusos horários". Desmarque, ou pressione o botão "Remover" para remover um fuso horário adicionado.
Também pode reordenar os vários fusos horários no anel com os botões "Mover para cima" ou "Mover para baixo".
Use o campo "Filtrar" para restringir a pesquisa.
Marque a caixa de verificação "Anunciar fusos horários abreviados" para ouvir a designação abreviada dos fusos horários, como IST or GMT, ou desmarque para ouvir o nome completo, como "Asia/Kolkata" ou "Europe/London".
Para terminar a configuração, pressione o botão "Guardar".

Agora, pode pressionar "NVDA+Alt+t" para ouvir a hora e data nos fusos horários configurados no anel.

Quando o extra é instalado, é definido como padrão o seu fuso horário, se possível.


## Histórico de versões

### Versão 1.01, lançada em 12/03/2020
* A hora e data passam a ser anunciadas na configuração regional do utilizador, sendo assim respeitada a configuração de 12 ou 24 horas.
* O NVDA anunciará o fuso horário abreviadamente, ou não, dependendo da marcação da respectiva caixa de verificação na janela "Configurar o anel de fusos horários". Por exemplo, anunciará "Europe/London," ou "GMT" ou BST.
* O extra passa a incluir comentários para os tradutores. (@ruifontes.)
* O extra já inclui no código os cabeçalhos. (@ruifontes.)
* A tecla "Escape" fecha a janela "Configurar o anel de fusos horários". (@ruifontes.)
* O item de menu para abrir a janela "Configurar o anel de fusos horários" é nomeado apropriadamente. (@ruifontes.)
* O extra passa a assumir como padrão o fuso horário local, se disponível.
* Suporte para múltiplos fusos horários através do "Anel de fusos horários".
* O comando passa a ser "NVDA+Alt+t", para não haver conflitos com o extra "Relógio".
* O diálogo "Selector de fuso horário" passa a ter um campo para filtrar os resultados, e o NVDA vai anunciando o número de resultados enquanto se escreve.
* Suporte ao Python 3
* O anúncio da hora e data é agora feito numa sequência separada para prevenir problemas no NVDA, caso o processamento demore muito tempo. .
* O diálogo "Selector de fuso horário" passa a ter um botão "Cancelar" e já não impede o NVDA de fechar.

[1]: https://github.com/munawarb/NVDA-Time-Zoner/releases/latest