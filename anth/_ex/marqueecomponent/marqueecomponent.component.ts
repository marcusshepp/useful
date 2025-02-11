```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-marqueecomponent',
  template: `
    <div class="marquee-container">
      <div class="marquee">
        <span>{{marqueeText}}</span>
      </div>
    </div>
  `,
  styles: [`
    .marquee-container {
      width: 100%;
      overflow: hidden;
      white-space: nowrap;
    }
    
    .marquee {
      display: inline-block;
      animation: marquee 20s linear infinite;
    }
    
    @keyframes marquee {
      0% { transform: translateX(100%); }
      100% { transform: translateX(-100%); }
    }
  `]
})
export class MarqueeComponentComponent implements OnInit {
  marqueeText: string = 'This is a scrolling marquee text...';

  constructor() { }

  ngOnInit(): void {
  }
}
```