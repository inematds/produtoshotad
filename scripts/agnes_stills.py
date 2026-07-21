"""Worker 1 (ad-pipeline-agnes) — gera as 5 stills a partir de 1 foto real de produto,
usando o cliente Agnes AI já existente em ~/projetos/imagens-agnes/gerar.py (US$ 0).

Uso:
  python3 scripts/agnes_stills.py products/hero.png products/closeup.png \
      --desc "digital alarm clock, black plastic body, red LED display"

Gera 5 stills em output/stills/:
  still-1-plain.png, still-2-plain.png, still-3-plain.png   (Fully Automated)
  still-4-overlay.png, still-5-overlay.png                   (AI-Assisted, base p/ HTML/CSS)

Regras aplicadas (product-consistency.md + regras Agnes medidas):
  - hero + no máx. 1 close-up reanexados em toda chamada (teto Agnes = 2 refs)
  - prompt em inglês, curto, 1 variável por geração, unchanged-clause explícita
  - QA checkpoint = gate humano (imprime as 5 imagens geradas, pede confirmação)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.expanduser('~/projetos/imagens-agnes'))
import gerar  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output', 'stills')

UNCHANGED = ('keep the product shape, proportions, color and label exactly '
             'as in the reference photos, only change ')

VARIATIONS = [
    ('still-1-plain', 'the background to a clean studio white backdrop with soft shadow'),
    ('still-2-plain', 'the setting to a minimalist lifestyle surface (wood tabletop, natural light)'),
    ('still-3-plain', 'the angle to a 3/4 hero shot with subtle rim lighting'),
    ('still-4-overlay', 'the background to a plain neutral gradient, leaving empty space for text overlay'),
    ('still-5-overlay', 'the composition to an off-center product placement, leaving empty space for text overlay'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('hero', help='foto real do produto (hero, fundo neutro)')
    ap.add_argument('closeup', nargs='?', help='1 crop de detalhe distintivo (opcional)')
    ap.add_argument('--desc', required=True, help='descrição curta do produto, em inglês')
    ap.add_argument('--ratio', default='4:3')
    a = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    refs = [a.hero] + ([a.closeup] if a.closeup else [])

    print(f'Referências travadas: {refs} (máx. 2 por chamada Agnes)')
    results = []
    for name, change in VARIATIONS:
        prompt = f'{a.desc}. {UNCHANGED}{change}.'
        dest = os.path.join(OUT_DIR, f'{name}.png')
        print(f'\n--- {name} ---\nprompt: {prompt}')
        url = gerar.gerar(prompt, dest, ratio=a.ratio, size='1K', refs=refs)
        results.append((name, dest, url is not None))

    print('\n=== QA checkpoint (gate humano) ===')
    ok = all(success for _, _, success in results)
    for name, dest, success in results:
        print(f'  {"✅" if success else "❌"} {name} -> {dest}')
    if not ok:
        print('⚠️  Uma ou mais gerações falharam — não avance para o worker 2/3 sem revisar.')
        sys.exit(1)
    print('Confira as 5 imagens contra a foto real do produto antes de avançar de estágio.')


if __name__ == '__main__':
    main()
