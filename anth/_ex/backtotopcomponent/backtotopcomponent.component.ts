```typescript
import { Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-backtotop',
  template: `
    <div class="back-to-top" [ngClass]="{'show-scrollTop': windowScrolled}" (click)="scrollToTop()">
      <i class="bi bi-arrow-up"></i>
    </div>
  `,
  styles: [`
    .back-to-top {
      position: fixed;
      bottom: 15px;
      right: 15px;
      opacity: 0;
      transition: all .2s ease-in-out;
      z-index: 1000;
      background: #0d6efd;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      color: #fff;
      cursor: pointer;
    }
    
    .show-scrollTop {
      opacity: 1;
      transition: all .2s ease-in-out;
    }
  `]
})
export class BacktotopComponent {
  windowScrolled = false;

  @HostListener('window:scroll', [])
  onWindowScroll() {
    if (window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop > 100) {
      this.windowScrolled = true;
    } else if (this.windowScrolled && window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop < 10) {
      this.windowScrolled = false;
    }
  }

  scrollToTop() {
    window.scrollTo(0, 0);
  }
}
```