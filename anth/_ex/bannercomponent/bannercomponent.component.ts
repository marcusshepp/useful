```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-banner',
  template: `
    <div class="bg-gray-800 text-white py-4">
      <div class="container mx-auto px-4">
        <p class="text-center">This is a banner message</p>
      </div>
    </div>
  `,
  styles: []
})
export class BannerComponent {
  constructor() { }
}
```