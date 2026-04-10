# Aurea — Spec-Driven Development Specification

> **Apresentações que brilham.**
>
> Toolkit open-source para gerar apresentações HTML fascinantes via comandos em agentes AI.
> Inspirado no [GitHub Spec Kit](https://github.com/github/spec-kit), focado exclusivamente em apresentações.

---

## 1. Visão geral do produto

### 1.1 Problema

Criar apresentações de alta qualidade visual com agentes AI hoje é um processo ad-hoc: o desenvolvedor pede "crie uma apresentação sobre X", recebe um Markdown genérico sem design system, sem narrativa estruturada e sem output portável. Não existe um workflow estruturado que guie o agente desde a concepção da narrativa até um HTML standalone publicável.

### 1.2 Solução

Aurea é um toolkit que fornece:

1. **CLI portável** para scaffolding, build e gestão de temas
2. **Prompt templates estruturados** que guiam agentes AI através de um workflow de criação de apresentações em fases (outline → generate → refine → visual → build)
3. **Biblioteca de temas** baseados em DESIGN.md — design systems reais extraídos de sites reconhecidos (Apple, Stripe, Linear, etc.), prontos para uso
4. **Extração de temas** de qualquer URL pública via webscraping + interpretação AI
5. **Output HTML standalone** baseado em reveal.js — zero dependências externas no arquivo final

### 1.3 Público-alvo

- Desenvolvedores e tech leads que usam agentes AI (Claude Code, Gemini CLI, ChatGPT, Devin.ai, Windsurf) no dia a dia
- Ambiente primário: **Windows corporativo (~80% dos usuários)**, com suporte a Mac/Linux
- Nível técnico: confortável com terminal mas sem expectativa de instalar toolchains complexos

### 1.4 Princípios de design

- **Portabilidade acima de tudo** — funcionar no maior número de ambientes com o mínimo de fricção
- **Templates são o produto** — a CLI é conveniência, os prompts são o valor real
- **Output autossuficiente** — o HTML gerado deve abrir em qualquer browser, offline, sem servidor
- **Progressivo** — funcionar desde "copiar templates manualmente" até "CLI completa com temas e live preview"

---

## 2. Modos de funcionamento (estratégia de portabilidade)

O Aurea suporta **quatro modos de instalação/uso**, do mais simples ao mais completo. Cada modo é autossuficiente — o usuário escolhe o que funciona no seu ambiente.

### 2.1 Modo 1 — Zero-install (copy & paste)

**Quando usar:** Ambientes altamente restritivos onde nada pode ser instalado; máquinas corporativas bloqueadas; experimentação rápida.

**Como funciona:**

1. Usuário baixa o ZIP do release (ou clona o repo)
2. Copia manualmente o diretório `commands/<agent>/` para o diretório de comandos do seu agente AI
3. Cria slides em Markdown seguindo o template
4. Usa o comando `/aurea.build` que instrui o agente a gerar o HTML final inline (o agente monta o reveal.js + CSS + conteúdo num único arquivo)

**Limitações:**

- Sem gestão de temas automatizada (usa tema default embutido no template)
- Sem live preview
- Build depende do agente gerar o HTML completo (funciona, mas é mais lento e consome mais tokens)
- Sem versionamento de builds
- Extração de temas (`/aurea.extract`) funciona via web fetch nativo do agente, sem CLI

**Estrutura entregue:**

```
aurea-templates/
├── commands/
│   ├── claude/
│   │   ├── aurea.outline.md
│   │   ├── aurea.generate.md
│   │   ├── aurea.refine.md
│   │   ├── aurea.visual.md
│   │   ├── aurea.theme.md
│   │   ├── aurea.extract.md
│   │   └── aurea.build.md
│   ├── gemini/           # formato .toml
│   ├── copilot/          # formato .agent.md
│   ├── windsurf/         # formato .md
│   └── devin/            # formato .md
├── themes/
│   ├── registry.json     # Índice com metadados de todos os temas
│   ├── default/
│   │   ├── DESIGN.md     # Design system completo (lido pelo agente AI)
│   │   ├── theme.css     # CSS compilado para reveal.js (usado pelo build)
│   │   ├── layout.css    # Grid, animações, transições
│   │   └── meta.json     # Metadados resumidos para busca
│   ├── apple/
│   ├── stripe/
│   ├── linear/
│   └── ... (40+ temas)
├── templates/
│   └── slide-template.md
└── README.md
```

### 2.2 Modo 2 — Script portável (Python zipapp)

**Quando usar:** Ambientes onde Python 3.8+ está disponível (já vem no Windows 10/11 via Microsoft Store, macOS e Linux), mas o usuário não pode ou não quer instalar `pip`, `uv`, ou qualquer package manager.

**Como funciona:**

O Aurea é distribuído como um **Python zipapp** (`.pyz`) — um único arquivo executável que contém todo o código e dependências vendored:

```bash
curl -Lo aurea.pyz https://github.com/<org>/aurea/releases/latest/download/aurea.pyz
python aurea.pyz init minha-apresentacao --agent claude
python aurea.pyz build
python aurea.pyz serve
python aurea.pyz theme search "dark minimal"
python aurea.pyz extract https://cal.com --name cal
```

**No Windows (sem curl):**

```powershell
Invoke-WebRequest -Uri "https://github.com/<org>/aurea/releases/latest/download/aurea.pyz" -OutFile aurea.pyz
python aurea.pyz init minha-apresentacao --agent claude
```

**Vantagens sobre o Modo 1:** Build local real, gestão de temas completa, live preview, extração de temas com pipeline completo. Um único arquivo, sem instalação.

**Limitações:** Requer Python 3.8+ no PATH. Arquivo maior (~2-5MB). Sem autocompletion.

### 2.3 Modo 3 — Executável standalone (PyInstaller)

**Quando usar:** Windows corporativo sem Python; distribuição via share de rede, SCCM, Intune, Artifactory.

```
aurea-windows-amd64.exe    (~20-25MB)
aurea-linux-amd64           (~18-22MB)
aurea-macos-arm64           (~18-22MB)
```

```powershell
.\aurea.exe init minha-apresentacao --agent claude
.\aurea.exe build
.\aurea.exe serve
```

**Vantagens:** Zero dependências. Distribuição corporativa trivial.

**Mitigação para antivírus:** Code signing EV; distribuir como MSI/MSIX; checksums SHA256 no release.

### 2.4 Modo 4 — Instalação via package manager (pip/uv/pipx)

```bash
uv tool install aurea-cli
uvx aurea init minha-apresentacao --agent claude

# ou
pipx install aurea-cli
pip install aurea-cli
```

**Mitigação para air-gap:**

```bash
pip download aurea-cli -d ./aurea-wheels/
pip install --no-index --find-links=./aurea-wheels/ aurea-cli
```

### 2.5 Matriz de decisão de modo

| Cenário | Modo recomendado |
|---------|------------------|
| Máquina totalmente bloqueada, sem Python, sem admin | Modo 1 (zero-install) |
| Windows corporativo com Python mas sem pip/uv | Modo 2 (zipapp) |
| Windows corporativo sem Python, distribuição via IT | Modo 3 (PyInstaller .exe) |
| Desenvolvedor com ambiente completo | Modo 4 (pip/uv/pipx) |
| CI/CD pipeline | Modo 4 (pip/uv) |
| Experimentação rápida / avaliação | Modo 1 ou Modo 2 |

---

## 3. Arquitetura técnica

### 3.1 Stack tecnológico

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| CLI | Python 3.8+ / Typer | Portabilidade, parsing robusto, ecossistema maduro |
| Templates | Jinja2 | Leve, sem dependências nativas, sintaxe familiar |
| Prompt templates | Markdown / TOML puro | Agnóstico a agente, editável por humanos |
| Apresentação engine | reveal.js 5.x | Standard da indústria, offline-capable, extensível |
| Temas | DESIGN.md + CSS custom properties | Fonte de verdade legível por AI + CSS executável |
| Extração de design | httpx + beautifulsoup4 + cssutils | Parsing robusto de HTML/CSS para webscraping |
| Distribuição | PyInstaller + zipapp + pip | Cobertura máxima de ambientes |
| CI/CD | GitHub Actions | Build multiplataforma, release automático |

### 3.2 Estrutura do projeto (repositório)

```
aurea/
├── src/
│   └── aurea/
│       ├── __init__.py
│       ├── cli.py              # Typer app — init, build, serve, theme, extract
│       ├── init.py             # Lógica de scaffolding
│       ├── build.py            # Markdown → HTML (Jinja2 + reveal.js)
│       ├── serve.py            # Live preview server
│       ├── themes.py           # Gestão de temas (list, search, use, info)
│       ├── extract.py          # Webscraping → DESIGN.md + CSS
│       └── agents.py           # Registry de agentes + formatos de comando
├── templates/
│   ├── commands/               # Prompt templates genéricos
│   │   ├── outline.md
│   │   ├── generate.md
│   │   ├── refine.md
│   │   ├── visual.md
│   │   ├── theme.md
│   │   ├── extract.md
│   │   └── build.md
│   ├── themes/
│   │   ├── registry.json       # Índice de todos os temas
│   │   ├── default/            # Tema original Aurea
│   │   ├── midnight/           # Tema original Aurea
│   │   ├── aurora/             # Tema original Aurea
│   │   ├── editorial/          # Tema original Aurea
│   │   ├── brutalist/          # Tema original Aurea
│   │   ├── apple/              # Importado de awesome-design-md
│   │   ├── stripe/
│   │   ├── linear/
│   │   ├── claude/
│   │   ├── vercel/
│   │   ├── cursor/
│   │   ├── notion/
│   │   ├── figma/
│   │   ├── ferrari/
│   │   ├── spacex/
│   │   └── ... (40+ temas)
│   ├── reveal/                 # Vendored — embutido no output
│   │   ├── reveal.min.js
│   │   ├── reveal.min.css
│   │   └── plugins/
│   └── base.html.j2
├── tests/
├── scripts/
│   ├── build-pyinstaller.sh
│   ├── build-zipapp.sh
│   ├── import-awesome-designs.py  # Importa de VoltAgent/awesome-design-md
│   └── release.sh
├── .github/workflows/
│   ├── ci.yml
│   ├── release.yml
│   └── sync-designs.yml          # Sync periódico com awesome-design-md
├── pyproject.toml
├── LICENSE
├── README.md
└── CHANGELOG.md
```

### 3.3 Estrutura gerada pelo `aurea init`

```
minha-apresentacao/
├── .aurea/
│   ├── config.json             # Agente, tema ativo, preferências
│   ├── themes/
│   │   ├── registry.json       # Índice local dos temas
│   │   └── stripe/             # Tema ativo (exemplo)
│   │       ├── DESIGN.md
│   │       ├── theme.css
│   │       ├── layout.css
│   │       └── meta.json
│   └── scripts/
│       └── build-fallback.sh
├── .claude/commands/           # (ou .gemini/ ou .windsurf/ etc.)
│   ├── aurea.outline.md
│   ├── aurea.generate.md
│   ├── aurea.refine.md
│   ├── aurea.visual.md
│   ├── aurea.theme.md
│   ├── aurea.extract.md
│   └── aurea.build.md
├── slides/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── README.md
```

### 3.4 Registry de agentes (AGENT_CONFIG)

```python
AGENT_CONFIG = {
    "claude":  { "commands_dir": ".claude/commands",              "format": "md",       "arg_placeholder": "$ARGUMENTS"  },
    "gemini":  { "commands_dir": ".gemini/commands",              "format": "toml",     "arg_placeholder": "{{args}}"    },
    "copilot": { "commands_dir": ".github/copilot-instructions",  "format": "agent.md", "arg_placeholder": "$ARGUMENTS"  },
    "windsurf":{ "commands_dir": ".windsurf/commands",            "format": "md",       "arg_placeholder": "$ARGUMENTS"  },
    "devin":   { "commands_dir": ".devin/commands",               "format": "md",       "arg_placeholder": "$ARGUMENTS"  },
    "chatgpt": { "commands_dir": ".chatgpt/commands",             "format": "md",       "arg_placeholder": "$ARGUMENTS"  },
    "cursor":  { "commands_dir": ".cursor/commands",              "format": "md",       "arg_placeholder": "$ARGUMENTS"  },
    "generic": { "commands_dir": None,                            "format": "md",       "arg_placeholder": "$ARGUMENTS"  },
}
```

---

## 4. Sistema de temas

### 4.1 O que é um tema

Um tema é a **identidade visual** da apresentação. Ele é composto por um `DESIGN.md` (fonte de verdade para o agente AI) e arquivos CSS derivados (para o build pipeline). Essa unificação elimina a distinção entre "documento de design" e "implementação CSS" — são faces do mesmo artefato.

### 4.2 Anatomia de um tema

```
themes/<nome>/
├── DESIGN.md           # Fonte de verdade — design system completo (lido pelo agente AI)
├── theme.css           # CSS derivado do DESIGN.md (usado pelo build pipeline)
├── layout.css          # Grid de slides, animações, transições reveal.js
└── meta.json           # Metadados resumidos para registry e CLI
```

O **DESIGN.md** segue o formato padronizado pelo [Google Stitch](https://stitch.withgoogle.com/docs/design-md/overview/) com 9 seções:

| # | Seção | O que captura |
|---|-------|--------------|
| 1 | Visual theme & atmosphere | Mood, densidade, filosofia de design |
| 2 | Color palette & roles | Nome semântico + hex + papel funcional |
| 3 | Typography rules | Famílias de fonte, hierarquia completa |
| 4 | Component stylings | Botões, cards, inputs, navegação com estados |
| 5 | Layout principles | Escala de espaçamento, grid, whitespace |
| 6 | Depth & elevation | Sistema de sombras, hierarquia de superfícies |
| 7 | Do's and don'ts | Guardrails e anti-patterns de design |
| 8 | Responsive behavior | Breakpoints, touch targets, estratégia de colapso |
| 9 | Agent prompt guide | Referência rápida de cores, prompts prontos para uso |

### 4.3 Formato do `meta.json`

```json
{
  "id": "stripe",
  "name": "Stripe",
  "description": "Signature purple gradients, weight-300 elegance, fintech precision",
  "version": "1.0.0",
  "author": "Aurea Core",
  "source": "awesome-design-md",
  "source_url": "https://stripe.com",
  "category": "infrastructure",
  "tags": ["purple", "gradient", "elegant", "fintech", "developer"],
  "mood": "Signature purple gradients, weight-300 elegance",
  "colors": {
    "primary": "#635BFF",
    "secondary": "#00D4AA",
    "background": "#FFFFFF",
    "surface": "#F6F9FC",
    "text": "#425466",
    "accent": "#635BFF"
  },
  "typography": {
    "heading": "Camphor",
    "body": "Camphor",
    "code": "Menlo"
  },
  "transition": "slide",
  "backgroundTransition": "fade"
}
```

### 4.4 Temas incluídos (v1)

**Temas originais Aurea (5):**

| Tema | Mood | Background | Tipografia |
|------|------|------------|------------|
| `default` | Clean, versátil | Branco/cinza claro | System sans + mono |
| `midnight` | Profissional, elegante | Escuro (#0f0f1a) | Playfair Display + Source Sans |
| `aurora` | Suave, moderno | Gradientes pastéis | DM Sans + DM Serif Display |
| `editorial` | Magazine, bold | Branco com acentos fortes | Libre Baskerville + Inter |
| `brutalist` | Raw, impactante | Preto/branco puro | Space Mono + Archivo Black |

**Temas importados do [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (31+):**

| Categoria | Temas |
|-----------|-------|
| AI & Machine Learning | claude, cohere, minimax, mistral, ollama, opencode, replicate, runwayml, together, voltagent, xai |
| Developer Tools | cursor, expo, linear, lovable, mintlify, sentry, supabase, vercel, zapier |
| Infrastructure & Cloud | clickhouse, composio, hashicorp, sanity, stripe |
| Design & Productivity | figma, notion |
| Enterprise & Consumer | apple, ibm, nvidia, uber |
| Automotive | bmw, ferrari, lamborghini, renault, tesla |
| Finance | coinbase, kraken, revolut, wise |
| Social & Media | airbnb, airtable, cal, clay, elevenlabs, framer, intercom, miro, pinterest, spotify, spacex, webflow |

### 4.5 Registry (`registry.json`)

Índice JSON de todos os temas para busca rápida:

```json
{
  "version": "1.0.0",
  "sources": {
    "awesome-design-md": { "repo": "VoltAgent/awesome-design-md", "last_sync": "2026-04-08" }
  },
  "themes": [
    {
      "id": "stripe",
      "name": "Stripe",
      "category": "infrastructure",
      "tags": ["purple", "gradient", "elegant", "fintech"],
      "mood": "Signature purple gradients, weight-300 elegance",
      "colors": { "primary": "#635BFF", "accent": "#00D4AA", "background": "#FFFFFF" },
      "path": "themes/stripe/"
    }
  ]
}
```

### 4.6 Pipeline de importação do awesome-design-md

O script `scripts/import-awesome-designs.py` automatiza a importação:

1. Clona/atualiza o repo `VoltAgent/awesome-design-md`
2. Para cada diretório em `design-md/`:
   - Copia o `DESIGN.md`
   - Extrai metadados (cores, tipografia, mood) do conteúdo
   - Gera `meta.json` a partir dos metadados extraídos
   - Gera `theme.css` traduzindo os tokens para CSS custom properties de reveal.js
   - Gera `layout.css` com defaults sensíveis
3. Atualiza `registry.json` com todos os temas
4. GitHub Actions `sync-designs.yml` roda periodicamente para capturar novos designs

---

## 5. Extração de temas via webscraping

### 5.1 Conceito

Além dos temas pré-validados, o Aurea permite **extrair o design system de qualquer URL pública** e salvá-lo como tema reutilizável completo (DESIGN.md + CSS). O usuário diz "quero o visual do site X" e o Aurea cria tudo.

### 5.2 Pipeline de extração

```
URL
 │
 ▼
Fetch HTML + CSS (httpx)
 │
 ▼
Parse e extração de tokens brutos:
├── Cores: declarações color/background/border, agrupadas por frequência
├── Tipografia: font-family, font-size, font-weight, line-height por seletor
├── Espaçamento: margin, padding, gap → escala
├── Sombras: box-shadow → hierarquia de elevação
├── Border radius: padrões de arredondamento
└── Breakpoints: @media queries
 │
 ▼
Geração de DESIGN.md rascunho (tokens brutos organizados)
 │
 ▼
Refinamento AI (via agente no /aurea.extract):
├── Agrupa cores em papéis semânticos
├── Identifica hierarquia tipográfica
├── Descreve mood e atmosfera
├── Gera do's and don'ts
└── Cria agent prompt guide
 │
 ▼
Geração de theme.css + layout.css + meta.json
 │
 ▼
Salva em .aurea/themes/<nome>/ + atualiza registry.json local
```

### 5.3 Comando CLI: `aurea extract`

```bash
aurea extract https://linear.app --name linear-custom
aurea extract https://stripe.com --name stripe-custom --depth 2
aurea extract https://vercel.com --name vercel-raw --raw
aurea extract https://notion.so --name notion-custom --use
```

| Opção | Tipo | Descrição |
|-------|------|-----------|
| `<url>` | Argumento | URL pública para extrair |
| `--name` | Opção | Nome do tema (ID e diretório) |
| `--depth` | Opção | Profundidade de crawl (default: 1) |
| `--raw` | Flag | Tokens brutos sem refinamento AI |
| `--use` | Flag | Aplica o tema extraído imediatamente |
| `--timeout` | Opção | Timeout em segundos (default: 30) |
| `--user-agent` | Opção | User-agent customizado (default: `Aurea/1.0`) |

### 5.4 Módulo de extração

```python
# src/aurea/extract.py

class DesignExtractor:
    """Extrai tokens de design de uma URL pública e gera tema completo."""

    def __init__(self, url: str, depth: int = 1, timeout: int = 30): ...
    def fetch_page(self) -> str: ...
    def extract_stylesheets(self, html: str) -> list[str]: ...
    def extract_color_tokens(self, css: str) -> dict: ...
    def extract_typography_tokens(self, css: str) -> dict: ...
    def extract_spacing_tokens(self, css: str) -> dict: ...
    def extract_shadow_tokens(self, css: str) -> dict: ...
    def generate_raw_design_md(self) -> str: ...
    def generate_theme_css(self, design_md: str) -> str: ...
    def run(self) -> Path: ...
```

### 5.5 Limitações e mitigações

| Limitação | Mitigação |
|-----------|-----------|
| CSS-in-JS (Tailwind, Styled Components) — tokens no runtime | Agente AI complementa via inspeção visual |
| Rate limiting / bloqueio de bots | Respeitar robots.txt; timeout generoso |
| CSS de terceiros (CDNs) polui tokens | Filtrar CDNs conhecidos |
| Direitos autorais | Captura apenas tokens CSS públicos — disclaimer no output |

---

## 6. Workflow de criação de apresentações

### 6.1 Visão geral do fluxo

```
/aurea.theme    →  /aurea.outline  →  /aurea.generate  →  /aurea.refine  →  /aurea.visual  →  /aurea.build
  (identidade)      (narrativa)        (slides .md)        (iteração)        (assets SVG)      (HTML final)

/aurea.extract  →  (gera tema novo a partir de URL)  →  alimenta o fluxo acima
```

Cada comando é independente. O `/aurea.theme` e `/aurea.extract` são opcionais e podem ser usados a qualquer momento.

### 6.2 Comando: `/aurea.theme`

**Propósito:** Buscar, explorar e aplicar um tema da biblioteca.

**Input:** Nome, descrição ou mood desejado (ex: "algo minimalista e escuro", "estilo fintech premium", "stripe").

**Fluxo:**

1. Agente lê `registry.json`
2. Faz match por semelhança semântica (tags, mood, categoria)
3. Apresenta 3-5 candidatos com nome, mood, cores, tipografia
4. Usuário escolhe
5. Copia tema para `.aurea/themes/` e atualiza `config.json`
6. Nos próximos comandos, o agente lê o `DESIGN.md` do tema ativo

### 6.3 Comando: `/aurea.extract`

**Propósito:** Extrair design de qualquer URL e salvar como tema reutilizável.

**Fluxo:**

1. Executa `aurea extract <url> --name <nome>` (se CLI disponível) OU faz web fetch nativo (Modo 1)
2. Recebe tokens brutos
3. Refina em DESIGN.md completo (9 seções)
4. Gera theme.css derivado
5. Salva em `.aurea/themes/<nome>/`
6. Pergunta se quer aplicar

### 6.4 Comando: `/aurea.outline`

**Propósito:** Definir narrativa, público, tom e estrutura.

**Output:** `slides/outline.md` com público-alvo, objetivo, tom, arco narrativo, lista de slides planejados, tempo estimado, constraints visuais (referência ao DESIGN.md ativo).

**Comportamento:** Lê `config.json` → carrega `DESIGN.md` do tema → clarifica se vago → gera outline → apresenta para aprovação.

### 6.5 Comando: `/aurea.generate`

**Propósito:** Gerar slides em Markdown a partir do outline.

**Output:** `slides/presentation.md` usando sintaxe reveal.js (separador `---`, speaker notes com `Note:`, atributos de slide com `<!-- .slide: -->`).

**Comportamento:** Lê outline + DESIGN.md → gera slides respeitando arco narrativo → usa cores/tipografia do tema → marca slides que precisam de visuais com `<!-- VISUAL: descrição -->`.

### 6.6 Comando: `/aurea.refine`

**Propósito:** Iterar sobre slides específicos ou toda a apresentação.

**Comportamento:** Lê apresentação atual → aplica mudanças → valida contra outline e DESIGN.md → reporta diff.

### 6.7 Comando: `/aurea.visual`

**Propósito:** Gerar assets visuais (SVG, mermaid, CSS backgrounds).

**Comportamento:** Identifica slides marcados → lê DESIGN.md para paleta e do's/don'ts → gera assets → atualiza `presentation.md`.

### 6.8 Comando: `/aurea.build`

**Modo CLI:** Executa `aurea build` → Jinja2 + inline CSS/JS → `output/presentation.html`.

**Modo fallback:** Agente gera HTML completo inline.

---

## 7. Especificação da CLI

### 7.1 Comandos

| Comando | Descrição |
|---------|-----------|
| `aurea init <nome>` | Cria novo projeto de apresentação |
| `aurea build` | Compila slides para HTML standalone |
| `aurea serve` | Live preview com hot reload |
| `aurea theme list` | Lista temas disponíveis |
| `aurea theme search <query>` | Busca temas por nome, tag, categoria, mood |
| `aurea theme info <id>` | Mostra detalhes de um tema |
| `aurea theme use <id>` | Aplica tema ao projeto |
| `aurea theme show <id>` | Imprime o DESIGN.md no terminal |
| `aurea theme create <nome>` | Scaffolding de tema customizado |
| `aurea extract <url>` | Extrai tema de uma URL pública |
| `aurea check` | Verifica dependências e agente |
| `aurea export pdf` | Exporta para PDF (requer Chrome/Chromium) |

### 7.2 Opções do `aurea init`

| Opção | Tipo | Descrição |
|-------|------|-----------|
| `<project-name>` | Argumento | Nome do diretório (ou `.`) |
| `--agent` | Opção | `claude`, `gemini`, `copilot`, `windsurf`, `devin`, `chatgpt`, `cursor`, `generic` |
| `--theme` | Opção | Tema inicial (default: `default`) |
| `--here` | Flag | Inicializa no diretório atual |
| `--force` | Flag | Sobrescreve se já existir |
| `--no-git` | Flag | Não inicializa repo git |
| `--commands-dir` | Opção | Diretório customizado (requer `--agent generic`) |
| `--lang` | Opção | Idioma dos prompts: `pt-br`, `en` (default: `en`) |

### 7.3 Opções do `aurea build`

| Opção | Tipo | Descrição |
|-------|------|-----------|
| `--input` | Opção | Arquivo .md (default: `slides/presentation.md`) |
| `--output` | Opção | Arquivo .html (default: `output/presentation.html`) |
| `--theme` | Opção | Override de tema |
| `--minify` | Flag | Minifica HTML/CSS/JS |
| `--watch` | Flag | Rebuild automático ao salvar |
| `--embed-fonts` | Flag | Base64-encode fonts no HTML |

### 7.4 Opções do `aurea theme search`

| Opção | Tipo | Descrição |
|-------|------|-----------|
| `<query>` | Argumento | Busca fulltext em nome, tags, mood, categoria |
| `--category` | Opção | Filtra por categoria |
| `--tag` | Opção | Filtra por tag |
| `--format` | Opção | `table` ou `json` (default: `table`) |

---

## 8. Prompt templates — design detalhado

### 8.1 Formato

YAML frontmatter + corpo Markdown (padrão spec-kit). Convertido para formato nativo de cada agente durante `aurea init`.

### 8.2 Princípios dos prompts

1. **Carregar contexto primeiro** — ler `config.json` e `DESIGN.md` do tema ativo antes de gerar conteúdo
2. **Respeitar o design system** — cores, tipografia e mood do DESIGN.md são constraints
3. **Arco narrativo obrigatório** — abertura → desenvolvimento → clímax → conclusão
4. **Slides enxutos** — máximo 40 palavras por slide (excluindo speaker notes)
5. **Speaker notes de primeira classe** — todo slide deve ter notes
6. **Visual-first** — preferir diagramas a paredes de texto
7. **Do's and don'ts do tema** — respeitar seção 7 do DESIGN.md

### 8.3 Variáveis de template

| Placeholder | Substituição |
|-------------|-------------|
| `{{DESIGN_MD_PATH}}` | DESIGN.md do tema ativo |
| `{{THEME_CSS_PATH}}` | theme.css |
| `{{CONFIG_PATH}}` | `.aurea/config.json` |
| `{{REGISTRY_PATH}}` | `registry.json` |
| `{{SLIDES_DIR}}` | `slides/` |
| `{{OUTPUT_DIR}}` | `output/` |
| `$ARGUMENTS` | Input do usuário |

---

## 9. Build pipeline

```
slides/presentation.md
 → Parse frontmatter (título, tema, autor)
 → Resolve tema: .aurea/themes/<tema>/theme.css + layout.css
 → Split por `---` em slides
 → Para cada slide: Markdown → HTML, mermaid → SVG, resolve assets
 → Jinja2 (base.html.j2): inline reveal.js + CSS + fonts + assets
 → output/presentation.html (arquivo único, ~200-500KB)
```

---

## 10. Plano de implementação (milestones)

### Milestone 0 — Projeto e infra (1 semana)

- [ ] Repositório + `pyproject.toml`
- [ ] CI (GitHub Actions): lint, testes, build multiplataforma
- [ ] Typer CLI com comandos placeholder
- [ ] PyInstaller + zipapp no CI
- [ ] README com 4 modos de funcionamento
- [ ] Licença MIT

### Milestone 1 — Prompt commands (2 semanas)

- [ ] 7 prompt templates (theme, extract, outline, generate, refine, visual, build)
- [ ] Conversão para formato de cada agente (AGENT_CONFIG)
- [ ] Teste com Claude Code e Gemini CLI
- [ ] `slide-template.md` com sintaxe documentada
- [ ] `aurea init` completo
- [ ] Testes

### Milestone 2 — Temas: importação e gestão (2 semanas)

- [ ] Script `import-awesome-designs.py` (VoltAgent/awesome-design-md → temas Aurea)
- [ ] Gerar DESIGN.md + theme.css + layout.css + meta.json por design
- [ ] 5 temas originais (default, midnight, aurora, editorial, brutalist)
- [ ] `registry.json` com metadados
- [ ] `aurea theme list/search/info/use/show/create`
- [ ] GitHub Actions `sync-designs.yml`
- [ ] Testes

### Milestone 3 — Build pipeline (2 semanas)

- [ ] Parser Markdown → slides
- [ ] Jinja2 com inlining CSS/JS
- [ ] Vendor reveal.js 5.x
- [ ] `aurea build` end-to-end
- [ ] `aurea serve` com hot reload
- [ ] Testes end-to-end

### Milestone 4 — Extração de temas via webscraping (1 semana)

- [ ] `DesignExtractor` (fetch, parse CSS, tokens)
- [ ] Geração de DESIGN.md rascunho
- [ ] Geração de theme.css a partir de DESIGN.md
- [ ] `aurea extract` CLI
- [ ] Filtro de CSS de CDNs
- [ ] Testes com 5+ URLs reais

### Milestone 5 — Distribuição e polish (1 semana)

- [ ] PyInstaller Windows/Mac/Linux
- [ ] Zipapp
- [ ] PyPI
- [ ] Code signing Windows
- [ ] Documentação completa
- [ ] Air-gap (wheel bundles)
- [ ] Release v1.0.0

### Milestone 6 — Pós-v1

- [ ] i18n (pt-br, en, es)
- [ ] Export PDF
- [ ] Modo apresentador remoto
- [ ] Marketplace de temas
- [ ] Mermaid rendering no build
- [ ] CI/CD para build automático
- [ ] Sync bidirecional com awesome-design-md

---

## 11. Dependências

### 11.1 Runtime

```toml
[project]
name = "aurea-cli"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "typer>=0.9.0",
    "jinja2>=3.1.0",
    "mistune>=3.0.0",
    "rich>=13.0.0",
    "watchdog>=3.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
extract = [
    "httpx>=0.27.0",
    "beautifulsoup4>=4.12.0",
    "cssutils>=2.9.0",
    "lxml>=5.0.0",
]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "ruff",
    "mypy",
    "pyinstaller>=6.0",
]

[project.scripts]
aurea = "aurea.cli:main"
```

### 11.2 Vendored (embutidas no output HTML)

- reveal.js 5.x (~120KB)
- highlight.js (~40KB)
- Fonts por tema (Google Fonts via `@import` ou base64)

### 11.3 Opcionais de sistema

| Ferramenta | Para | Fallback |
|-----------|------|----------|
| Chrome/Chromium | Export PDF | Não disponível |
| mermaid-cli | Pre-render mermaid | Renderer JS inline |
| git | Versionamento | `--no-git` |

---

## 12. Riscos e mitigações

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Antivírus bloqueia .exe | Alta | Alto | Code signing; MSI/MSIX; Modos 1-2 como fallback |
| Python ausente em Windows | Média | Alto | Modo 3 (PyInstaller); Modo 1 como fallback absoluto |
| reveal.js quebra temas | Baixa | Médio | Versão pinada; testes de regressão |
| Prompts ruins em agentes específicos | Média | Médio | Testar cada agente; registry de quirks |
| Webscraping falha em CSS-in-JS | Alta | Médio | Fallback via agente AI; priorizar temas pré-validados |
| awesome-design-md muda ou morre | Baixa | Médio | Snapshot local; não depender exclusivamente |

---

## 13. Critérios de sucesso (v1.0)

- [ ] `aurea init` funciona nos 4 modos em Windows 10/11, macOS e Ubuntu
- [ ] 7 comandos `/aurea.*` com output de qualidade no Claude Code e Gemini CLI
- [ ] HTML gerado abre offline em Chrome, Firefox, Safari e Edge
- [ ] 36+ temas (5 originais + 31+ importados)
- [ ] `aurea theme search "dark minimal"` retorna resultados relevantes em < 1s
- [ ] `aurea extract <url>` gera tema funcional para 80%+ das URLs testadas
- [ ] Build < 2s para 30 slides
- [ ] Quickstart em < 5 minutos
- [ ] Zero dependências externas no HTML de output

---

## Apêndice A — Exemplo de sessão completa

```bash
# 1. Instalar
python aurea.pyz init pitch-investidores --agent claude --theme stripe

# 2. No Claude Code:
/aurea.theme Quero algo premium e tech, talvez estilo Stripe ou Linear

# 3. Ou extrair de um site:
/aurea.extract Extraia o design do https://oute.me para usar como tema

# 4. Definir narrativa:
/aurea.outline Pitch para VCs série A da Oute. 12-15 slides, 10 min.

# 5. Gerar:
/aurea.generate

# 6. Iterar:
/aurea.refine Slide de mercado fraco. Mais dados de mercado.

# 7. Visuais:
/aurea.visual Diagrama de arquitetura no slide 5, gráfico no slide 3.

# 8. Build:
/aurea.build

# 9. Preview:
python aurea.pyz serve --open
```
