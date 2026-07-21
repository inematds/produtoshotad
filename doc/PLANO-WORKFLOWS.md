# PLANO — 3 Workflows de Produção de Anúncios (produtoshotad)

> **Para o executor (Opus/Sonnet):** este documento é a análise + plano de implementação.
> Leia primeiro `doc/CLAUDE.md`, depois este arquivo inteiro, e execute a seção
> "Tarefas de implementação" na ordem. As regras não-negociáveis de `doc/CLAUDE.md`
> e `doc/product-consistency.md` valem para os 3 workflows, sem exceção.

## 1. Análise do estado atual

O projeto `produtoshotad` transforma **1 foto real de produto** em **5 imagens de anúncio
+ 5 vídeos curtos (9:16, ~30s)**, em duas avenidas (Fully Automated + QA / AI-Assisted).

Arquivos existentes em `doc/`:

| Arquivo | Papel |
|---|---|
| `CLAUDE.md` | Playbook mestre: regras, batch 3+2 stills / 3+2 vídeos |
| `ad-pipeline.md` | Sequenciamento: hero → variações → cenas i2v → montagem → voz |
| `product-consistency.md` | Anti-drift: referência travada em TODA chamada, QA obrigatório |
| `fal-setup.md` | Mecânica Fal.ai/Seedance (auth FAL_KEY, upload CDN, i2v submit/poll) |
| `elevenlabs-setup.md` | Mecânica ElevenLabs TTS |
| `HyperFrames Production SKILL.md` | Padrões de produção HyperFrames (GSAP, shaders, easing) |

**Lacunas:** não há código, `.env.example`, nem estrutura de pastas (`products/`, `output/`);
o pipeline original depende de APIs pagas (Fal, ElevenLabs).

**API keys (verificado em 2026-07-21):** `AGNES_API_KEY` e `ELEVENLABS_API_KEY` existem em
`~/projetos/openpcbot/.env` — carregar em runtime de lá (nunca copiar/imprimir valores).
`FAL_KEY` existe em `~/projetos/wifi/.env` (adicionada em 2026-07-21) — worker 3 desbloqueado.

## 2. Os 3 workflows (workers)

Padrão de nomes do projeto: arquivos-skill em kebab-case com frontmatter `name`/`description`
(como `ad-pipeline`, `product-consistency`). Os workers seguem o mesmo padrão:

### Worker 1 — `ad-pipeline-agnes` (custo US$ 0, só imagens + Agnes)

- **Escopo:** apenas produção de **imagens** (as 5 stills: 3 plain + 2 copy-overlay).
- **Gerador:** Agnes AI `agnes-image-2.1-flash` via `apihub.agnes-ai.com` — reusar o
  cliente pronto `~/projetos/imagens-agnes/gerar.py` (suporta `--ref` para img2img).
  Chave: `AGNES_API_KEY` (buscar em `~/projetos/videos-agnes` / `~/projetos/imagens-agnes` .env).
- **Regras Agnes medidas na prática** (de `~/projetos/videos-agnes/README.md`):
  prompts **em inglês**; **máx. 2 imagens de referência** por chamada (usar hero + 1 crop,
  não o set inteiro — adaptação necessária do product-consistency); retry com backoff
  (~34% de 503); 1K para volume; baixar o PNG na hora (URL temporária).
- **Voz (só se precisar):** TTS local **Kokoro** (`kokoro_onnx` 0.5.0 já instalado no
  sistema; verificar presença dos arquivos de modelo `kokoro-v1.0.onnx` + `voices-v1.0.bin`
  e baixá-los se ausentes). Sem ElevenLabs neste worker.
- **Sem vídeo.** Se o usuário pedir vídeo dentro deste worker, encaminhar ao worker 2 ou 3.

### Worker 2 — `ad-pipeline-hyperframes` (imagens + HyperFrames + Remotion, SEM gerador de vídeo IA)

- **Escopo:** os 5 vídeos são construídos **animando as stills** — nada de Seedance/Kling/
  Agnes-video. Motion design determinístico: HTML/CSS/GSAP via **HyperFrames**
  (skill `hyperframes` + `HyperFrames Production SKILL.md`) e, quando composição React
  for mais adequada, **Remotion** (skill `remotion` / `remotion-best-practices`).
- **Entrada:** as 5 stills aprovadas (de qualquer worker de imagem) + fotos de referência.
- **Técnicas:** Ken Burns/parallax nas stills, glass cards, typewriter para copy,
  cut-the-curve transitions, captions — tudo do catálogo do
  `HyperFrames Production SKILL.md`. Saída 1080x1920 (9:16), ~30s, MP4.
- **Voz:** Kokoro local (mesma mecânica do worker 1) ou ElevenLabs se o usuário pedir.
- **QA:** como as stills não são re-geradas, o checkpoint de consistência roda 1× nas
  stills de entrada e 1× no vídeo final (copy legível, produto não distorcido por zoom/crop).

### Worker 3 — `ad-pipeline` (orientação original do projeto)

- **Escopo:** o pipeline completo conforme `doc/CLAUDE.md` + `doc/ad-pipeline.md`:
  Fal.ai/**Seedance** para stills e image-to-video, **ElevenLabs** para voz,
  **HyperFrames** para a montagem da avenida automatizada, CapCut/Premiere na assistida.
- Mecânica em `doc/fal-setup.md` (já presente); `FAL_KEY` em `~/projetos/wifi/.env`.

## 3. Tarefas de implementação (ordem de execução)

1. **Estrutura:** criar `products/` (fotos de entrada), `output/{stills,videos,voz}/`,
   `scripts/`, `.env.example` (`AGNES_API_KEY`, `FAL_KEY`, `ELEVENLABS_API_KEY`),
   `.gitignore` (output/, .env, __pycache__).
2. **Worker 1:** escrever `doc/ad-pipeline-agnes.md` (skill com frontmatter) +
   `scripts/agnes_stills.py` (wrapper de `imagens-agnes/gerar.py` com retry/backoff,
   máx. 2 refs, QA gate) + `scripts/kokoro_tts.py` (opcional, só quando houver voz).
3. **Worker 2:** escrever `doc/ad-pipeline-hyperframes.md` + template de composição
   HyperFrames 9:16 (uma cena por still, 5–6s cada) e alternativa Remotion; script de
   render/concat (ffmpeg) até o MP4 final.
4. **Worker 3:** revisar `ad-pipeline.md` para apontar para os workers 1 e 2 como lanes alternativas
   ("lane $0" e "lane sem-vídeo-IA").
5. **CLAUDE.md:** adicionar seção "Escolha de worker" — como rotear o pedido do usuário
   para 1, 2 ou 3 (custo zero → 1; sem IA de vídeo / determinístico → 2; qualidade
   máxima paga → 3).
6. **Teste de fumaça por worker:** 1 still Agnes de um produto de `products/`;
   1 clipe HyperFrames de 5s de uma still; 1 chamada Seedance (se `FAL_KEY` existir —
   senão marcar como pendente, não bloquear).
7. **Publicação:** commit + push no repo público `inematds/produtoshotad`
   (autor/committer `inematds <inematds@gmail.com>`). Trabalho termina no push.

## 4bis. Status de implementação (2026-07-21)

Tarefas 1–5 concluídas: estrutura de pastas, `.env.example`, `scripts/agnes_stills.py`,
`scripts/kokoro_tts.py`, `doc/ad-pipeline-agnes.md`, `scripts/hyperframes-still-scene.template.html`,
`doc/ad-pipeline-hyperframes.md`, `ad-pipeline.md` e `CLAUDE.md` atualizados com o roteamento
de worker.

**Teste de fumaça (tarefa 6):** `AGNES_API_KEY`, `FAL_KEY` e `ELEVENLABS_API_KEY` carregam
corretamente dos `.env` (sem imprimir valores). Kokoro TTS gerou áudio local com sucesso
(`output/voz/smoke-test.wav`). **Não executado** por falta de insumo real: geração de still
via Agnes (precisa de uma foto real de produto em `products/`) e chamada Seedance (custo real,
requer pedido explícito e produto real). Rodar esses dois quando houver uma foto de produto.

## 4. Regras transversais (valem para os 3)

- Referência travada re-anexada em toda geração (adaptada a 2 refs no Agnes).
- QA checkpoint antes de avançar de estágio — nunca pular em silêncio.
- Prompts curtos, 1 variável por geração, unchanged-clause explícita, em inglês no Agnes.
- Script/voz só depois das cenas travadas.
- Split 3 automatizados / 2 manuais decidido **depois** de ver a saída automatizada.
- Nunca imprimir valores de API keys; carregar em runtime dos .env já existentes.
