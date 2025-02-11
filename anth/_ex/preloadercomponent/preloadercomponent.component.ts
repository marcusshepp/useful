```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-preloader',
  template: `
    <div id="preloader">
      <div class="preload-content">
          <div id="sonar-load"></div>
      </div>
    </div>
  `,
  styles: [`
    #preloader {
      background: #ffffff;
      height: 100%;
      left: 0;
      position: fixed;
      top: 0;
      width: 100%;
      z-index: 99999;
    }

    .preload-content {
      left: 50%;
      position: absolute;
      top: 50%;
      transform: translate(-50%, -50%);
    }

    #sonar-load {
      width: 40px;
      height: 40px;
      background-color: #6c63ff;
      border-radius: 50%;
      display: inline-block;
      -webkit-animation: sonar 2s infinite ease-in-out;
      animation: sonar 2s infinite ease-in-out;
    }

    @-webkit-keyframes sonar {
      0% {
        transform: scale(0.9);
        opacity: 1;
      }
      100% {
        transform: scale(2);
        opacity: 0;
      }
    }

    @keyframes sonar {
      0% {
        transform: scale(0.9);
        opacity: 1;
      }
      100% {
        transform: scale(2);
        opacity: 0;
      }
    }
  `]
})
export class PreloaderComponent implements OnInit {
  constructor() { }

  ngOnInit(): void {
  }
}
```