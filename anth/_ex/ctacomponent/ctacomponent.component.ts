```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-cta',
  template: `
    <section class="py-6">
      <div class="container">
        <div class="row">
          <div class="col-md-8 mx-auto text-center">
            <h4 class="text-muted">Ready to get started?</h4>
            <h2 class="display-4 mt-2">Get Started Today</h2>
            <p class="lead">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at ipsum eu nunc commodo posuere et sit amet ligula.</p>
            <a href="#" class="btn btn-primary mt-3">Get Started!</a>
          </div>
        </div>
      </div>
    </section>
  `,
  styles: []
})
export class CtaComponent {

}
```