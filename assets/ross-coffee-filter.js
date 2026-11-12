/* ROSS · kleurfilter voor de koffiecollectie (in de browser, zonder herladen). */
if (!customElements.get('ross-coffee-filter')) {
  customElements.define(
    'ross-coffee-filter',
    class RossCoffeeFilter extends HTMLElement {
      connectedCallback() {
        this.color = 'alle';
        this.chips = Array.from(this.querySelectorAll('.ross-chip'));
        this.checks = Array.from(this.querySelectorAll('input[data-filter]'));
        this.items = Array.from(this.querySelectorAll('[data-ross-item]'));
        this.countEl = this.querySelector('[data-count]');
        this.wordEl = this.querySelector('[data-count-word]');
        this.noneEl = this.querySelector('.ross-coll__none');

        this.chips.forEach((chip) =>
          chip.addEventListener('click', () => this.setColor(chip.dataset.color, true))
        );
        this.checks.forEach((box) => box.addEventListener('change', () => this.apply()));
        const reset = this.querySelector('.ross-coll__reset');
        if (reset) {
          reset.addEventListener('click', () => {
            this.checks.forEach((box) => (box.checked = false));
            this.setColor('alle', true);
          });
        }

        const fromUrl = new URLSearchParams(window.location.search).get('kleur');
        if (fromUrl && this.chips.some((chip) => chip.dataset.color === fromUrl)) {
          this.setColor(fromUrl, false);
        } else {
          this.apply();
        }
      }

      setColor(color, updateUrl) {
        this.color = color;
        this.chips.forEach((chip) => chip.setAttribute('aria-pressed', String(chip.dataset.color === color)));
        if (updateUrl) {
          const url = new URL(window.location.href);
          if (color === 'alle') url.searchParams.delete('kleur');
          else url.searchParams.set('kleur', color);
          window.history.replaceState({}, '', url);
        }
        this.apply();
      }

      apply() {
        const wanted = this.checks.filter((box) => box.checked).map((box) => box.dataset.filter);
        let shown = 0;
        this.items.forEach((item) => {
          const card = item.querySelector('.ross-coffee-card');
          let visible = true;
          if (this.color !== 'alle' || wanted.length) {
            if (!card) {
              visible = false;
            } else {
              if (this.color !== 'alle' && card.dataset.rossColor !== this.color) visible = false;
              wanted.forEach((key) => {
                if (card.dataset[key] !== 'true') visible = false;
              });
            }
          }
          item.hidden = !visible;
          if (visible) shown += 1;
        });
        if (this.countEl) this.countEl.textContent = String(shown);
        const filtering = this.color !== 'alle' || wanted.length > 0;
        if (this.wordEl) {
          if (filtering) this.wordEl.textContent = shown === 1 ? 'koffie' : 'koffies';
          else this.wordEl.textContent = shown === 1 ? 'product' : 'producten';
        }
        if (this.noneEl) this.noneEl.hidden = shown > 0;
      }
    }
  );
}
