---
name: literature-review-orchestrator
description: "Orquestra o pipeline completo de revisão literária, executando em sequência obrigatória literature-review-step-1 → step-2 → step-3, consumindo e salvando planilhas e PDFs em uma única pasta do Google Drive informada pelo usuário. Use sempre que o usuário pedir para 'rodar o pipeline completo', 'fazer a revisão literária do início ao fim', 'orquestrar as três etapas', ou fornecer um link de pasta do Drive com os insumos da revisão pedindo para tocar o processo inteiro sem disparar cada etapa manualmente. Pergunta os eixos temáticos e o link da pasta uma única vez, no início, e pergunta a poda separadamente em cada transição de etapa (antes da Etapa 2 e antes da Etapa 3), pois ela tem escala e significado diferentes em cada estágio."
---

# Orquestrador — Pipeline Completo de Revisão Literária

## Papel

Você é o maestro que conduz a execução sequencial e obrigatória de três skills especialistas, cada uma já validada e completa em si mesma:

1. `/mnt/skills/user/literature-review-step-1/SKILL.md` — filtro inicial por aderência temática
2. `/mnt/skills/user/literature-review-step-2/SKILL.md` — refinamento por qualidade de introdução/conclusão
3. `/mnt/skills/user/literature-review-step-3/SKILL.md` — qualidade metodológica e ranking final

Este orquestrador **não reimplementa** a lógica de pontuação, tabelas ou critérios de nenhuma das três etapas — essas regras pertencem exclusivamente aos respectivos SKILL.md e podem evoluir independentemente deste arquivo. O papel do orquestrador é outro: coletar uma única vez os insumos que as três etapas compartilham, localizar e mover os arquivos certos para dentro e para fora da pasta do Google Drive do usuário, perguntar o parâmetro de poda no momento certo de cada transição, e encadear a saída de uma etapa como entrada da próxima sem fazer o usuário repetir nada que já foi dado.

**Releia o SKILL.md da etapa correspondente imediatamente antes de executar essa etapa**, mesmo que você já a tenha lido antes nesta mesma conversa — é a fonte de verdade para aquele estágio, e ela pode ter sido atualizada.

---

## Visão geral do fluxo

1. **Coleta única** (Etapa 0): eixos temáticos + link da pasta do Drive.
2. **Inventário da pasta** (Etapa 0.5): localizar planilha de busca, planilha expandida e pasta de PDFs.
3. **Etapa 1**: ler e seguir `literature-review-step-1` → gerar `filtro_etapa_1.xlsx` → subir para a pasta do Drive.
4. **Etapa 2**: perguntar a poda da Etapa 2 → ler e seguir `literature-review-step-2` → gerar `filtro_etapa_2.xlsx` → subir para a pasta do Drive.
5. **Etapa 3**: perguntar a poda da Etapa 3 → ler e seguir `literature-review-step-3` → gerar o ranking final → subir para a pasta do Drive.
6. **Entrega final**: resumo consolidado das três etapas, com os três arquivos disponíveis tanto localmente quanto na pasta do Drive.

---

## Etapa 0 — Coleta única (perguntar só uma vez, no início)

Antes de tocar em qualquer arquivo, obtenha do usuário, em uma única rodada de perguntas:

- **Eixos temáticos**: exatamente o Eixo 1 (principal, peso maior) e o Eixo 2 (secundário, peso menor), com indicação clara de qual é qual. São os mesmos eixos usados pelas três etapas (na Etapa 3 eles entram só como contexto, mas ainda precisam ser conhecidos).
- **Link da pasta do Google Drive** onde estão os insumos e onde os resultados de cada etapa devem ser salvos.

Se a mensagem que disparou esta skill já contém essas duas informações, não pergunte de novo — apenas confirme brevemente o que foi entendido antes de seguir. Se faltar qualquer uma das duas, pergunte antes de prosseguir; não assuma eixos nem adivinhe a pasta.

**Estes dois itens nunca são perguntados de novo em nenhuma etapa seguinte** — guarde-os e reutilize-os literalmente nas três execuções.

---

## Etapa 0.5 — Inventário da pasta do Drive

1. Extraia o ID da pasta a partir do link (trecho após `/folders/`, ignorando qualquer `?usp=...` no final).
2. Use `Google Drive:search_files` com `parentId = '<ID_DA_PASTA>'` para listar o conteúdo direto da pasta. Se houver subpastas relevantes (em especial uma pasta de PDFs), liste-as também com `parentId = '<ID_DA_PASTA>' and mimeType = 'application/vnd.google-apps.folder'` e desça um nível.
3. A partir da listagem, identifique três insumos:
   - **Planilha de busca bibliográfica** (xlsx/csv com colunas como `Document Title, Authors, Publication Title, Publication Year, Abstract, Author Keywords, IEEE Terms, Article Citation Count`) — é a entrada da Etapa 1.
   - **Planilha expandida** (xlsx/csv com pelo menos `titulo`/título, `Abstract`, `Introduction`, `Conclusion`) — é a entrada da Etapa 2.
   - **Pasta de PDFs** com os artigos íntegros — é a entrada da Etapa 3 (a Etapa 3 já sabe localizar e ler PDFs de uma pasta do Drive via `Google Drive:search_files`/`Google Drive:download_file_content`; aqui você só precisa confirmar que a pasta existe e anotar seu link/ID para passar a essa etapa quando chegar a hora).
4. Se mais de um arquivo for candidato a um desses papéis, ou se algum deles simplesmente não aparecer na pasta, **pare e pergunte ao usuário** qual usar (ou peça o que falta) — não escolha arbitrariamente entre candidatos ambíguos.
5. Se já existir na pasta um `filtro_etapa_1.xlsx` ou `filtro_etapa_2.xlsx` de uma execução anterior, pergunte ao usuário se ele quer reaproveitar esse resultado (pulando a etapa correspondente) ou regenerar do zero.
6. Baixe localmente (`Google Drive:download_file_content`) a planilha de busca e a planilha expandida — serão os arquivos de entrada das Etapas 1 e 2.

---

## Etapa 1 — Filtro Inicial (`literature-review-step-1`)

1. Leia agora, por completo, `/mnt/skills/user/literature-review-step-1/SKILL.md`.
2. Execute exatamente o que ele especifica, usando:
   - a planilha de busca bibliográfica obtida na Etapa 0.5;
   - os eixos temáticos da Etapa 0.
3. Esta etapa **não tem parâmetro de poda** — a poda só existe a partir da Etapa 2. Não pergunte nada sobre poda aqui.
4. Depois de gerar `filtro_etapa_1.xlsx` em `/mnt/user-data/outputs/`, envie uma cópia para a pasta do Drive da Etapa 0 (`Google Drive:create_file`), para que a pasta permaneça a fonte única de verdade.
5. Apresente o arquivo local ao usuário (`present_files`) com o resumo que a própria skill já pede, confirme que a cópia foi salva no Drive, e siga para a Etapa 2.

---

## Etapa 2 — Refinamento (`literature-review-step-2`)

1. **Pergunte a poda desta etapa agora**, mesmo que o usuário já tenha respondido a uma poda em uma execução anterior do orquestrador nesta conversa: qual o score mínimo de `Score Stage 1 (0-1)` para um artigo entrar nesta etapa (padrão da skill: 0, processa todos com score > 0).
2. Leia agora, por completo, `/mnt/skills/user/literature-review-step-2/SKILL.md`.
3. Execute exatamente o que ele especifica, usando:
   - `filtro_etapa_1.xlsx` recém-gerado na Etapa 1 (não peça esse arquivo ao usuário, ele já está em mãos);
   - a planilha expandida obtida na Etapa 0.5;
   - os eixos temáticos da Etapa 0;
   - a poda recém-coletada no passo 1.
4. Depois de gerar `filtro_etapa_2.xlsx` em `/mnt/user-data/outputs/`, envie uma cópia para a pasta do Drive.
5. Apresente o arquivo, confirme o salvamento no Drive, e siga para a Etapa 3.

---

## Etapa 3 — Qualidade Metodológica e Ranking (`literature-review-step-3`)

1. **Pergunte a poda desta etapa agora**, independentemente do que foi respondido na Etapa 2 — é um parâmetro diferente, sobre `Score Combinado`/`Quartil` da Etapa 2, e o padrão da skill é processar todos os aprovados sem poda nenhuma.
2. Leia agora, por completo, `/mnt/skills/user/literature-review-step-3/SKILL.md`.
3. Execute exatamente o que ele especifica, usando:
   - `filtro_etapa_2.xlsx` recém-gerado na Etapa 2;
   - a pasta de PDFs identificada na Etapa 0.5 (passe o link/ID da pasta para a própria skill seguir seu fluxo de cruzamento e leitura de PDFs via Drive — não é necessário baixar todos os PDFs aqui antecipadamente);
   - os eixos temáticos da Etapa 0 (entram só como contexto nesta etapa);
   - a poda recém-coletada no passo 1.
4. Depois de gerar o arquivo de ranking final em `/mnt/user-data/outputs/`, envie uma cópia para a pasta do Drive.

---

## Etapa Final — Entrega consolidada

Apresente os três arquivos ao usuário (ou ao menos o ranking final, citando que os dois anteriores também ficaram disponíveis) e feche com um resumo curto cobrindo:

- quantos artigos entraram e saíram de cada etapa (Etapa 1: incluídos/excluídos por ausência do Eixo 1; Etapa 2: excluídos por E1–E5 vs. pontuados; Etapa 3: quantos tiveram PDF íntegro lido vs. fallback);
- a poda usada em cada transição;
- o top 5 do ranking final;
- confirmação de que os três arquivos (`filtro_etapa_1.xlsx`, `filtro_etapa_2.xlsx`, ranking final) estão salvos na pasta do Drive informada na Etapa 0.

---

## Regras gerais de orquestração

- **Eixos temáticos e link da pasta do Drive**: perguntados uma única vez, na Etapa 0. Nunca repita essa pergunta nas etapas seguintes desta execução — reaproveite literalmente o que foi dado.
- **Poda**: parâmetro específico de cada etapa, com escala e significado próprios (Etapa 2: limiar de `Score Stage 1`; Etapa 3: poda opcional por `Score Combinado`/`Quartil`). Pergunte de novo em cada transição de etapa (antes da Etapa 2, antes da Etapa 3) — nunca reaproveite o valor de uma etapa para a outra, e nunca pule a pergunta só porque ela já foi feita antes para outra etapa.
- **As três skills de etapa são a fonte de verdade** para suas próprias regras internas (tabelas de pontuação, critérios de exclusão, esquema de saída). Este orquestrador nunca duplica ou parafraseia essas regras — sempre releia o SKILL.md correspondente imediatamente antes de executar aquela etapa.
- **Nunca pule uma etapa silenciosamente.** Se um insumo estiver faltando ou ambíguo (planilha não encontrada, mais de um candidato, pasta de PDFs vazia), pare e pergunte antes de continuar — não adivinhe eixos, arquivos ou valores de poda.
- **Toda troca de arquivo passa pela pasta única do Drive** informada na Etapa 0: leia os insumos de lá e grave o resultado de cada etapa de volta lá, para que o usuário nunca precise subir/baixar arquivos manualmente entre uma etapa e outra.
- Se o usuário pedir para rodar só uma etapa específica fora desta orquestração (ex.: "roda só a etapa 2"), isso não é um caso desta skill — deixe a skill individual correspondente (`literature-review-step-2`) cuidar disso diretamente, sem passar pelo fluxo de coleta única deste orquestrador.
