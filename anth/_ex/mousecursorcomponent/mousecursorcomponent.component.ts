```typescript
import { Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-mousecursor',
  template: `
    <div class="cursor"
         [ngStyle]="{
           'transform': 'translate3d(' + x + 'px, ' + y + 'px, 0)',
           'opacity': isVisible ? '1' : '0'
         }">
    </div>
  `,
  styles: [`
    .cursor {
      width: 20px;
      height: 20px;
      border: 2px solid #000;
      border-radius: 50%;
      position: fixed;
      pointer-events: none;
      transition: all 0.2s ease;
      transition-property: transform, opacity;
      z-index: 9999;
    }
  `]
})
export class MousecursorComponent {
  x: number = 0;
  y: number = 0;
  isVisible: boolean = false;

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(e: MouseEvent) {
    this.x = e.clientX;
    this.y = e.clientY;
    this.isVisible = true;
  }

  @HostListener('document:mouseleave')
  onMouseLeave() {
    this.isVisible = false;
  }

  @HostListener('document:mouseenter')
  onMouseEnter() {
    this.isVisible = true;
  }
}
```