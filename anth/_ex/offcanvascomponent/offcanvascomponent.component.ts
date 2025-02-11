```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-offcanvas',
  templateUrl: './offcanvas.component.html',
  styleUrls: ['./offcanvas.component.css']
})
export class OffcanvasComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

  items = [
    {
      title: 'About',
      link: '/about'
    },
    {
      title: 'Services', 
      link: '/services'
    },
    {
      title: 'Portfolio',
      link: '/portfolio'
    },
    {
      title: 'Contact',
      link: '/contact'
    }
  ];

  toggle = false;

  toggleOffcanvas() {
    this.toggle = !this.toggle;
  }

}
```